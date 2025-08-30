from __future__ import annotations

from typing import Optional, Sequence, Tuple

from dtx_attacks.base.gates import require_deps, torch

require_deps("torch")

import gc
from types import SimpleNamespace
from torch import nn

# Lazy-import the heavy utils inside the functions to avoid hard import-time deps.
# If you prefer eager imports, move these to the top:
# from aisafetylab.utils import foward_with_separated_losses as _forward_sep_losses
# from aisafetylab.utils import foward_with_separated_losses_advprompter as _forward_sep_losses_adv


def _maybe_empty_cache() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


def _cat_past_key_values(pkv_chunks: Sequence[Tuple[Tuple[torch.Tensor, ...], ...]]) -> Optional[Tuple[Tuple[torch.Tensor, ...], ...]]:
    """
    pkv_chunks: list over chunks
      each element is a PKV for one chunk:
        tuple over layers -> tuple over kv tensors (e.g., (k, v) or more), each [B_chunk, ...]
    Returns the same structure with tensors concatenated on batch dim (dim=0).
    """
    if not pkv_chunks:
        return None

    n_layers = len(pkv_chunks[0])
    out_layers: list[Tuple[torch.Tensor, ...]] = []
    for l in range(n_layers):
        n_items = len(pkv_chunks[0][l])  # K/V or more
        cat_items = []
        for i in range(n_items):
            cat_items.append(torch.cat([pkv_chunks[c][l][i] for c in range(len(pkv_chunks))], dim=0))
        out_layers.append(tuple(cat_items))
    return tuple(out_layers)


class LossFeedback:
    @staticmethod
    def get_sliced_loss(
        logits: torch.Tensor,
        ids: torch.Tensor,
        target_slice: slice,
        loss_slice: Optional[slice] = None,
    ) -> torch.Tensor:
        """
        Compute token-wise CE loss on a slice of the sequence.

        logits: [B, T, V]
        ids:    [B, T]
        target_slice: tokens aligned with logits[..., 1:, :] convention (use loss_slice for shift)
        loss_slice: by default, shift(target_slice) to the left by 1, i.e. [start-1:stop-1]
        """
        if loss_slice is None:
            loss_slice = slice(target_slice.start - 1, target_slice.stop - 1)

        crit = nn.CrossEntropyLoss(reduction="none")
        # CE expects [B, V, T]; we slice on T then transpose
        sliced_logits = logits[:, loss_slice, :].transpose(1, 2)  # [B, V, T_slice]
        sliced_ids = ids[:, target_slice]                          # [B, T_slice]
        return crit(sliced_logits, sliced_ids)

    @staticmethod
    def compute_separated_losses(
        model,
        prompt_with_output_encoded: torch.Tensor,  # [B, T]
        output_indices: Sequence[int],
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor, ...], ...]] = None,
        *,
        chunk_size: int = 100,
        show_progress: bool = True,
    ) -> SimpleNamespace:
        """
        Batch-forward in chunks producing per-sequence losses computed only at `output_indices`.

        Returns:
            SimpleNamespace(
                loss:  [B] tensor (mean over selected positions per sequence),
                past_key_values: concatenated PKV across chunks or None,
                logits: [B, T, V]
            )
        """
        # Lazy imports to reduce hard deps
        from aisafetylab.utils import foward_with_separated_losses as _forward_sep_losses

        device = next(model.parameters()).device if hasattr(model, "parameters") else getattr(model, "device", "cpu")

        if attention_mask is None:
            attention_mask = torch.ones_like(prompt_with_output_encoded, device=device, dtype=torch.long)

        pkv_in = past_key_values
        past_input_length = pkv_in[0][0].shape[2] if pkv_in is not None else 0

        # Use model embeddings directly, drop the prefill positions (handled via PKV)
        embed_weight = model.get_input_embeddings().weight
        input_embeddings = embed_weight[prompt_with_output_encoded[..., past_input_length:]]  # [B, T', D]

        # Labels: pass full ids; the separation fn does its own shift/slicing
        labels = prompt_with_output_encoded

        # Loop in chunks
        rng = range(0, input_embeddings.shape[0], chunk_size)
        if show_progress:
            try:
                from tqdm import trange
                rng = trange(0, input_embeddings.shape[0], chunk_size, desc="Loss chunks")
            except Exception:
                pass

        all_losses: list[float] = []
        all_logits: list[torch.Tensor] = []
        pkv_chunks: list = []

        for start in rng:
            end = start + chunk_size
            input_chunk = input_embeddings[start:end]
            labels_chunk = labels[start:end]
            attn_chunk = attention_mask[start:end]
            pkv_chunk_in = None
            if pkv_in is not None:
                # for each layer, pick batch slice for k/v (and potential others)
                pkv_chunk_in = tuple(tuple(kv[start:end] for kv in layer) for layer in pkv_in)

            res = _forward_sep_losses(
                model=model,
                input_embeddings_chunk=input_chunk,
                labels_chunk=labels_chunk,
                output_indices=list(output_indices),
                attention_mask_chunk=attn_chunk,
                past_key_values_chunk=pkv_chunk_in,
            )

            # res.loss: [B_chunk]
            all_losses.extend(res.loss.tolist())
            all_logits.append(res.logits)
            if getattr(res, "past_key_values", None) is not None:
                pkv_chunks.append(res.past_key_values)

            # Cleanup
            del input_chunk, labels_chunk, attn_chunk, pkv_chunk_in, res
            _maybe_empty_cache()

        # Concatenate outputs
        logits = torch.cat(all_logits, dim=0)
        new_pkv = _cat_past_key_values(pkv_chunks) if pkv_chunks else None

        return SimpleNamespace(
            loss=torch.tensor(all_losses, device=logits.device),
            past_key_values=new_pkv,
            logits=logits,
        )


