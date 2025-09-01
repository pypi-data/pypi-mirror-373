# dtx_attacks/attacks/mutation/rot13/handler.py

from __future__ import annotations

import re
import codecs
from typing import Optional, List
from dataclasses import dataclass, field

from loguru import logger


# -------------------------
# Config
# -------------------------
@dataclass
class Rot13Config:
    """
    Configuration for the ROT13 mutation.

    Behavior:
      - If `sensitive_terms` are provided, only those terms (or any [masked] tokens)
        found in the prompt are encoded. Otherwise, the entire prompt is encoded.
    """
    sensitive_terms: Optional[List[str]] = field(
        default=None,
        metadata={
            "help": "Comma-separated list of terms to encode; if empty, encode full prompt (e.g., bomb,attack)"
        },
    )


# -------------------------
# Mutation
# -------------------------
class Rot13Mutation:
    """
    ROT13 mutation.

    Encodes text using the classic ROT13 substitution cipher.
    """

    # Exposed to REPL via generic adapter
    name = "rot13"
    description = "Encode text (or selected terms) using the classic ROT13 substitution cipher."

    def __init__(self, config: Optional[Rot13Config] = None):
        self.cfg = config or Rot13Config()

    def mutate(self, prompt: str) -> Optional[str]:
        targets: list[str] = []

        # 1) Collect all sensitive terms present
        if self.cfg.sensitive_terms:
            for word in self.cfg.sensitive_terms:
                if word.lower() in prompt.lower():
                    targets.append(word)
                    logger.debug("Found sensitive term for ROT13: {}", word)

        # 2) If none, check masked content [xxx]
        if not targets:
            matches = re.findall(r"\[([^\]]+)\]", prompt)
            if matches:
                targets = matches
                logger.debug("Found [masked] word(s) for ROT13: {}", matches)

        # 3) If still none, encode full prompt
        if not targets:
            logger.debug("No specific targets detected, applying ROT13 to entire prompt.")
            return self._rot13(prompt)

        # Encode only the targeted terms (case-insensitive)
        adv_prompt = prompt
        for t in targets:
            def _repl(m: re.Match) -> str:
                original = m.group(0)
                return self._rot13(original)

            adv_prompt = re.sub(re.escape(t), _repl, adv_prompt, flags=re.IGNORECASE)
            logger.debug("ROT13 encoded '{}' -> '{}'", t, self._rot13(t))

        return adv_prompt

    # -------------------------
    # Internal encoder
    # -------------------------
    @staticmethod
    def _rot13(text: str) -> str:
        """
        Applies ROT13 to `text`.
        """
        try:
            return codecs.encode(text, "rot13")
        except Exception as e:
            logger.error("ROT13 encoding failed: {}", e)
            return text
