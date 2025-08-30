import random
import string
from typing import Optional, Callable, List, Protocol


# ---- internal: RNG-aware primitives -----------------------------------------
class _RND(Protocol):
    def random(self) -> float: ...
    def choice(self, seq): ...
    def shuffle(self, x) -> None: ...


def _character_scrambling(text: str, *, rnd: _RND, sigma: float) -> str:
    """
    Scramble interior letters of words (len>3) with probability p ~ sigma**0.5.
    """
    p = max(0.0, min(1.0, sigma ** 0.5))
    def scramble_word(word: str) -> str:
        if len(word) > 3 and rnd.random() < p:
            mid = list(word[1:-1])
            rnd.shuffle(mid)
            return word[0] + "".join(mid) + word[-1]
        return word
    return " ".join(scramble_word(w) for w in text.split())


def _random_capitalization(text: str, *, rnd: _RND, sigma: float) -> str:
    """
    Flip case on characters with probability p ~ sigma**0.5.
    """
    p = max(0.0, min(1.0, sigma ** 0.5))
    out = []
    for ch in text:
        if ch.isalpha() and rnd.random() < p:
            out.append(ch.upper() if ch.islower() else ch.lower())
        else:
            out.append(ch)
    return "".join(out)


def _character_noising(text: str, *, rnd: _RND, sigma: float) -> str:
    """
    Small ASCII perturbations with probability p ~ sigma**3 on printable chars.
    Preserves readability by +/-1 codepoint within printable range.
    """
    p = max(0.0, min(1.0, sigma ** 3))
    out = []
    for ch in text:
        if ch.isprintable() and rnd.random() < p:
            delta = rnd.choice([-1, 1])
            code = ord(ch) + delta
            out.append(chr(code) if 32 <= code <= 126 else ch)
        else:
            out.append(ch)
    return "".join(out)


# ---- public: legacy, non-RNG helpers (kept for compatibility) ----------------
def character_scrambling(text: str, scramble_prob: float = 0.6) -> str:
    rnd = random
    def scramble_word(word: str) -> str:
        if len(word) > 3 and rnd.random() < scramble_prob:
            middle = list(word[1:-1])
            rnd.shuffle(middle)
            return word[0] + ''.join(middle) + word[-1]
        return word
    return ' '.join(scramble_word(w) for w in text.split())


def random_capitalization(text: str, cap_prob: float = 0.6) -> str:
    rnd = random
    return ''.join(ch.upper() if rnd.random() < cap_prob else ch.lower() for ch in text)


def character_noising(text: str, noise_prob: float = 0.06, seed: Optional[int] = None) -> str:
    if not 0 <= noise_prob <= 1:
        raise ValueError("noise_prob must be between 0 and 1")
    rnd = random.Random(seed) if seed is not None else random
    def alter_char(ch: str) -> str:
        if not ch.isalpha():
            return ch
        charset = string.ascii_uppercase if ch.isupper() else string.ascii_lowercase
        if rnd.random() >= noise_prob:
            return ch
        idx = charset.index(ch)
        return rnd.choice([charset[(idx - 1) % len(charset)], charset[(idx + 1) % len(charset)]])
    return ''.join(alter_char(c) for c in text)


# ---- recommended: seeded, sigma-controlled closures for BON ------------------
def make_safe_augs(sigma: float = 0.4, seed: Optional[int] = None) -> List[Callable[[str], str]]:
    """
    Returns a list of (str)->str augmenters that close over a deterministic RNG and sigma.
    This keeps your BON runner simple: you can call each function directly on the prompt.

    Args:
        sigma: overall augmentation strength (typ. 0.2–0.6). Internally:
               - scramble & random caps use p = sigma**0.5
               - ascii noising uses p = sigma**3 (rarer to preserve readability)
        seed:  optional base seed for determinism

    Example:
        SAFE_AUGS = make_safe_augs(sigma=0.4, seed=1234)
        augmented = SAFE_AUGS[0]("some text")
    """
    base_rnd = random.Random(seed) if seed is not None else random

    def with_fixed_rng(fn):
        # each call uses an independent child RNG derived from base_rnd for stability
        def wrapped(text: str) -> str:
            # derive a per-call seed so repeated runs are reproducible but distinct
            child_seed = base_rnd.getrandbits(64)
            rnd = random.Random(child_seed)
            return fn(text, rnd=rnd, sigma=sigma)
        return wrapped

    return [
        with_fixed_rng(_character_scrambling),
        with_fixed_rng(_random_capitalization),
        with_fixed_rng(_character_noising),
    ]


# Default SAFE_AUGS for convenience (sigma=0.4, no fixed seed)
SAFE_AUGS: List[Callable[[str], str]] = make_safe_augs(sigma=0.4, seed=None)

__all__ = [
    # legacy helpers
    "character_scrambling", "random_capitalization", "character_noising",
    # recommended BON usage
    "make_safe_augs", "SAFE_AUGS",
]
