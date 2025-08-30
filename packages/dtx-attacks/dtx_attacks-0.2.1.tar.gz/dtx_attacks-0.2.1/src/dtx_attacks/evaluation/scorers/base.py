from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Any, List, Literal, TypedDict

Role = Literal["system", "user", "assistant"]

class BaseScorer:
    def __init__(self):
        pass

    def score(self, query: str, response: str):
        raise NotImplementedError

class ChatMessage(TypedDict):
    role: Role
    content: str


class ModelBackend(ABC):
    """Abstract inference backend for chat-style messages (dict format)."""

    @abstractmethod
    def generate_messages(
        self,
        messages: List[ChatMessage],
        *,
        max_new_tokens: int = 1,
        do_sample: bool = False,
        **gen_kwargs: Any,
    ) -> str:
        """Return the assistant's text completion for the given chat messages."""
        raise NotImplementedError

    # Optional convenience for legacy single-string use (not required).
    def generate(
        self,
        prompt: str,
        *,
        max_new_tokens: int = 1,
        do_sample: bool = False,
        **gen_kwargs: Any,
    ) -> str:
        return self.generate_messages(
            [{"role": "user", "content": prompt}],
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            **gen_kwargs,
        )