class LossFeedbackAdvprompter:
    @staticmethod
    def compute_separated_losses_advprompter(
        model,
        prompt_with_output_encoded: torch.Tensor,  # [B, T]
        output_indices: Sequence[int],
        attention_mask: torch.Tensor,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor, ...], ...]] = None,
        *,
        suffix_indices: Optional[Sequence[int]] = None,
        chunk_size: int = 100,
        show_progress: bool = True,
    ) -> SimpleNamespace:
        """
        Same as compute_separated_losses but uses the advprompter variant that
        (optionally) applies suffix-regularization and 1/t token weights.
        """
        from aisafetylab.utils import foward_with_separated_losses_advprompter as _forward_sep_losses_adv

        device = next(model.parameters()).device if hasattr(model, "parameters") else getattr(model, "device", "cpu")

        pkv_in = past_key_values
        past_input_length = pkv_in[0][0].shape[2] if pkv_in is not None else 0

        embed_weight = model.get_input_embeddings().weight
        input_embeddings = embed_weight[prompt_with_output_encoded[..., past_input_length:]]

        labels = prompt_with_output_encoded

        rng = range(0, input_embeddings.shape[0], chunk_size)
        if show_progress:
            try:
                from tqdm import trange
                rng = trange(0, input_embeddings.shape[0], chunk_size, desc="Loss chunks (adv)")
            except Exception:
                pass

        all_losses: list[float] = []
        all_logits: list[torch.Tensor] = []
        pkv_chunks: list = []

        for start in rng:
            end = start + chunk_size
            input_chunk = input_embeddings[start:end]
            labels_chunk = labels[start:end]
            attn_chunk = attention_mask[start:end]
            pkv_chunk_in = None
            if pkv_in is not None:
                pkv_chunk_in = tuple(tuple(kv[start:end] for kv in layer) for layer in pkv_in)

            res = _forward_sep_losses_adv(
                model=model,
                input_embeddings_chunk=input_chunk,
                labels_chunk=labels_chunk,
                output_indices=list(output_indices),
                attention_mask_chunk=attn_chunk,
                past_key_values_chunk=pkv_chunk_in,
                suffix_indices=None if suffix_indices is None else list(suffix_indices),
            )

            all_losses.extend(res.loss.tolist())
            all_logits.append(res.logits)
            if getattr(res, "past_key_values", None) is not None:
                pkv_chunks.append(res.past_key_values)

            del input_chunk, labels_chunk, attn_chunk, pkv_chunk_in, res
            _maybe_empty_cache()

        logits = torch.cat(all_logits, dim=0)
        new_pkv = _cat_past_key_values(pkv_chunks) if pkv_chunks else None

        return SimpleNamespace(
            loss=torch.tensor(all_losses, device=logits.device),
            past_key_values=new_past_key_values if (new_pkv := _cat_past_key_values(pkv_chunks)) else None,  # type: ignore[name-defined]
            logits=logits,
        )
