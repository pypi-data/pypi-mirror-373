from time import time
import random
from typing import Tuple

# Optional deps via gates
from dtx_attacks.base.gates import require_deps, torch 

# Numpy is light; keep direct import
import numpy as np

# Make wandb optional (no-op logger if not installed)
try:
    import wandb  # type: ignore
    _HAVE_WANDB = True
except Exception:  # pragma: no cover
    _HAVE_WANDB = False

    class _WandbStub:
        @staticmethod
        def log(*args, **kwargs):
            pass

    wandb = _WandbStub()  # type: ignore


class Timer:
    def __init__(self, t: float):
        self.last_time = t

    @staticmethod
    def start() -> "Timer":
        return Timer(time())

    def end(self) -> float:
        t = self.last_time
        self.last_time = time()
        return time() - t


def schedule_n_to_change_fixed(max_n_to_change: int, it: int) -> int:
    """Piece-wise constant schedule for n_to_change (chars/tokens)."""
    if 0 < it <= 10:
        n_to_change = max_n_to_change
    elif 10 < it <= 25:
        n_to_change = max_n_to_change // 2
    elif 25 < it <= 50:
        n_to_change = max_n_to_change // 4
    elif 50 < it <= 100:
        n_to_change = max_n_to_change // 8
    elif 100 < it <= 500:
        n_to_change = max_n_to_change // 16
    else:
        n_to_change = max_n_to_change // 32
    return max(n_to_change, 1)


def schedule_n_to_change_prob(max_n_to_change: int, prob: float, target_model) -> int:
    """
    Piece-wise constant schedule for n_to_change based on best prob.
    Adjusted for tougher families like LLaMA/R2D2 (heuristic).
    """
    model_name = getattr(target_model, "model_name", "") or ""
    name = model_name.lower()

    if "llama" in name or "r2d2" in name:
        if 0 <= prob <= 0.01:
            n_to_change = max_n_to_change // 2
        elif 0.01 < prob <= 0.1:
            n_to_change = max_n_to_change // 4
        elif 0.1 < prob <= 1.0:
            n_to_change = max_n_to_change // 8
        else:
            raise ValueError(f"Wrong prob {prob}")
    else:
        if 0 <= prob <= 0.01:
            n_to_change = max_n_to_change
        elif 0.01 < prob <= 0.1:
            n_to_change = max_n_to_change // 2
        elif 0.1 < prob <= 1.0:
            n_to_change = max_n_to_change // 4
        else:
            raise ValueError(f"Wrong prob {prob}")

    return max(n_to_change, 1)


def extract_logprob(logprob_dict: dict, target_token: str) -> float:
    logprobs = []
    prefixed = " " + target_token
    if prefixed in logprob_dict:
        logprobs.append(logprob_dict[prefixed])
    if target_token in logprob_dict:
        logprobs.append(logprob_dict[target_token])
    return -np.inf if not logprobs else max(logprobs)


def early_stopping_condition(
    best_logprobs,
    target_model,
    logprob_dict,
    target_token,
    determinstic_jailbreak: bool,
    no_improvement_history: int = 750,
    prob_start: float = 0.02,
    no_improvement_threshold_prob: float = 0.01,
) -> bool:
    # Deterministic check: if argmax token is the target, stop.
    if determinstic_jailbreak and logprob_dict:
        argmax_token = max(logprob_dict, key=logprob_dict.get)
        return argmax_token in (target_token, " " + target_token)

    if len(best_logprobs) == 0:
        return False

    best_logprob = best_logprobs[-1]

    if no_improvement_history < len(best_logprobs):
        prob_best = np.exp(best_logprobs[-1])
        prob_history = np.exp(best_logprobs[-no_improvement_history])
        no_sufficient_improvement = (prob_best - prob_history) < no_improvement_threshold_prob
    else:
        no_sufficient_improvement = False

    if np.exp(best_logprob) > prob_start and no_sufficient_improvement:
        return True
    if np.exp(best_logprob) > 0.1:
        return True
    # For other models: conservative higher threshold
    if np.exp(best_logprob) > 0.4:
        return True
    return False


@require_deps("torch")
def get_batch_topK_indices(tensor, topK: int = 10) -> Tuple["torch.Tensor", "torch.Tensor"]:
    """
    Top-K over the last two dims collapsed: [B, S, V] -> per-row over S*V.
    Returns (topk_values [B,K], original_indices [B,K,2=(row,col)]).
    """
    K = int(topK)
    if K <= 0:
        raise ValueError("topK must be positive")

    B, S, V = tensor.size()
    flattened = tensor.view(B, -1)
    topk_values, topk_indices = torch.topk(flattened, k=K, dim=1)

    rows = torch.div(topk_indices, V, rounding_mode="floor")
    cols = topk_indices % V
    original_indices = torch.stack((rows, cols), dim=2)  # [B,K,2]
    return topk_values, original_indices


