# gates.py
from typing import TYPE_CHECKING, Callable, Any

class MissingDependencyError(RuntimeError):
    pass

def _fmt_missing(*pkgs: str) -> str:
    tips = []
    if "torch" in pkgs:
        tips.append("pip install torch --index-url https://download.pytorch.org/whl/cu121  # or cpu")
    if "transformers" in pkgs:
        tips.append("pip install transformers")
    if "peft" in pkgs:
        tips.append("pip install peft")
    return (
        "This function requires the following missing packages: "
        + ", ".join(pkgs)
        + "\nTry:\n  - " + "\n  - ".join(tips)
    )

def require_deps(*deps: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    need_torch = "torch" in deps
    need_tfmr = "transformers" in deps
    need_peft = "peft" in deps

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args, **kwargs):
            missing = []
            if need_torch and not HAVE_TORCH:
                missing.append("torch")
            if need_tfmr and not HAVE_TRANSFORMERS:
                missing.append("transformers")
            if need_peft and not HAVE_PEFT:
                missing.append("peft")
            if missing:
                raise MissingDependencyError(_fmt_missing(*missing))
            return fn(*args, **kwargs)
        return wrapped
    return deco

# --- Optional multiprocessing (prefer torch.multiprocessing if available) ---
try:
    from torch import multiprocessing as mp  # type: ignore
    HAVE_TORCH_MP = True
except Exception:  # pragma: no cover
    try:
        import multiprocessing as mp  # stdlib fallback
        HAVE_TORCH_MP = False
    except Exception:  # extremely rare
        mp = None  # type: ignore
        HAVE_TORCH_MP = False


# ---- Optional imports with flags (never crash module import) -----------------
try:
    import torch  # type: ignore
    import torch.nn.functional as F  # type: ignore
    import torch.nn as nn  # type: ignore
    HAVE_TORCH = True
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    F = None      # type: ignore
    nn = None     # type: ignore
    HAVE_TORCH = False

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer  # minimal
    HAVE_TRANSFORMERS = True
except Exception:  # pragma: no cover
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    HAVE_TRANSFORMERS = False

def _opt(cls_path: str):
    """Best-effort optional import of a class."""
    mod, name = cls_path.rsplit(".", 1)
    try:
        from importlib import import_module
        return getattr(import_module(mod), name)
    except Exception:
        return None

GPT2LMHeadModel    = _opt("transformers.GPT2LMHeadModel")
GPTJForCausalLM    = _opt("transformers.GPTJForCausalLM")
GPTNeoXForCausalLM = _opt("transformers.GPTNeoXForCausalLM")
LlamaForCausalLM   = _opt("transformers.LlamaForCausalLM")
Qwen2ForCausalLM   = _opt("transformers.Qwen2ForCausalLM")
FalconForCausalLM  = _opt("transformers.FalconForCausalLM")
GemmaForCausalLM   = _opt("transformers.GemmaForCausalLM")
MistralForCausalLM = _opt("transformers.MistralForCausalLM")

# Optional PEFT
try:
    from peft import LoraConfig, PeftModel  # type: ignore
    HAVE_PEFT = True
except Exception:  # pragma: no cover
    LoraConfig = None  # type: ignore
    PeftModel = None   # type: ignore
    HAVE_PEFT = False

# For type checkers only (won’t import at runtime)
if TYPE_CHECKING:
    import torch as _torch
    from transformers import PreTrainedModel as _PTM, PreTrainedTokenizerBase as _Tok
else:
    _torch = Any  # type: ignore
    _PTM = Any    # type: ignore
    _Tok = Any    # type: ignore
