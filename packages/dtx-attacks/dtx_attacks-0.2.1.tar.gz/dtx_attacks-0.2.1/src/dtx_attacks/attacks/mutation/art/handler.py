from pydantic import BaseModel, Field
from typing import Optional, List
import re
from loguru import logger

from .prompts import JAILBREAK_PROMPT, JAILBREAK_SIMPLE_PROMPT
from art import text2art


class ArtPromptMutationConfig(BaseModel):
    sensitive_terms: Optional[List[str]] = Field(
        None,
        description="List of words/phrases to mask in the attack. Could be either a word or a phrase."
    )
    simple_mode: bool = Field(
        True,
        description="Use simple mode for the attack (i.e. hash separated letters as ascii art). Default: True"
    )
    disable_font_learn: bool = Field(
        True,
        description="Disable font learning. Default: True"
    )


class ArtPromptMutation:
    """
    Simplified transformer: converts input prompt into adversarial ASCII-art jailbreak prompt.
    """

    def __init__(self, config: ArtPromptMutationConfig):
        self._config = config
        # Normalize sensitive_terms → always a list
        self._sensitive_terms: List[str] = config.sensitive_terms or []
        self._simple_mode = config.simple_mode
        self._jailbreak_prompt = (
            JAILBREAK_SIMPLE_PROMPT if self._simple_mode else JAILBREAK_PROMPT
        )

    def mutate(self, prompt: str) -> Optional[str]:
        """
        Transform input prompt into an adversarial jailbreak prompt.
        """
        harmful_word = self._find_harmful_word(prompt)
        if not harmful_word:
            logger.error("No harmful word found in prompt: {}", prompt)
            return None

        masked_prompt = (
            prompt.replace(f"[{harmful_word}]", "[MASK]")
                  .replace(harmful_word, "[MASK]")
        )

        banner = (
            self._create_banner_simple(harmful_word)
            if self._simple_mode
            else self._create_banner(harmful_word)
        )

        adv_prompt = self._jailbreak_prompt.format(
            harmful_word_length=len(harmful_word),
            banner=banner,
            masked_prompt=masked_prompt
        )
        logger.debug("Mutated (adversarial) prompt → {}", adv_prompt[:200])
        return adv_prompt

    # -------------------------
    # Helpers
    # -------------------------
    def _find_harmful_word(self, prompt: str) -> Optional[str]:
        # Priority 1: explicitly sensitive terms
        for w in self._sensitive_terms:
            if w and w.lower() in prompt.lower():
                return w

        # Priority 2: anything inside [brackets]
        matches = re.findall(r"\[([^\]]+)\]", prompt)
        if matches:
            return matches[0]
        return None

    def _create_banner_simple(self, word: str) -> str:
        border = (len(word) * 2 + 1) * "#"
        return f"{border}\n#{'#'.join([l.upper() for l in word])}#\n{border}"

    def _create_banner(self, word: str) -> str:
        lines = []
        for idx, char in enumerate(word):
            char_art = text2art(char, "blocks")
            char_lines = [l for l in char_art.splitlines() if l.strip()]
            if idx < len(word) - 1:
                char_lines = [l + "*" for l in char_lines]
            lines.append(char_lines)
        combined = ["".join(line) for line in zip(*lines)]
        return "\n".join(combined)
