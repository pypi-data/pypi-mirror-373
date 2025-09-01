from __future__ import annotations

import re
import random
from typing import Optional, List
from dataclasses import dataclass, field



# -------------------------
# Config (dataclass for generic adapter)
# -------------------------
@dataclass
class BinaryMutationConfig:
    """
    Transform selected words (or the whole prompt) into binary.
    - bits_per_char: width per character (8, 16, 32).
    - indices: convert words at these 0-based positions (mutually exclusive with others).
    - keywords: convert words matching any of these (case-insensitive).
    - proportion: convert this fraction of words at random (0..1).
    - regex: Python regex (string) to match words to convert (case-insensitive).
    - binary_space: when True AND all words are selected, join using binary ' ' between words.
    """
    bits_per_char: int = field(
        default=16,
        metadata={"help": "Bits per char (8, 16, or 32).", "choices": [8, 16, 32]},
    )
    indices: Optional[List[int]] = field(
        default=None,
        metadata={"help": "0-based word indices to convert (mutually exclusive)."},
    )
    keywords: Optional[List[str]] = field(
        default=None,
        metadata={"help": "Words to match (case-insensitive). Mutually exclusive."},
    )
    proportion: Optional[float] = field(
        default=None,
        metadata={"help": "Random fraction 0..1 of words to convert. Mutually exclusive."},
    )
    regex: Optional[str] = field(
        default=None,
        metadata={"help": "Regex pattern to match words (case-insensitive). Mutually exclusive."},
    )
    binary_space: bool = field(
        default=False,
        metadata={"help": "If all words are selected, join with binary representation of space."},
    )


# -------------------------
# Mutation
# -------------------------
class BinaryMutation:
    """
    Transforms input text into its binary representation with configurable bits per character (8, 16, or 32).
    Supports selecting which words to convert by indices, keywords, proportion, or regex.
    """

    name = "binary"
    description = "Convert words (or entire prompt) to binary with 8/16/32 bits; supports regex/keywords/indices/proportion."

    def __init__(self, config: Optional[BinaryMutationConfig] = None):
        self.cfg = config or BinaryMutationConfig()

    # --- Public API expected by adapter ---
    def mutate(self, prompt: str) -> Optional[str]:
        # Tokenize into words + spaces (preserve whitespace)
        tokens = list(_iter_tokens(prompt))
        words = [t for t in tokens if t.is_word]

        if not words:
            return prompt

        # Determine selection mode (mutually exclusive)
        mode_count = sum(
            x is not None for x in (self.cfg.indices, self.cfg.keywords, self.cfg.proportion, self.cfg.regex)
        )
        if mode_count > 1:
            raise ValueError("Only one of indices/keywords/proportion/regex may be provided.")

        selected: set[int] = set()

        if self.cfg.indices is not None:
            selected = {i for i in self.cfg.indices if 0 <= i < len(words)}
        elif self.cfg.keywords:
            kw = {k.lower() for k in self.cfg.keywords}
            for i, w in enumerate(words):
                if w.text.lower() in kw:
                    selected.add(i)
        elif self.cfg.regex:
            pat = re.compile(self.cfg.regex, flags=re.IGNORECASE)
            for i, w in enumerate(words):
                if pat.search(w.text):
                    selected.add(i)
        elif self.cfg.proportion is not None:
            p = max(0.0, min(1.0, float(self.cfg.proportion)))
            rng = random.Random()  # seed is passed via adapter if technique uses randomness elsewhere
            for i in range(len(words)):
                if rng.random() <= p:
                    selected.add(i)
        else:
            # No selector -> all words
            selected = set(range(len(words)))

        # Validate bits against selected content
        bits = self._validate_bits(self.cfg.bits_per_char)
        for i in selected:
            self._validate_word_bits(words[i].text, bits)

        # Convert
        word_idx = 0
        out_parts: List[str] = []
        for t in tokens:
            if not t.is_word:
                out_parts.append(t.text)
                continue
            if word_idx in selected:
                out_parts.append(self._to_binary(t.text, bits))
            else:
                out_parts.append(t.text)
            word_idx += 1

        out = "".join(out_parts)

        # If all words selected and binary_space=True, replace literal spaces between words with binary of ' '
        if self.cfg.binary_space and len(selected) == len(words):
            space_bin = format(ord(" "), f"0{bits}b")
            # Replace runs of spaces with single binary-space surrounded by single spaces
            out = re.sub(r"\s+", f" {space_bin} ", out.strip())

        return out

    # --- Helpers ---
    @staticmethod
    def _validate_bits(bits: int) -> int:
        if bits not in (8, 16, 32):
            raise ValueError("bits_per_char must be one of 8, 16, 32.")
        return bits

    @staticmethod
    def _validate_word_bits(word: str, bits: int) -> None:
        max_code_point = max((ord(c) for c in word), default=0)
        min_bits_required = max_code_point.bit_length()
        if bits < min_bits_required:
            raise ValueError(
                f"bits_per_char={bits} too small for characters in '{word}'. "
                f"Minimum required: {min_bits_required}."
            )

    @staticmethod
    def _to_binary(word: str, bits: int) -> str:
        return " ".join(format(ord(c), f"0{bits}b") for c in word)


# ----- internal token model -----
@dataclass
class _Tok:
    text: str
    is_word: bool


def _iter_tokens(text: str):
    # words = non-space runs, spaces = whitespace runs
    for m in re.finditer(r"\S+|\s+", text):
        chunk = m.group(0)
        yield _Tok(text=chunk, is_word=not chunk.isspace())
