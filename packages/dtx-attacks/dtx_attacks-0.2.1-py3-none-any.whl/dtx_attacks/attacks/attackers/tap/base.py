from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, MutableMapping, Optional, Protocol, runtime_checkable



class BaseSelection:
    def __init__(self):
        pass

# ---------- Core data types ----------

@dataclass(frozen=True)
class Message:
    """One chat turn."""
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class AttackContext:
    """
    Shared context for the attacker when proposing children.
    A TAP orchestrator populates this as the search proceeds.
    """
    system_prompt: Optional[str] = None
    keep_last_n: int = 3
    branching_factor: int = 4
    max_attempts: int = 5

    # Latest conversation/history with the *attacker* model (if relevant)
    history: List[Message] = field(default_factory=list)

    # Free-form metadata the caller can set and read
    attrs: MutableMapping[str, str] = field(default_factory=dict)


# ---------- Required abstractions ----------

@runtime_checkable
class AttackerModel(Protocol):
    """
    Proposes K child prompts given one or more parent prompts.
    Implementations can be chat- or completion-style under the hood.
    """
    def generate_children(
        self,
        parents: List[str],
        *,
        k: int,
        context: AttackContext,
    ) -> List[str]:
        """
        Return up to k * len(parents) mutated prompts (flat list).
        Implementations MAY return fewer (e.g., filtering invalid children).
        """
        ...