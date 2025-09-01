from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel
from loguru import logger

# dtx_attacks building blocks
from dtx_attacks.models.base import Model
from dtx_attacks.attacks.targets.base import TargetClient, GenerationConfig
from dtx_attacks.attacks.attackers.base.results import AttackRunResult, AttackFlavor
from dtx_attacks.attacks.templates.seed_template import SeedTemplate
from dtx_attacks.evaluation.scorers.prompted_llm_scorer import (
    PromptedLLMScorer,
    PromptedLLMScorerConfig,
)
from dtx_attacks.attacks.attackers.telemetry.progress_hook import BaseAttackProgressHook

"""
ActorAttackRunner — dtx_attacks-style orchestrator with progress hook integration (PAIR-like)
"""

SPLIT_TOKEN: str = "[SPLIT]"


class ActorRunDetails(BaseModel):
    """Telemetry about the run for downstream analysis/UX."""
    behavior: str
    actors: List[str]
    chosen_actor: Optional[str]
    num_questions_total: int
    judge_template: str
    success_threshold: float
    classifier_score: float


@dataclass
class ActorAttackConfig:
    # Helper models
    behavior_model: Model
    actors_model: Model
    questions_model: Model

    # Target generation config
    gen_cfg: GenerationConfig = GenerationConfig(max_new_tokens=150, temperature=1.0, top_p=1.0)

    # Prompts/templates
    behavior_extraction_prompt: Optional[str] = None
    actors_generation_prompt: Optional[str] = None
    questions_generation_prompt: Optional[str] = None

    # Seed templates
    seed_provider: SeedTemplate = SeedTemplate()

    # Judging/classification
    eval_model: Optional[Model] = None
    judge_template: str = "chao2023pair"
    judge_generation_kwargs: Optional[dict] = None
    success_threshold: float = 10.0

    # Logging / persistence
    res_save_path: Optional[str] = None
    delete_existing_res: bool = False

    conversation_mode: str = "actor-network"
    """
    Controls how chat history is preserved:
    - "actor-network": preserve full history across all actors (paper default)
    - "per-actor": reset history per actor, but keep multi-turn inside actor
    - "stateless": each Q/A independent, no history at all
    """

