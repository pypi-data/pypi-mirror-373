# dtx_attacks/attacks/attack_result.py
from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from ..base import AttackFlavor

# Ensure enums dump to their string value
JsonEnumConfig = ConfigDict(use_enum_values=True)

# ---- Generic payload for attack-specific details ----
T = TypeVar("T")

class AttackRunResult(BaseModel, Generic[T]):
    """
    Generic container for a single attack run result.
    - kind: which attack algorithm produced this
    - success: whether the run met or exceeded its success threshold
    - score: global best score from the run (redundant with payload fields, kept for quick access)
    - prompt/response: global best prompt & response for convenience
    - payload: attack-specific details (typed)
    """
    model_config = JsonEnumConfig

    kind: AttackFlavor = Field(...)
    success: bool = Field(...)
    score: float = Field(...)
    prompt: str = Field(default="")
    response: str = Field(default="")
    payload: Optional[T] = Field(default=None)