@require_deps("torch")
def get_variants(
    prompt_with_output_encoded,
    adv_indices,
    topk_indices,
    topk_values,  # kept for API parity; not used as weights currently
    replace_size: int,
    beam_size: int,
):
    """
    Create variants by substituting tokens at adv_indices with Top-K choices.
    Returns a stacked tensor of shape [B*beam_size, len(adv_indices)].
    """
    variants_list = []
    tensor = prompt_with_output_encoded[..., adv_indices]  # [B, L_adv]
    B, L_adv = tensor.shape

    for b in range(B):
        base = tensor[b]
        b_indices = topk_indices[b]  # [K,2] with (row, col) over L_adv × vocab
        # We only need the candidate token ids (cols)
        cand_rows = b_indices[:, 0]
        cand_cols = b_indices[:, 1]

        for _ in range(int(beam_size)):
            variant = base.clone()
            sampled = random.choices(range(len(b_indices)), k=int(replace_size))
            for idx in sampled:
                pos = cand_rows[idx].item()
                tok = cand_cols[idx].item()
                if 0 <= pos < L_adv:
                    variant[pos] = tok
            variants_list.append(variant)

    return torch.stack(variants_list)


@require_deps("torch")
def random_topk_substitute(
    signal,
    original,
    num_sub_positions: int = 10,
    topK: int = 20,
    beam_size: int = 10
):
    """
    Hierarchical substitution using per-position Top-K from `signal`.
    `original` is [B, L_adv] containing only adv tokens.
    Returns [B*beam_size, L_adv].
    """
    topk = torch.topk(signal, dim=-1, k=int(topK))
    topk_indices = topk.indices  # [B, L_adv, topK]

    variants = []
    for batch_tensor, batch_topk in zip(original, topk_indices):
        L_adv = batch_tensor.shape[0]
        for _ in range(int(beam_size)):
            positions = random.choices(range(L_adv), k=int(num_sub_positions))
            v = batch_tensor.clone()
            for pos in positions:
                candidates = batch_topk[pos]  # [topK]
                v[pos] = random.choice(candidates.tolist())
            variants.append(v)
    return torch.stack(variants)


def hit_rate_at_n(jb_stat: np.ndarray, n: int) -> float:
    jb_sum_at_n = np.sum(jb_stat[:, :n], axis=1)
    return np.where(jb_sum_at_n > 0, 1.0, jb_sum_at_n).mean()


def add_dummy_dim_to_slice(slice_obj):
    """
    Insert None-dims after any integer index in a (possibly tuple) slice,
    to simulate adding new axes during tensor indexing.
    """
    if not isinstance(slice_obj, tuple):
        slice_obj = (slice_obj,)

    new_slice = []
    for sl in slice_obj:
        if isinstance(sl, int):
            new_slice.append(sl)
            new_slice.append(None)
        else:
            new_slice.append(sl)
    return tuple(new_slice)


def list_avg(_list):
    return sum(_list) / max(len(_list), 1)


def check_jailbroken(seq, test_prefixes):
    jailbroken_list = [all(prefix not in text for prefix in test_prefixes) for text in seq.text]
    return list_avg(jailbroken_list), jailbroken_list


def check_affirmative(seq, affirmative_prefixes):
    affirmative_list = [
        any(text[: len(prefix)].lower() == prefix.lower() for prefix in affirmative_prefixes)
        for text in seq.text
    ]
    return list_avg(affirmative_list), affirmative_list


def check_success(seq, target_seq):
    success_list = [target_seq.text[i].lower() in text.lower() for i, text in enumerate(seq.text)]
    return list_avg(success_list), success_list


class Metrics:
    def __init__(self, prefix: str = ""):
        self.metrics = {}
        self.prefix = prefix

    def log(self, key, value, step=None, log_to_wandb: bool = False):
        key = f"{self.prefix}{key}"
        self.metrics.setdefault(key, []).append(value)
        if log_to_wandb and _HAVE_WANDB:
            assert step is not None
            wandb.log({key: value}, step=step)

    def get_combined(self, fn, prefix: str = "", step=None, log_to_wandb: bool = False):
        out = {f"{prefix}{k}": fn(vs) for k, vs in self.metrics.items()}
        if log_to_wandb and _HAVE_WANDB:
            assert step is not None
            wandb.log(out, step=step)
        return out

    def get_avg(self, prefix: str = "avg/", step=None, log_to_wandb: bool = False):
        return self.get_combined(list_avg, prefix=prefix, step=step, log_to_wandb=log_to_wandb)

    def get_max(self, prefix: str = "max/", step=None, log_to_wandb: bool = False):
        return self.get_combined(max, prefix=prefix, step=step, log_to_wandb=log_to_wandb)

    def get_min(self, prefix: str = "min/", step=None, log_to_wandb: bool = False):
        return self.get_combined(min, prefix=prefix, step=step, log_to_wandb=log_to_wandb)

    def log_dict(self, metrics_dict, step=None, log_to_wandb: bool = False):
        for k, v in metrics_dict.items():
            self.log(k, v, step=step, log_to_wandb=log_to_wandb)

    def reset(self):
        self.metrics = {}
