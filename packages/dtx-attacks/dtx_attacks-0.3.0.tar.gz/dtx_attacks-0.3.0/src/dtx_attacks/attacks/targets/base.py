from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Mapping, Optional, Dict, Any, Sequence, overload, Union, cast
from abc import ABC, abstractmethod

Message = Mapping[str, str]
Messages = List[Message]
PromptLike = Union[str, Message, Sequence[Message]]

@dataclass(frozen=True)
class GenerationConfig:
    max_new_tokens: int = 256
    temperature: float = 1.0
    top_p: float = 1.0
    stop: Optional[List[str]] = None
    extra: Mapping[str, object] = field(default_factory=dict)

    def openai_format(self, *, include_none: bool = False, **overrides: Any) -> Dict[str, Any]:
        base = {"max_tokens": self.max_new_tokens, "temperature": self.temperature, "top_p": self.top_p, "stop": self.stop}
        if not include_none:
            base = {k: v for k, v in base.items() if v is not None}
        return {**base, **dict(self.extra or {}), **overrides}

    def to_hf_format(self, *, include_none: bool = False, **overrides: Any) -> Dict[str, Any]:
        """
        Convert to kwargs suitable for transformers.GenerationMixin.generate(...).

        Notes:
        - HF generate expects 'max_new_tokens', 'temperature', 'top_p', etc.
        - 'stop' is NOT a supported kwarg in HF; it is intentionally omitted here.
          If you need stop sequences, add a StoppingCriteria via your call site.
        - 'extra' is merged last, then 'overrides' can replace anything.
        """
        base: Dict[str, Any] = {
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            # "stop" is intentionally not included; handle via StoppingCriteria if needed.
        }

        if include_none:
            merged = {**base, **dict(self.extra or {}), **overrides}
        else:
            pruned = {k: v for k, v in base.items() if v is not None}
            merged = {**pruned, **{k: v for k, v in dict(self.extra or {}).items() if v is not None}, **overrides}

        # Ensure we don't accidentally pass an unsupported 'stop' through extras/overrides
        merged.pop("stop", None)
        return merged

class TargetModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...


class BlackboxTargetModel(TargetModel):
    """API-only targets. Provides common chat normalization helpers."""

    @abstractmethod
    def reset(self) -> None: ...

    @overload
    def query(self, prompt: str, config: Optional[GenerationConfig] = None) -> str: ...
    @overload
    def query(self, prompt: Message, config: Optional[GenerationConfig] = None) -> str: ...
    @overload
    def query(self, prompt: Sequence[Message], config: Optional[GenerationConfig] = None) -> str: ...
    @abstractmethod
    def query(self, prompt: PromptLike, config: Optional[GenerationConfig] = None) -> str: ...
    @abstractmethod
    def batch_query(self, prompts: List[str], config: Optional[GenerationConfig] = None) -> List[str]: ...

    def _to_messages(self, prompt: PromptLike) -> Messages:
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        if isinstance(prompt, Mapping):
            role = prompt.get("role"); content = prompt.get("content")
            if isinstance(role, str) and isinstance(content, str):
                return [cast(Message, {"role": role, "content": content})]
            raise ValueError(f"Invalid message mapping: {prompt!r}")
        if isinstance(prompt, Sequence):
            msgs: Messages = []
            for i, item in enumerate(prompt):
                if not isinstance(item, Mapping):
                    raise ValueError(f"Item {i} not a mapping: {item!r}")
                role = item.get("role"); content = item.get("content")
                if not (isinstance(role, str) and isinstance(content, str)):
                    raise ValueError(f"Invalid message at {i}: {item!r}")
                msgs.append(cast(Message, {"role": role, "content": content}))
            if not msgs:
                raise ValueError("Empty conversation sequence")
            return msgs
        raise ValueError(f"Unsupported prompt type: {type(prompt).__name__}")

    def _ensure_system(self, msgs: Messages, system_prompt: str) -> Messages:
        if not msgs or msgs[0].get("role") != "system":
            return [{"role": "system", "content": system_prompt}, *msgs]
        return msgs

class WhiteboxTargetModel(TargetModel):
    """Targets with weights/tokenizer. Exposes properties used by whitebox attacks."""
    @property
    @abstractmethod
    def model(self) -> Any: ...
    @property
    @abstractmethod
    def tokenizer(self) -> Any: ...
    @property
    @abstractmethod
    def device(self) -> Any: ...
    @property
    @abstractmethod
    def conversation(self) -> Any: ...
    @abstractmethod
    def generate(self, *args, **kwargs) -> Any: ...

# Back-compat alias
TargetClient = TargetModel
