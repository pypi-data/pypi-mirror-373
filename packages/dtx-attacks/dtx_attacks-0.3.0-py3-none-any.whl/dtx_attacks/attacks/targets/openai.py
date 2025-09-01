from __future__ import annotations
from typing import List, Optional
from .base import BlackboxTargetModel, GenerationConfig, PromptLike
from dtx_attacks.models.openai_model import OpenAIModel

class OpenAITarget(BlackboxTargetModel):
    def __init__(self, model: OpenAIModel, system_prompt: Optional[str] = None) -> None:
        self._model = model
        self._system_prompt = system_prompt or "You are a helpful, safe assistant."

    @property
    def name(self) -> str:
        return getattr(self._model, "model_name", "openai/unknown")

    def reset(self) -> None:
        pass

    def batch_query(self, prompts: List[str], config: Optional[GenerationConfig] = None) -> List[str]:
        cfg = (config or GenerationConfig()).openai_format()
        batched = [self._ensure_system([{"role": "user", "content": p}], self._system_prompt) for p in prompts]
        return self._model.batch_chat(batched, **cfg)

    def query(self, prompt: PromptLike, config: Optional[GenerationConfig] = None) -> str:
        cfg = (config or GenerationConfig()).openai_format()
        msgs = self._ensure_system(self._to_messages(prompt), self._system_prompt)
        return self._model.chat(msgs, **cfg)
