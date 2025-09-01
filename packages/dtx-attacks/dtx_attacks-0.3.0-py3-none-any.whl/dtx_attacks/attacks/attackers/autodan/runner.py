"""
Single-example AutoDAN
- keeps only one public method: `run(query, target="Sure, here's")`
- no dataset dependency
- optional progress_hook compatible with BaseAttackProgressHook
"""

from __future__ import annotations

import random
from pydantic import BaseModel
from dataclasses import dataclass, field
from typing import List, Optional, Any, Tuple

from loguru import logger
from nltk.corpus import stopwords
from collections import defaultdict
from tqdm import trange
import nltk

from dtx_attacks.base.gates import require_deps, torch
from dtx_attacks.attacks.attackers.base import BaseAttackManager
from dtx_attacks.attacks.templates.seed_template import SeedTemplate

from dtx_attacks.attacks.mutation.crossover import CrossOver
from dtx_attacks.attacks.mutation.rephrase import Rephrase
from dtx_attacks.attacks.mutation.synonyms import Synonyms

from .prefix_prompt_manager import PrefixPromptManager
from dtx_attacks.attacks.selection.selection_utils import RouletteWheelSelection
from dtx_attacks.attacks.datasets.example import Example
from dtx_attacks.evaluation.scorers.pattern import PatternScorer
from dtx_attacks.models.feedback.model_utils import get_developer
from dtx_attacks.models.feedback.func_utils import Timer
from dtx_attacks.attacks.targets.base import WhiteboxTargetModel
from dtx_attacks.attacks.attackers.telemetry.progress_hook import BaseAttackProgressHook
from .targetloss_selection import TargetLossSelection
from dtx_attacks.models.base import Model
from dtx_attacks.attacks.attackers.base.results import AttackRunResult, AttackFlavor

from dtx_attacks.base.logging_utils import _snip 


# -------------------------
# Config & data holders
# -------------------------

class AutoDANRunDetails(BaseModel):
    # config echoes
    mutation_rate: float
    num_candidates: int
    num_steps: int
    ratio_elites: float
    num_points: int
    crossover_rate: float
    sentence_level_steps: int
    word_dict_size: int
    model_display_name: str

    # run bookkeeping
    best_step_index: int                 # 0-based major step where best occurred
    best_sentence_step_index: int        # 0-based minor step (or -1 if N/A)
    total_evaluations: int               # how many times we ran select+generate
    final_loss: float | None             # last observed loss (if available)


@dataclass
class AutoDANConfig:
    # population & search
    mutation_rate: float = 0.01
    num_candidates: int = 64
    num_steps: int = 100
    ratio_elites: float = 0.1
    num_points: int = 5
    crossover_rate: float = 0.5
    sentence_level_steps: int = 5
    word_dict_size: int = 50

    # label replacement in seeds
    model_display_name: str = "llama-2"

    # NEW: injected rephrase backend (same pattern as PAIR)
    rephrase_model: Model = None  # required at runtime


@dataclass
class AttackData:
    init_templates: List[str]
    prompt_manager: Optional[PrefixPromptManager] = None
    word_dict: dict = field(default_factory=dict)

    # running stats
    score_list: Optional[List[float]] = None  # larger is better (we store -loss)
    current_loss: Optional[Any] = None
    best_id: Optional[int] = None
    best_template: Optional[str] = None
    response: Optional[str] = None
    is_success: bool = False
    step: Optional[int] = None
    sentence_step: Optional[int] = None


