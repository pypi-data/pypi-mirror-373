from __future__ import annotations

import random
from loguru import logger
from pydantic import BaseModel
from dataclasses import dataclass
from typing import List, Optional

from dtx_attacks.attacks.targets.base import TargetClient, GenerationConfig
from dtx_attacks.attacks.datasets.attack_dataset import AttackDataset
from dtx_attacks.attacks.datasets.example import Example
from dtx_attacks.attacks.templates.seed_template import SeedTemplate
from dtx_attacks.attacks.attackers.telemetry.progress_hook import BaseAttackProgressHook
from dtx_attacks.attacks.attackers.base.results import AttackRunResult
from dtx_attacks.attacks.attackers.base import AttackFlavor

# Core deps
from dtx_attacks.models.base import Model

# Mutation (attacker-side) — provider-agnostic introspection
from dtx_attacks.attacks.attackers.tap.introspection import IntrospectGeneration

# Selection utilities (match original TAP semantics)
from .delete_off_topic import DeleteOffTopic
from .scores_selection import ScoresSelection

# Judge scorer (LLM-judge)
from dtx_attacks.evaluation.scorers.prompted_llm_scorer import (
    PromptedLLMScorer,
    PromptedLLMScorerConfig,
)


# -------------------------
# Helpers
# -------------------------
def _snip(text: str, n: int = 160) -> str:
    if text is None:
        return ""
    s = str(text).replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"



class TAPRunDetails(BaseModel):
    tree_width: int
    tree_depth: int
    branching_factor: int
    keep_last_n: int
    max_attempts: int
    use_delete_off_topic: bool
    judge_template: str
    success_threshold: float

    total_evaluations: int         # number of model evals (root + children)
    best_depth_index: int          # 0 = root; >=1 for deeper levels


# -------------------------
# Config
# -------------------------
@dataclass
class TAPConfig:
    """
    End-to-end TAP knobs + models.

    Required:
      - attack_model: attacker LLM used by IntrospectGeneration (must implement Model.chat)
      - eval_model:   judge LLM used by DeleteOffTopic and PromptedLLMScorer

    You still pass `target: TargetClient` to TAPRunner separately.
    """
    attack_model: Model
    eval_model: Model

    # Search hyperparameters
    tree_width: int = 3
    tree_depth: int = 3
    branching_factor: int = 3
    keep_last_n: int = 3
    max_attempts: int = 5

    # Target generation config
    gen_cfg: GenerationConfig = GenerationConfig()

    # Scoring & pruning
    success_threshold: float = 10.0
    shuffle_before_rank: bool = True

    # Judge template + kwargs (PromptedLLMScorer)
    judge_template: str = "Mehrotra2023TAP"
    judge_generation_kwargs: Optional[dict] = None

    # Attacker system prompt (if None, pull from SeedTemplate 'TAP')
    system_prompt: Optional[str] = None

    # Whether to apply DeleteOffTopic topical filter before querying target
    use_delete_off_topic: bool = True


# -------------------------
# Auxiliary components
# -------------------------
class TAPMutator:
    """Wraps IntrospectGeneration as a callable mutation operator."""

    def __init__(self, attack_model: Model, system_prompt: str,
                 keep_last_n: int, branching_factor: int, max_n_attack_attempts: int) -> None:
        self.mutator = IntrospectGeneration(
            model=attack_model,
            system_prompt=system_prompt,
            keep_last_n=keep_last_n,
            branching_factor=branching_factor,
            max_n_attack_attempts=max_n_attack_attempts,
            attr_name="jailbreak_prompt",
            prompt_format=None,
        )

    def mutate(self, dataset: AttackDataset) -> AttackDataset:
        return self.mutator(dataset)


class TAPSelector:
    """Topicality filter (DeleteOffTopic) + beam pruning (ScoresSelection)."""

    def __init__(self, eval_model: Model, tree_width: int) -> None:
        self.tree_width = tree_width
        self.eval_model = eval_model

    def constraint(self, dataset: AttackDataset) -> AttackDataset:
        # Guard singleton: the original DeleteOffTopic fallback expects >=2
        if len(dataset) <= 1:
            return dataset
        constr = DeleteOffTopic(self.eval_model, self.tree_width)
        return constr(dataset)

    def select(self, dataset: AttackDataset) -> AttackDataset:
        selector = ScoresSelection(dataset, self.tree_width)
        return selector.select(dataset)