class ActorAttackRunner:
    """Actor-network-inspired attack orchestrator with hook events."""

    def __init__(self, *, target: TargetClient, config: ActorAttackConfig,
                 progress_hook: Optional[BaseAttackProgressHook] = None) -> None:
        self.target = target
        self.cfg = config
        self.progress_hook = progress_hook

        # Resolve default prompts
        if not (self.cfg.behavior_extraction_prompt and self.cfg.actors_generation_prompt and self.cfg.questions_generation_prompt):
            tmpls = self.cfg.seed_provider.get_templates("ACTOR", num=-1)
            if self.cfg.behavior_extraction_prompt is None and len(tmpls) > 0:
                self.cfg.behavior_extraction_prompt = tmpls[0]
            if self.cfg.actors_generation_prompt is None and len(tmpls) > 1:
                self.cfg.actors_generation_prompt = tmpls[1]
            if self.cfg.questions_generation_prompt is None and len(tmpls) > 2:
                self.cfg.questions_generation_prompt = tmpls[2]

        # Judge setup
        self.judge = None
        if self.cfg.eval_model is not None:
            self.judge = PromptedLLMScorer(
                PromptedLLMScorerConfig(
                    model=self.cfg.eval_model,
                    prompt_template=self.cfg.judge_template,
                    generation_kwargs=self.cfg.judge_generation_kwargs or {"temperature": 0.0, "max_tokens": 256},
                )
            )

        # Logging prep
        if self.cfg.res_save_path:
            if self.cfg.delete_existing_res and os.path.exists(self.cfg.res_save_path):
                os.remove(self.cfg.res_save_path)
            os.makedirs(os.path.dirname(self.cfg.res_save_path) or ".", exist_ok=True)

        logger.debug(
            "ActorAttackRunner initialized | target={} | judge={} | hook={}",
            getattr(self.target, "name", "<unknown>"),
            bool(self.judge),
            bool(self.progress_hook),
        )

    # --------------------------
    # Public API
    # --------------------------
    def run(self, prompt: str) -> AttackRunResult[ActorRunDetails]:
        logger.info("ActorAttack started | prompt='{}'", _snip(prompt))
        if self.progress_hook:
            self.progress_hook.on_total_behaviors(1)
            self.progress_hook.on_behavior_start(0, 0, 1)

        # 1) Behavior extraction
        behavior = self._extract_behavior(prompt)
        logger.debug("Extracted behavior: {}", _snip(behavior))

        # 2) Actors generation
        actors = self._generate_actors(behavior)
        logger.debug("Generated {} actors", len(actors))
        if self.progress_hook:
            self.progress_hook.on_total_strategies(len(actors) or 1)

        # 3) Iterate actors -> questions -> target chat
        best_prompt, best_response, best_score = "", "", float("-inf")
        chosen_actor: Optional[str] = None
        num_questions_total = 0

        # history container (shared only if actor-network)
        global_history: List[dict] = []

        for idx, actor in enumerate(actors or [""]):
            if self.progress_hook:
                self.progress_hook.on_strategy_start({"actor": actor}, idx + 1, idx + 1, len(actors) or 1)

            questions = self._generate_questions(behavior, actor)
            if not questions:
                if self.progress_hook:
                    self.progress_hook.on_strategy_end(
                        {"actor": actor, "reason": "no-questions", "score": 0.0}, idx + 1, len(actors) or 1
                    )
                continue

            num_questions_total += len(questions)
            if self.progress_hook:
                self.progress_hook.on_total_turns(len(questions))

            # history setup based on mode
            if self.cfg.conversation_mode == "actor-network":
                history: List[dict] = global_history
            elif self.cfg.conversation_mode == "per-actor":
                history = []
            else:  # stateless
                history = []

            last_resp = ""
            for t_idx, q in enumerate(questions):
                if self.progress_hook:
                    self.progress_hook.on_turn_start(
                        {"actor": actor, "question": q}, idx + 1, t_idx, idx * len(questions) + t_idx, len(questions)
                    )

                last_resp, history = self._chat_target([q], history)

                if self.cfg.conversation_mode == "actor-network":
                    global_history = history  # persist across actors

                if self.progress_hook:
                    self.progress_hook.on_turn_end(
                        {"actor": actor, "response": last_resp, "score": 0.0},
                        idx * len(questions) + t_idx,
                        len(questions),
                    )

            prompt_block = "\n".join(q for q in questions if q.strip())
            response = last_resp

            score = self._classify(prompt_block, response, goal=prompt)
            logger.debug("Actor '{}' -> score={}", actor, score)
            if self.progress_hook:
                self.progress_hook.on_best_score_update(
                    "ACTOR", score, {"actor": actor, "prompt": prompt_block, "response": response}
                )

            if score > best_score:
                best_score, best_prompt, best_response, chosen_actor = score, prompt_block, response, actor

            # Early stop
            if score >= self.cfg.success_threshold:
                logger.info("Success threshold reached (score={}) with actor '{}'", score, actor)
                if self.progress_hook:
                    self.progress_hook.on_success(idx + 1, score, prompt_block)
                    self.progress_hook.on_strategy_end({"actor": actor, "score": score}, idx + 1, len(actors) or 1)
                    self.progress_hook.on_behavior_end({"best_score": score}, 0, 1)
                break

            if self.progress_hook:
                self.progress_hook.on_strategy_end({"actor": actor, "score": score}, idx + 1, len(actors) or 1)

        details = ActorRunDetails(
            behavior=behavior or "",
            actors=actors,
            chosen_actor=chosen_actor,
            num_questions_total=num_questions_total,
            judge_template=self.cfg.judge_template,
            success_threshold=self.cfg.success_threshold,
            classifier_score=float(best_score if best_score != float("-inf") else 0.0),
        )

        success = best_score >= self.cfg.success_threshold
        result = AttackRunResult[ActorRunDetails](
            kind=AttackFlavor.ACTOR,
            success=bool(success),
            score=float(best_score if best_score != float("-inf") else 0.0),
            prompt=best_prompt,
            response=best_response,
            payload=details,
        )

        logger.info("ActorAttack finished | success={} | score={}", success, result.score)
        if self.progress_hook:
            self.progress_hook.on_behavior_end({"best_score": result.score}, 0, 1)
        return result

    # --------------------------
    # Internals
    # --------------------------
    def _extract_behavior(self, original_prompt: str) -> str:
        if not self.cfg.behavior_extraction_prompt:
            return ""
        try:
            prompt = self.cfg.behavior_extraction_prompt.format(ORIGINAL_PROMPT=original_prompt)
            out = self.cfg.behavior_model.generate(prompt)
            return (out or "").strip()
        except Exception as e:
            logger.error("Behavior extraction failed: {}", e)
            return ""

    def _generate_actors(self, behavior: str) -> List[str]:
        if not self.cfg.actors_generation_prompt:
            return []
        try:
            prompt = self.cfg.actors_generation_prompt.format(EXTRACTED_BEHAVIOR=behavior)
            out = self.cfg.actors_model.generate(prompt)
            text = (out or "").strip()
            parts = [p.strip() for p in text.split(SPLIT_TOKEN)] if SPLIT_TOKEN in text else [t.strip() for t in text.split("\n")]
            return [p for p in parts if p]
        except Exception as e:
            logger.error("Actors generation failed: {}", e)
            return []

    def _generate_questions(self, behavior: str, actor: str) -> List[str]:
        if not self.cfg.questions_generation_prompt:
            return []
        try:
            prompt = self.cfg.questions_generation_prompt.format(EXTRACTED_BEHAVIOR=behavior, ACTOR=actor)
            out = self.cfg.questions_model.generate_clean(prompt)
            text = (out or "").strip()
            parts = [p.strip() for p in text.split(SPLIT_TOKEN)] if SPLIT_TOKEN in text else [t.strip() for t in text.split("\n")]
            return [p for p in parts if p]
        except Exception as e:
            logger.error("Questions generation failed for actor '{}': {}", actor, e)
            return []

    def _chat_target(
        self,
        questions: List[str],
        history: Optional[List[dict]] = None,
    ) -> tuple[str, List[dict]]:
        """
        Stateless helper: takes current history and new questions,
        returns last response and updated history.

        Args:
            questions: list of new user questions (strings).
            history: prior conversation history [{"role":..., "content":...}].

        Returns:
            (last_response, updated_history)
        """
        chat_history = history[:] if history else []
        last_response = ""

        for q in questions:
            if not q.strip():
                continue
            chat_history.append({"role": "user", "content": q})
            try:
                last_response = self.target.query(chat_history, config=self.cfg.gen_cfg)
            except Exception as e:
                logger.error("TargetClient.query failed: {}", e)
                last_response = last_response or ""
            chat_history.append({"role": "assistant", "content": last_response})

        return last_response, chat_history


    def _classify(self, prompt_block: str, response: str, *, goal: str) -> float:
        if not self.judge:
            return 0.0
        try:
            out = self.judge.score(query=prompt_block, response=response, goal=goal)
            return float(out.get("score", 0.0))
        except Exception as e:
            logger.error("Classification failed: {}", e)
            return 0.0


# -------------------------
# Helpers
# -------------------------

def _snip(text: str, n: int = 180) -> str:
    if text is None:
        return ""
    s = str(text).replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"