# -------------------------
# Init
# -------------------------
class AutoDANInit:
    def __init__(self, cfg: AutoDANConfig) -> None:
        init_templates = SeedTemplate().get_templates("AutoDAN", cfg.num_candidates)
        logger.debug("SeedTemplate returned {} templates (pre-inject).", len(init_templates))
        for i in range(len(init_templates)):
            before = init_templates[i]
            init_templates[i] = (
                init_templates[i]
                .replace("ChatGPT", cfg.model_display_name)
                .replace("chatgpt", cfg.model_display_name)
                .replace("ModelKeeper", get_developer(cfg.model_display_name))
            ) + " [PROMPT]:"
            if i < 5:  # log only the first few verbosely
                logger.debug("Seed[{}] injected: '{}' -> '{}'", i, _snip(before), _snip(init_templates[i]))
        self.config = cfg
        self.data = AttackData(init_templates=init_templates)

    def example_init(self, attack_manager: "AutoDANManager", example: Example) -> None:
        pm = PrefixPromptManager(
            tokenizer=attack_manager.target_model.tokenizer,
            conv_template=attack_manager.conv_template,
            instruction=example.query,
            target=example.target,
            adv_string=self.data.init_templates[0],
        )
        example.candidate_templates = list(self.data.init_templates)
        self.data.prompt_manager = pm
        self.data.word_dict = {}
        logger.info("Initialized example. Query='{}' | TargetHint='{}'", _snip(example.query), _snip(example.target))
        logger.debug("Initial candidate[0]: {}", _snip(self.data.init_templates[0]))

    def step_init(self, step: int) -> None:
        logger.debug("===> Step {} start", step)
        self.data.step = step
        self.data.sentence_step = -1

    def sentence_step_init(self, sentence_step: int) -> None:
        logger.debug("  --> Sentence step {}", sentence_step)
        self.data.sentence_step = sentence_step


# -------------------------
# Mutations
# -------------------------
class AutoDANMutator:
    def __init__(self, cfg: AutoDANConfig, rephrase_model):
        self.mutation_rephrase = Rephrase(rephrase_model)
        self.mutation_crossover = CrossOver(num_points=cfg.num_points)
        self.mutation_synonyms = Synonyms(crossover_rate=cfg.crossover_rate)
        self.cfg = cfg

    def rephrase(self, templates: List[str]) -> None:
        timer = Timer.start()
        changes: List[Tuple[int, str, str]] = []
        for i in range(len(templates)):
            if random.random() < self.cfg.mutation_rate:
                before = templates[i]
                templates[i] = self.mutation_rephrase.rephrase(templates[i])
                changes.append((i, before, templates[i]))
        took = timer.end()
        if changes:
            for idx, b, a in changes[:8]:  # cap logging
                logger.debug("Rephrase@{}: '{}' -> '{}'", idx, _snip(b), _snip(a))
            if len(changes) > 8:
                logger.debug("Rephrase: +{} more changes not shown", len(changes) - 8)
        logger.debug("Rephrase mutation finished in {:.2f}s (rate={}%)", took, int(self.cfg.mutation_rate * 100))

    def crossover(self, parents_list: List[str]) -> List[str]:
        mutated = []
        pair_logs = []
        for i in range(0, len(parents_list), 2):
            p1 = parents_list[i]
            p2 = parents_list[i + 1] if (i + 1) < len(parents_list) else parents_list[0]
            if random.random() < self.cfg.crossover_rate:
                c1, c2 = self.mutation_crossover.crossover(p1, p2)
                mutated.extend([c1, c2])
                if len(pair_logs) < 6:
                    pair_logs.append(("XO", _snip(p1), _snip(p2), _snip(c1), _snip(c2)))
            else:
                mutated.extend([p1, p2])
                if len(pair_logs) < 6:
                    pair_logs.append(("SKIP", _snip(p1), _snip(p2), _snip(p1), _snip(p2)))
        for tag, p1s, p2s, c1s, c2s in pair_logs:
            logger.debug("Crossover [{}]: P1='{}' | P2='{}' -> C1='{}' | C2='{}'", tag, p1s, p2s, c1s, c2s)
        logger.debug("Crossover produced {} candidates (rate={}%)", len(mutated), int(self.cfg.crossover_rate * 100))
        return mutated

    def _construct_momentum_word_dict(self, word_dict, control_suffixs, score_list, topk=-1):
        T = {
            "llama2", "llama-2", "meta", "vicuna", "lmsys", "guanaco", "theblokeai",
            "wizardlm", "mpt-chat", "mosaicml", "mpt-instruct", "falcon", "tii",
            "chatgpt", "modelkeeper", "prompt",
        }
        stop_words = set(stopwords.words("english"))
        if len(control_suffixs) != len(score_list):
            raise ValueError("control_suffixs and score_list must have the same length.")
        word_scores = defaultdict(list)
        for prefix, score in zip(control_suffixs, score_list):
            words = set(
                w for w in nltk.word_tokenize(prefix)
                if w.lower() not in stop_words and w.lower() not in T
            )
            for w in words:
                word_scores[w].append(score)
        for w, scores in word_scores.items():
            avg = sum(scores) / len(scores)
            word_dict[w] = (word_dict[w] + avg) / 2 if w in word_dict else avg
        sorted_items = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
        if sorted_items:
            logger.debug("Momentum top words: {}", ", ".join([f"{k}:{v:.2f}" for k, v in sorted_items[:10]]))
        return dict(sorted_items if topk == -1 else sorted_items[:topk])

    def synonyms_replacement(self, candidate_templates: List[str], example: Example, data: AttackData) -> List[str]:
        data.word_dict = self._construct_momentum_word_dict(
            data.word_dict, example.candidate_templates, data.score_list, topk=self.cfg.word_dict_size
        )
        self.mutation_synonyms.update(data.word_dict)
        out = [self.mutation_synonyms.replace_synonyms(t) for t in candidate_templates]
        # log first few replacements
        for i, (b, a) in enumerate(zip(candidate_templates, out)):
            if i >= 6:
                break
            if b != a:
                logger.debug("Synonym replace[{}]: '{}' -> '{}'", i, _snip(b), _snip(a))
        return out


