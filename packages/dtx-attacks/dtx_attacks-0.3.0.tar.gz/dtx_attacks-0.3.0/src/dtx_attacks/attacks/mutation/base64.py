from __future__ import annotations

import base64
from typing import Optional
from dataclasses import dataclass, field


# -------------------------
# Config (dataclass for generic adapter)
# -------------------------
@dataclass
class Base64MutationConfig:
    """
    Encode the prompt string as Base64.

    - urlsafe: use URL-safe alphabet (-, _) instead of (+, /)
    - strip_padding: remove trailing '=' padding
    - wrap_width: insert newlines every N characters (None = no wrapping)
    """
    urlsafe: bool = field(
        default=False,
        metadata={"help": "Use URL-safe alphabet (-, _) instead of (+, /)."},
    )
    strip_padding: bool = field(
        default=False,
        metadata={"help": "Strip trailing '=' padding characters from the output."},
    )
    wrap_width: Optional[int] = field(
        default=None,
        metadata={"help": "Wrap output at this column width (e.g., 76). None = no wrap."},
    )


# -------------------------
# Mutation
# -------------------------
class Base64Mutation:
    """
    Base64 encode input text with configurable alphabet, padding, and wrapping.
    """

    name = "base64"
    description = "Encode prompt as Base64 (standard or URL-safe), with optional padding strip and line wrapping."

    def __init__(self, config: Optional[Base64MutationConfig] = None):
        self.cfg = config or Base64MutationConfig()

    def mutate(self, prompt: str) -> Optional[str]:
        data = prompt.encode("utf-8")
        if self.cfg.urlsafe:
            enc = base64.urlsafe_b64encode(data).decode("ascii")
        else:
            enc = base64.b64encode(data).decode("ascii")

        if self.cfg.strip_padding:
            enc = enc.rstrip("=")

        if self.cfg.wrap_width and self.cfg.wrap_width > 0:
            w = int(self.cfg.wrap_width)
            enc = "\n".join(enc[i : i + w] for i in range(0, len(enc), w))

        return enc