class TAPEvaluator:
    """LLM-judge scoring with PromptedLLMScorer (query/response/goal)."""

    def __init__(self, eval_model: Model, prompt_template: str = "Mehrotra2023TAP",
                 generation_kwargs: Optional[dict] = None) -> None:
        self.judge = PromptedLLMScorer(
            PromptedLLMScorerConfig(
                model=eval_model,
                prompt_template=prompt_template,
                generation_kwargs=generation_kwargs or {"temperature": 0.0, "max_tokens": 256},
            )
        )

    def evaluate_dataset(self, dataset: AttackDataset, *, goal: str) -> None:
        """
        Appends a numeric score per example to example.eval_results, using:
          score = judge.score(query=goal, response=last_target_response, goal=goal)["score"]
        """
        for ex in dataset:
            if not getattr(ex, "target_responses", None):
                ex.eval_results.append(0)
                continue
            resp = ex.target_responses[-1]
            res = self.judge.score(query=goal, response=resp, goal=goal)
            ex.eval_results.append(int(res.get("score", 0)))

    def score(self, *, query: str, response: str, goal: Optional[str] = None) -> int:
        """Convenience: score a single (query/response) pair."""
        g = goal or query
        res = self.judge.score(query=query, response=response, goal=g)
        return int(res.get("score", 0))


# -------------------------
# Runner
# -------------------------
@dataclass
class _Node:
    prompt: str
    response: str
    score: float