# -------------------------
# Selection & evaluation
# -------------------------
class AutoDANSelector:
    def __init__(self):
        self.sel_loss = TargetLossSelection()
        self.sel_rw = RouletteWheelSelection()

    def select_loss(
        self,
        example: Example,
        attack_manager: "AutoDANManager",
        data: AttackData,
        batch_size: int = 4,
        ):
        """
        Score the current population of candidate templates against the white-box
        target and pick the best candidate for this iteration.

        Pipeline
        --------
        1) Build input ids for each candidate prefix using the PrefixPromptManager.
        This yields loss slicing metadata (pm._loss_slice) that tells the selector
        which region of the sequence to measure (e.g., target/prefix region).
        2) Call the loss-based selector (TargetLossSelection.select) to compute a
        per-candidate loss and identify the best index.
        3) Convert losses to "higher is better" scores by negation (score = -loss).
        Store: scores, current loss tensor (for the best candidate), best index.
        4) Emit structured DEBUG logs:
        - A short preview of a few candidate strings before scoring
        - Top-5 scores for this pass, with candidate indices and snipped text

        Parameters
        ----------
        example : Example
            Holds the attack query/target strings and the mutable population:
            `example.candidate_templates` is the list[str] to be scored.
        attack_manager : AutoDANManager
            Provides access to the white-box `target_model` (model, tokenizer,
            device) and its conversation template used to construct inputs.
        data : AttackData
            Run-state container that this function updates in-place:
            - data.score_list: List[float] (higher is better)
            - data.current_loss: torch.Tensor | float (loss of current best)
            - data.best_id: int (index into candidate_templates)

        Side Effects
        ------------
        Mutates `data.score_list`, `data.current_loss`, `data.best_id`.
        Reads `pm._loss_slice` to align loss computation with the target region.

        Logging (DEBUG)
        ---------------
        - First few candidates (pre-loss, snipped)
        - Top-5 scores with rank, index, score, and snipped candidate text

        Notes
        -----
        - This method runs on the attack_manager.target_model.device.
        - `TargetLossSelection.select` expects raw model, tokenized inputs, loss
        slices, and a pad token id. It returns (loss_list, best_loss, best_idx).
        - Because selection returns *loss* (lower is better), we invert to scores
        (higher is better) for consistency with evolutionary selection utilities.
        """
        dev = attack_manager.target_model.device
        pm = data.prompt_manager
        inputs, loss_slices = [], []

        # preview a few candidates
        for i, t in enumerate(example.candidate_templates[:6]):
            logger.debug("Candidate[{}] pre-loss: '{}'", i, _snip(t))

        # tokenize all candidates for this pass
        for t in example.candidate_templates:
            ids = pm.get_input_ids(adv_string=t).to(dev)
            inputs.append(ids)
            loss_slices.append(pm._loss_slice)

        # selector expects raw model, tokenized inputs, loss slices, pad id
        pad_id = attack_manager.target_model.tokenizer.pad_token_id

        score_list, current_loss, best_id = self.sel_loss.select(
            attack_manager.target_model.model,
            inputs,
            loss_slices,
            pad_id,
            batch_size=batch_size,   # <-- new optional arg
        )

        # convert losses to "higher is better"
        data.score_list = [-x for x in score_list]
        data.current_loss = current_loss
        data.best_id = best_id

        # log top-5 by score
        order = sorted(range(len(data.score_list)), key=lambda k: data.score_list[k], reverse=True)[:5]
        logger.debug("Top-5 scores this pass: {}", [round(data.score_list[i], 4) for i in order])
        for rank, i in enumerate(order):
            logger.debug(
                "  #{:<2d} idx={} | score={:.4f} | cand='{}'",
                rank + 1, i, data.score_list[i], _snip(example.candidate_templates[i])
            )


