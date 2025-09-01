from __future__ import annotations

import random
from typing import Optional, List, Dict
from dataclasses import dataclass, field

# -------------------------
# Config
# -------------------------
@dataclass
class EmojiConfig:
    """
    Options for Emoji mutation.

    seed: Fix RNG for deterministic output (set via /set seed=123, or CLI --seed).
    probability: 0..1 fraction of alphabetic chars to convert (default 1.0).
    """
    seed: Optional[int] = field(
        default=None,
        metadata={"help": "RNG seed for deterministic emoji choices"},
    )
    probability: float = field(
        default=1.0,
        metadata={"help": "Fraction (0..1) of letters to convert to emoji"},
    )

# -------------------------
# Mutation
# -------------------------
class EmojiMutation:
    """
    Converts English letters into randomly chosen circle/square letter emojis.
    Inspired by pyrit's EmojiConverter (Microsoft) / BASI-LABS Parseltongue.

    - Honors `probability` to partially transform text.
    - Use `seed` to make choices deterministic.
    """

    name = "emoji"
    description = "Map letters to circled/squared-letter emojis with optional deterministic randomness."

    #: Dictionary mapping letters to their corresponding emojis.
    emoji_dict: Dict[str, List[str]] = {
        "a": ["🅐", "🅰️", "🄰"],
        "b": ["🅑", "🅱️", "🄱"],
        "c": ["🅒", "🅲", "🄲"],
        "d": ["🅓", "🅳", "🄳"],
        "e": ["🅔", "🅴", "🄴"],
        "f": ["🅕", "🅵", "🄵"],
        "g": ["🅖", "🅶", "🄶"],
        "h": ["🅗", "🅷", "🄷"],
        "i": ["🅘", "🅸", "🄸"],
        "j": ["🅙", "🅹", "🄹"],
        "k": ["🅚", "🅺", "🄺"],
        "l": ["🅛", "🅻", "🄻"],
        "m": ["🅜", "🅼", "🄼"],
        "n": ["🅝", "🅽", "🄽"],
        "o": ["🅞", "🅾️", "🄾"],
        "p": ["🅟", "🅿️", "🄿"],
        "q": ["🅠", "🆀", "🅀"],
        "r": ["🅡", "🆁", "🅁"],
        "s": ["🅢", "🆂", "🅂"],
        "t": ["🅣", "🆃", "🅃"],
        "u": ["🅤", "🆄", "🅄"],
        "v": ["🅥", "🆅", "🅅"],
        "w": ["🅦", "🆆", "🅆"],
        "x": ["🅧", "🆇", "🅇"],
        "y": ["🅨", "🆈", "🅈"],
        "z": ["🅩", "🆉", "🅉"],
    }

    def __init__(self, config: Optional[EmojiConfig] = None):
        self.cfg = config or EmojiConfig()

    def mutate(self, prompt: str) -> Optional[str]:
        rng = random.Random(self.cfg.seed)
        prob = max(0.0, min(1.0, float(self.cfg.probability)))

        out_chars: List[str] = []
        for ch in prompt:
            base = ch.lower()
            if base in self.emoji_dict and rng.random() <= prob:
                out_chars.append(rng.choice(self.emoji_dict[base]))
            else:
                out_chars.append(ch)
        return "".join(out_chars)
