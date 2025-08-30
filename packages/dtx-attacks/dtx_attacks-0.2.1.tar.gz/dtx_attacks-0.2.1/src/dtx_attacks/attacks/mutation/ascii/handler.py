# dtx_attacks/attacks/mutation/ascii/handler.py

from __future__ import annotations

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass

from loguru import logger


# -------------------------
# Config
# -------------------------
@dataclass
class AsciiSmugglingConfig:
    use_unicode_tags: bool = False
    sensitive_terms: Optional[List[str]] = None  # Words to mask, e.g. ["bomb", "weapon"]


# -------------------------
# Mutation
# -------------------------
class AsciiSmugglingMutation:
    """
    Ascii Smuggling mutation.

    Encodes ASCII characters into Unicode private-use / tag characters,
    effectively "smuggling" harmful tokens past filters.
    """

    def __init__(self, config: Optional[AsciiSmugglingConfig] = None):
        self.cfg = config or AsciiSmugglingConfig()

    def mutate(self, prompt: str) -> Optional[str]:
        harmful_terms: list[str] = []

        # 1) Collect all sensitive terms present
        if self.cfg.sensitive_terms:
            for word in self.cfg.sensitive_terms:
                if word.lower() in prompt.lower():
                    harmful_terms.append(word)
                    logger.debug("Found sensitive term for smuggling: {}", word)

        # 2) If none, check masked content [xxx]
        if not harmful_terms:
            matches = re.findall(r"\[([^\]]+)\]", prompt)
            if matches:
                harmful_terms = matches
                logger.debug("Found [masked] word(s) for smuggling: {}", matches)

        # 3) If still none, encode full prompt
        if not harmful_terms:
            logger.debug("No sensitive term detected, encoding entire prompt.")
            _, encoded = self._encode_message(prompt, use_unicode_tags=self.cfg.use_unicode_tags)
            return encoded

        # Encode all harmful terms
        adv_prompt = prompt
        for harmful_word in harmful_terms:
            _, encoded_word = self._encode_message(harmful_word, use_unicode_tags=self.cfg.use_unicode_tags)
            adv_prompt = re.sub(harmful_word, encoded_word, adv_prompt, flags=re.IGNORECASE)
            logger.debug("AsciiSmuggling encoded '{}' -> {}", harmful_word, encoded_word)

        return adv_prompt

    # -------------------------
    # Internal encoder
    # -------------------------
    def _encode_message(self, message: str, use_unicode_tags: bool = False) -> Tuple[str, str]:
        """
        Encodes a message using Unicode code points.

        Args:
            message (str): The message to encode.
            use_unicode_tags (bool): Whether to add Unicode tags at start and end.

        Returns:
            Tuple[str, str]: (code_points_str, encoded_str)
        """
        encoded: str = ""
        code_points: str = ""
        invalid_chars: str = ""

        # Add starting tag if requested
        if use_unicode_tags:
            encoded += chr(0xE0001)
            code_points += "U+E0001 "

        for char in message:
            code_point: int = ord(char)
            if 0x20 <= code_point <= 0x7E:  # ASCII printable range
                new_code_point: int = 0xE0000 + code_point
                encoded += chr(new_code_point)
                code_points += f"U+{new_code_point:X} "
            else:
                invalid_chars += char

        # Add ending tag if requested
        if use_unicode_tags:
            encoded += chr(0xE007F)
            code_points += "U+E007F"

        if invalid_chars:
            logger.warning("Invalid characters detected in AsciiSmuggling: {}", invalid_chars)

        return code_points.strip(), encoded