class AutoDANEvaluator:
    def __init__(self):
        self.scorer = PatternScorer()

    def generate_evaluate(self, example: Example, attack_manager: "AutoDANManager", data: AttackData):
        dev = attack_manager.target_model.device
        pm = data.prompt_manager

        best_template = example.candidate_templates[data.best_id]
        temp_input_ids = pm.get_input_ids(adv_string=best_template)

        try:
            preview = attack_manager.target_model.tokenizer.decode(
                temp_input_ids[: pm._assistant_role_slice.stop], add_special_tokens=False
            )
            logger.debug("Prompt preview (pre-gen): '{}'", preview)
        except Exception:
            logger.debug("Prompt preview not available (decode failed).")

        output_ids = attack_manager.target_model.generate(
            temp_input_ids[: pm._assistant_role_slice.stop].to(dev).unsqueeze(0),
            batch=False,
        )
        response = attack_manager.target_model.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        data.best_template = best_template
        data.response = response
        is_success = self.scorer.score(response)["score"]

        logger.debug("Response (snip): '{}'", _snip(response, 300))
        logger.debug(
            "Step {} (sentence step {}), loss: {}\nbest template: {}\nsuccess: {}",
            data.step, data.sentence_step, data.current_loss, _snip(best_template, 200), is_success,
        )
        data.is_success = bool(is_success)