class TAPRunner:
    """
    End-to-end TAP orchestrator using:
      - TAPMutator (attacker-side branching)
      - TAPSelector (DeleteOffTopic + ScoresSelection)
      - TAPEvaluator (PromptedLLMScorer judge)
    """

    def __init__(
        self,
        *,
        target: TargetClient,
        config: TAPConfig,
        seed_template: Optional[SeedTemplate] = None,
        progress_hook: Optional[BaseAttackProgressHook] = None,   # <--- hook injected here
    ) -> None:
        self.target = target
        self.cfg = config
        self.seed_template = seed_template or SeedTemplate()
        self.progress_hook = progress_hook

        # Resolve system prompt for the attacker
        system_prompt = self.cfg.system_prompt or self.seed_template.get_templates("TAP", 1)[0]

        # Build modules
        self.mutator = TAPMutator(
            attack_model=self.cfg.attack_model,
            system_prompt=system_prompt,
            keep_last_n=self.cfg.keep_last_n,
            branching_factor=self.cfg.branching_factor,
            max_n_attack_attempts=self.cfg.max_attempts,
        )
        self.selector = TAPSelector(eval_model=self.cfg.eval_model, tree_width=self.cfg.tree_width)
        self.evaluator = TAPEvaluator(
            eval_model=self.cfg.eval_model,
            prompt_template=self.cfg.judge_template,
            generation_kwargs=self.cfg.judge_generation_kwargs,
        )

        logger.debug(
            "TAPRunner initialized | target={} | judge_template={} | use_delete_off_topic={}",
            getattr(self.target, "name", "<unknown>"),
            self.cfg.judge_template,
            self.cfg.use_delete_off_topic,
        )

    # -------------
    # Public API
    # -------------
    def run(self, prompt: str, *, goal: Optional[str] = None) -> AttackRunResult[TAPRunDetails]:
        """
        Execute TAP starting from `prompt`.

        Returns: AttackRunResult[TAPRunDetails]
        """
        g = goal or prompt
        logger.info(
            "Starting TAP on target={} (depth={}, width={}, branch={}).",
            self.target.name,
            self.cfg.tree_depth,
            self.cfg.tree_width,
            self.cfg.branching_factor,
        )
        logger.debug("Root task: {}", _snip(prompt))
        logger.debug("Judge goal: {}", _snip(g))

        # --- Behavior start (entire run = 1 behavior)
        if self.progress_hook:
            self.progress_hook.on_behavior_start(behavior_number=0, behavior_idx=0, total_behaviors=1)

        # Root baseline (no mutation)
        root_resp = self._query_target([prompt])[0]
        root_score = self.evaluator.score(query=prompt, response=root_resp, goal=g)
        best = _Node(prompt=prompt, response=root_resp, score=root_score)
        frontier_nodes: List[_Node] = [best]

        total_evaluations = 1  # counted the root
        best_depth_idx = 0     # depth index (0-based; root)

        # --- Initial structure progress
        if self.progress_hook:
            self.progress_hook.on_structure_progress(
                technique="TAP", structure_type="init", data={"prompt": prompt, "score": root_score}
            )
            self.progress_hook.on_best_score_update(
                technique="TAP",
                score=root_score,
                candidate={"prompt": prompt, "response": root_resp},
            )

        for depth in range(1, self.cfg.tree_depth + 1):
            logger.info("[Depth {}] Expanding {} node(s).", depth, len(frontier_nodes))

            # --- Strategy start (each depth = strategy)
            if self.progress_hook:
                self.progress_hook.on_strategy_start(
                    behavior_number=0,
                    strategy_idx=depth,
                    global_strategy_idx=depth,
                    total_strategies=self.cfg.tree_depth,
                )

            parents_ds = AttackDataset([Example(query=n.prompt, target="") for n in frontier_nodes])

            # Mutate children
            children_ds_parts: List[AttackDataset] = []
            for stream in [AttackDataset([ex]) for ex in parents_ds]:
                mutated = self.mutator.mutate(stream)
                children_ds_parts.append(mutated)
            children_ds = AttackDataset([ex for part in children_ds_parts for ex in part])

            logger.debug("[Depth {}] Generated {} child prompt(s).", depth, len(children_ds))

            if self.progress_hook:
                self.progress_hook.on_structure_progress(
                    technique="TAP",
                    structure_type="generation",
                    data={"depth": depth, "num_children": len(children_ds)},
                )

            if len(children_ds) == 0:
                logger.warning("No children generated; terminating early.")
                break

            # Optional on-topic constraint
            if self.cfg.use_delete_off_topic:
                before = len(children_ds)
                children_ds = self.selector.constraint(children_ds)
                logger.debug("[Depth {}] DeleteOffTopic kept {}/{} prompts.", depth, len(children_ds), before)

                if self.progress_hook:
                    self.progress_hook.on_structure_progress(
                        technique="TAP",
                        structure_type="filtering",
                        data={"depth": depth, "before": before, "after": len(children_ds)},
                    )

                if len(children_ds) == 0:
                    logger.warning("All children filtered as off-topic; terminating early.")
                    break

            # Query target for each child's jailbreak_prompt
            prompts = []
            for ex in children_ds:
                jb = getattr(ex, "jailbreak_prompt", None)
                if jb:
                    prompts.append(jb)
                else:
                    logger.debug("[Depth {}] Example missing jailbreak_prompt; skipping.", depth)

            if not prompts:
                logger.warning("No valid child prompts to query; terminating.")
                break

            responses = self._query_target(prompts)

            # Attach responses
            for ex, r in zip(children_ds, responses):
                ex.target_responses = [r]

            # Judge scoring
            self.evaluator.evaluate_dataset(children_ds, goal=g)

            # Track global best & build nodes
            nodes: List[_Node] = []
            for turn_idx, ex in enumerate(children_ds):
                if self.progress_hook:
                    self.progress_hook.on_turn_start(
                        behavior_number=0,
                        strategy_idx=depth,
                        turn_idx=turn_idx,
                        global_turn_idx=turn_idx,
                        total_turns=len(children_ds),
                    )

                s = ex.eval_results[-1] if ex.eval_results else 0
                r = ex.target_responses[-1] if getattr(ex, "target_responses", None) else ""
                p = getattr(ex, "jailbreak_prompt", ex.query)
                node = _Node(prompt=p, response=r, score=s)
                nodes.append(node)
                total_evaluations += 1

                if s > best.score:
                    logger.debug(
                        "[Depth {}] New global best: {:.2f} (prev {:.2f}) | prompt={}",
                        depth,
                        s,
                        best.score,
                        _snip(p),
                    )
                    if self.progress_hook:
                        self.progress_hook.on_new_global_best(
                            technique="TAP",
                            score=s,
                            prev_best=best.score,
                            candidate={"prompt": p, "response": r},
                        )
                    best = node
                    best_depth_idx = depth  # 0-based root is 0; children at this depth

                if self.progress_hook:
                    self.progress_hook.on_turn_end(
                        turn_result=node,
                        global_turn_idx=turn_idx,
                        total_turns=len(children_ds),
                    )

            # Early stop
            top_iter = max(nodes, key=lambda n: n.score)
            logger.debug("[Depth {}] Iteration best score: {:.2f}", depth, top_iter.score)

            # Always publish current best so far
            if self.progress_hook:
                self.progress_hook.on_best_score_update(
                    technique="TAP",
                    score=best.score,
                    candidate={"prompt": best.prompt, "response": best.response},
                )

            if top_iter.score >= self.cfg.success_threshold:
                logger.info("Success threshold reached (score={:.2f}). Early stopping.", top_iter.score)

                if self.progress_hook:
                    self.progress_hook.on_success(depth=depth, score=top_iter.score, prompt=top_iter.prompt)
                    self.progress_hook.on_strategy_end(
                        strategy_result=top_iter,
                        global_strategy_idx=depth,
                        total_strategies=self.cfg.tree_depth,
                    )
                    self.progress_hook.on_behavior_end(behavior_result=best, behavior_idx=0, total_behaviors=1)

                payload = TAPRunDetails(
                    tree_width=self.cfg.tree_width,
                    tree_depth=self.cfg.tree_depth,
                    branching_factor=self.cfg.branching_factor,
                    keep_last_n=self.cfg.keep_last_n,
                    max_attempts=self.cfg.max_attempts,
                    use_delete_off_topic=self.cfg.use_delete_off_topic,
                    judge_template=self.cfg.judge_template,
                    success_threshold=self.cfg.success_threshold,
                    total_evaluations=total_evaluations,
                    best_depth_index=best_depth_idx,
                )
                return AttackRunResult[TAPRunDetails](
                    kind=AttackFlavor.TAP,
                    success=True,
                    score=top_iter.score,
                    prompt=top_iter.prompt,
                    response=top_iter.response,
                    payload=payload,
                )

            # Beam prune
            frontier_nodes = self._apply_scores_selection(nodes, k=self.cfg.tree_width)
            logger.info(
                "[Depth {}] Kept top {} candidate(s). Current best score={:.2f}.",
                depth,
                len(frontier_nodes),
                best.score,
            )

            if self.progress_hook:
                self.progress_hook.on_strategy_end(
                    strategy_result=top_iter,
                    global_strategy_idx=depth,
                    total_strategies=self.cfg.tree_depth,
                )
                self.progress_hook.on_strategy_end_summary(
                    {"depth": depth, "kept": len(frontier_nodes), "best_score": best.score}
                )

            if not frontier_nodes:
                logger.warning("Frontier empty after pruning; terminating.")
                break

        logger.info("Search finished.")
        logger.debug(
            "Final best: score={:.2f} | prompt={} | resp={}",
            best.score,
            _snip(best.prompt),
            _snip(best.response),
        )

        # --- Behavior end
        if self.progress_hook:
            self.progress_hook.on_behavior_end(behavior_result=best, behavior_idx=0, total_behaviors=1)

        payload = TAPRunDetails(
            tree_width=self.cfg.tree_width,
            tree_depth=self.cfg.tree_depth,
            branching_factor=self.cfg.branching_factor,
            keep_last_n=self.cfg.keep_last_n,
            max_attempts=self.cfg.max_attempts,
            use_delete_off_topic=self.cfg.use_delete_off_topic,
            judge_template=self.cfg.judge_template,
            success_threshold=self.cfg.success_threshold,
            total_evaluations=total_evaluations,
            best_depth_index=best_depth_idx,
        )
        return AttackRunResult[TAPRunDetails](
            kind=AttackFlavor.TAP,
            success=bool(best.score >= self.cfg.success_threshold),
            score=best.score,
            prompt=best.prompt,
            response=best.response,
            payload=payload,
        )


    # -------------
    # Internals
    # -------------
    def _query_target(self, prompts: List[str]) -> List[str]:
        logger.debug("Target query count: {}", len(prompts))
        try:
            out = self.target.batch_query(prompts, config=self.cfg.gen_cfg)  # type: ignore
            logger.debug("Target batch_query succeeded with {} response(s).", len(out))
            return out
        except Exception as e:
            logger.debug("batch_query failed ({}); falling back to sequential.", e)
            results = []
            for i, p in enumerate(prompts):
                r = self.target.query(p, config=self.cfg.gen_cfg)
                logger.debug("Sequential target query[{}] done.", i)
                results.append(r)
            return results

    def _apply_scores_selection(self, nodes: List[_Node], k: int) -> List[_Node]:
        if not nodes:
            return []

        if len(nodes) == 1:
            return nodes

        # Use ScoresSelection to mirror original behavior
        exs = []
        for n in nodes:
            ex = Example(query=n.prompt, target="")
            setattr(ex, "jailbreak_prompt", n.prompt)
            ex.eval_results = [n.score]
            exs.append(ex)

        ds = AttackDataset(exs)
        try:
            selector = ScoresSelection(ds, tree_width=min(k, len(nodes)))
            kept_ds = selector.select(ds)
            kept_prompts = {ex.jailbreak_prompt for ex in kept_ds}
            kept = [n for n in nodes if n.prompt in kept_prompts]
            if not kept:
                items = nodes[:]
                if self.cfg.shuffle_before_rank:
                    random.shuffle(items)
                items.sort(key=lambda n: n.score, reverse=True)
                kept = items[: min(2, len(items))]
            return kept
        except Exception as e:
            logger.warning("ScoresSelection failed ({}). Falling back to rank.", e)
            items = nodes[:]
            if self.cfg.shuffle_before_rank:
                random.shuffle(items)
            items.sort(key=lambda n: n.score, reverse=True)
            kept = [n for n in items if n.score > 0][:k]
            if not kept:
                kept = items[: min(2, len(items))]
            return kept