# -------------------------
# Manager (single-example only)
# -------------------------
class AutoDANManager(BaseAttackManager):

    require_deps("torch")

    def __init__(
        self,
        *,
        target: WhiteboxTargetModel,
        config: AutoDANConfig,
        progress_hook: Optional[BaseAttackProgressHook] = None,
    ):
        super().__init__()
        self.config = config

        # use provided whitebox target
        self.target_model = target
        self.conv_template = target.conversation
        logger.info("AutoDAN target attached: {}", getattr(target, "name", "<unknown>"))

        if config.rephrase_model is None:
            raise ValueError("AutoDANConfig.rephrase_model must be provided.")
        self.rephrase_model = config.rephrase_model

        self.init = AutoDANInit(self.config)
        self.mutator = AutoDANMutator(self.config, self.rephrase_model)
        self.selector = AutoDANSelector()
        self.evaluator = AutoDANEvaluator()
        self.data = self.init.data
        self.progress_hook = progress_hook

    # --------------------------
    # Inner helpers
    # --------------------------
    def _loss_select_evaluate(self, example: Example, batch_size=4):
        with torch.no_grad():
            t = Timer.start()
            self.selector.select_loss(example, self, self.data, batch_size=batch_size)
            logger.debug("select_loss took {:.2f}s", t.end())
            t = Timer.start()
            self.evaluator.generate_evaluate(example, self, self.data)
            logger.debug("generate_evaluate took {:.2f}s", t.end())

    def _crossover_mutation_evolve(self, example: Example):
        elites, parents, num_elites, _ = self.selector.select_elites_new_parents(
            example, self.config, self.data
        )
        mutated = self.mutator.crossover(parents)
        self.mutator.rephrase(mutated)
        next_gen = elites + mutated[: self.config.num_candidates - num_elites]
        assert len(next_gen) == self.config.num_candidates
        logger.debug("NextGen (post XO+rephrase): elites={} | mutated_kept={}", len(elites), len(next_gen) - len(elites))
        # preview some next-gen candidates
        for i, cand in enumerate(next_gen[:6]):
            logger.debug("NextGen[{}]: '{}'", i, _snip(cand))
        example.candidate_templates = next_gen

    def _synonyms_replacement_rephrase_mutation_evolve(self, example: Example):
        elites, parents, num_elites, _ = self.selector.select_elites_new_parents(
            example, self.config, self.data
        )
        mutated = self.mutator.synonyms_replacement(parents, example, self.data)
        self.mutator.rephrase(mutated)
        next_gen = elites + mutated[: self.config.num_candidates - num_elites]
        assert len(next_gen) == self.config.num_candidates
        logger.debug("NextGen (post synonyms+rephrase): elites={} | mutated_kept={}", len(elites), len(next_gen) - len(elites))
        for i, cand in enumerate(next_gen[:6]):
            logger.debug("NextGen[{}]: '{}'", i, _snip(cand))
        example.candidate_templates = next_gen

    # --------------------------
    # Public API — single example
    # --------------------------
    def run(self, query: str, target: str = "Sure, here's", batch_size=1) -> AttackRunResult[AutoDANRunDetails]:
        """
        Run AutoDAN on a single (query, target) and return the best crafted prompt + metadata.
        """
        example = Example(query=query, target=target)
        self.init.example_init(self, example)

        # initial randomization
        self.mutator.rephrase(example.candidate_templates)
        logger.debug("After initial rephrase, candidate[0]: {}", _snip(example.candidate_templates[0]))

        # telemetry: one behavior, num_steps "strategies"
        if self.progress_hook:
            self.progress_hook.on_total_behaviors(1)
            self.progress_hook.on_behavior_start(0, 0, 1)
            self.progress_hook.on_total_strategies(self.config.num_steps)

        best_score_seen = float("-inf")
        best_prompt = None
        best_response = None
        best_step_index = -1
        best_sentence_step_index = -1
        total_evaluations = 0

        for step in trange(self.config.num_steps):
            self.init.step_init(step)

            if self.progress_hook:
                self.progress_hook.on_strategy_start(0, step + 1, step + 1, self.config.num_steps)

            # score population & evaluate champion
            self._loss_select_evaluate(example, batch_size=batch_size)
            total_evaluations += 1

            # telemetry: best score update
            current_best_score = self.data.score_list[self.data.best_id]
            logger.debug("Step {} best_id={} score={:.4f}", step, self.data.best_id, current_best_score)

            if self.progress_hook:
                self.progress_hook.on_best_score_update(
                    "AutoDAN",
                    current_best_score,
                    {
                        "prompt": example.candidate_templates[self.data.best_id],
                        "response": self.data.response or "",
                    },
                )
                prev_best = best_score_seen if best_score_seen != float("-inf") else float("nan")
                try:
                    self.progress_hook.on_new_global_best(
                        "AutoDAN",
                        float(current_best_score),
                        float(prev_best),
                        {
                            "prompt": example.candidate_templates[self.data.best_id],
                            "response": self.data.response or "",
                        },
                    )
                except Exception as e:
                    logger.debug("on_new_global_best hook failed: {}", e)

            # book-keeping
            if current_best_score > best_score_seen:
                logger.info("New global best @ step {}: {:.4f} | cand='{}' | resp='{}'",
                            step, current_best_score,
                            _snip(example.candidate_templates[self.data.best_id]),
                            _snip(self.data.response, 200))
                best_score_seen = current_best_score
                best_prompt = example.candidate_templates[self.data.best_id]
                best_response = self.data.response
                best_step_index = step
                best_sentence_step_index = -1  # top-level improvement

            if self.data.is_success:
                logger.info("Early success @ step {} with score {:.4f}", step, current_best_score)
                if self.progress_hook:
                    self.progress_hook.on_success(step + 1, current_best_score, best_prompt)
                    self.progress_hook.on_strategy_end(
                        {"iteration": step + 1, "best_score": current_best_score},
                        step + 1,
                        self.config.num_steps,
                    )
                    # Publish a final snapshot for the behavior
                    self.progress_hook.on_behavior_end(
                        {"prompt": best_prompt, "response": best_response, "score": current_best_score},
                        0, 1
                    )
                break

            # evolve: crossover + rephrase (global), then sentence-level synonyms + rephrase
            self._crossover_mutation_evolve(example)

            for sstep in range(self.config.sentence_level_steps):
                self.init.sentence_step_init(sstep)
                self._loss_select_evaluate(example)
                total_evaluations += 1

                current_best_score = self.data.score_list[self.data.best_id]
                logger.debug("  SentStep {} best_id={} score={:.4f}", sstep, self.data.best_id, current_best_score)

                if current_best_score > best_score_seen:
                    logger.info("  New global best @ step {} / sstep {}: {:.4f} | cand='{}' | resp='{}'",
                                step, sstep, current_best_score,
                                _snip(example.candidate_templates[self.data.best_id]),
                                _snip(self.data.response, 200))
                    best_score_seen = current_best_score
                    best_prompt = example.candidate_templates[self.data.best_id]
                    best_response = self.data.response
                    best_step_index = step
                    best_sentence_step_index = sstep

                if self.data.is_success:
                    logger.info("  Success in sentence step {} with score {:.4f}", sstep, current_best_score)
                    if self.progress_hook:
                        self.progress_hook.on_success(step + 1, current_best_score, example.candidate_templates[self.data.best_id])
                    break

                self._synonyms_replacement_rephrase_mutation_evolve(example)

            if self.progress_hook:
                self.progress_hook.on_strategy_end(
                    {"iteration": step + 1, "best_score": best_score_seen}, step + 1, self.config.num_steps
                )

            # final forced eval on last iteration
            if (step == self.config.num_steps - 1) and not self.data.is_success:
                logger.debug("Final forced eval at last step")
                self._loss_select_evaluate(example)
                total_evaluations += 1

        # compose final prompt string
        final_prefix = self.data.best_template if self.data.best_template else best_prompt
        final_prompt = (final_prefix + " " + example.query).strip()
        logger.info("Final best score: {:.4f} | success={} | final prefix='{}'",
                    best_score_seen, bool(self.data.is_success), _snip(final_prefix))

        # publish final snapshot to the hook instead of self.log(...)
        if self.progress_hook:
            try:
                final_loss_val = (
                    float(self.data.current_loss.item()) if hasattr(self.data.current_loss, "item")
                    else (float(self.data.current_loss) if self.data.current_loss is not None else None)
                )
            except Exception:
                final_loss_val = None

            self.progress_hook.on_behavior_end(
                {
                    "step": self.data.step,
                    "loss": final_loss_val,
                    "success": bool(self.data.is_success),
                    "final_template": final_prefix,
                    "query": example.query,
                    "final_query": final_prompt,
                    "response": self.data.response,
                    "best_score": best_score_seen,
                    "best_step_index": best_step_index,
                    "best_sentence_step_index": best_sentence_step_index,
                    "total_evaluations": total_evaluations,
                },
                0, 1
            )

        # --- Package as AttackRunResult with a custom payload
        try:
            kind = AttackFlavor.AUTODAN
        except AttributeError:
            kind = getattr(AttackFlavor, "OTHER", AttackFlavor.PAIR)

        payload = AutoDANRunDetails(
            mutation_rate=self.config.mutation_rate,
            num_candidates=self.config.num_candidates,
            num_steps=self.config.num_steps,
            ratio_elites=self.config.ratio_elites,
            num_points=self.config.num_points,
            crossover_rate=self.config.crossover_rate,
            sentence_level_steps=self.config.sentence_level_steps,
            word_dict_size=self.config.word_dict_size,
            model_display_name=self.config.model_display_name,
            best_step_index=max(best_step_index, 0),
            best_sentence_step_index=best_sentence_step_index,
            total_evaluations=total_evaluations,
            final_loss=float(self.data.current_loss.item()) if hasattr(self.data.current_loss, "item") else (
                float(self.data.current_loss) if self.data.current_loss is not None else None
            ),
        )

        return AttackRunResult[AutoDANRunDetails](
            kind=kind,
            success=bool(self.data.is_success),
            score=float(best_score_seen) if best_score_seen != float("-inf") else float("-1e9"),
            prompt=final_prompt,             # full crafted prompt (prefix + query)
            response=best_response or "",
            payload=payload,
        )

