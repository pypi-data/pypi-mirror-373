# gradients.py

from types import SimpleNamespace
import gc

from dtx_attacks.base.gates import require_deps, torch, nn   # optional deps, safe to import
from .model_utils import (
    prepare_labels,
    prepare_input_embeddings,
    forward_with_batches,
    get_embeddings,
    get_embedding_matrix,
)

@require_deps("torch", "transformers")
def _model_device(model):
    """Get the device of the first model parameter (robust if model.device is absent)."""
    try:
        return next(model.parameters()).device
    except StopIteration:
        # Fallback if the model has no parameters (unlikely)
        return torch.device("cpu")


@require_deps("torch", "transformers")
def token_gradients(model, input_ids, input_slice, target_slice, loss_slice):
    """
    Compute gradients of the CE loss w.r.t. the tokens in `input_slice`.

    Parameters
    ----------
    model : transformers.PreTrainedModel
        The (causal) LM.
    input_ids : torch.LongTensor [seq_len]
        Full token id sequence.
    input_slice : slice
        Region of `input_ids` we treat as controllable tokens.
    target_slice : slice
        Region used as CE targets.
    loss_slice : slice
        Region of logits to score against `target_slice`.

    Returns
    -------
    torch.Tensor [len(input_slice), vocab_size]
        Gradients of each control token's one-hot vector (per-token over vocab).
    """
    device = _model_device(model)
    model_was_training = model.training
    model.eval()  # typical for gradient-based attribution

    embed_weights = get_embedding_matrix(model)  # [vocab, dim]
    embed_weights = embed_weights.to(device)
    input_ids = input_ids.to(device)

    # Build one-hot for the control region (requires_grad=True)
    control_ids = input_ids[input_slice]  # [L_ctrl]
    vocab_size = embed_weights.size(0)

    one_hot = torch.zeros(
        control_ids.shape[0], vocab_size,
        device=device, dtype=embed_weights.dtype
    )
    one_hot.scatter_(
        1,
        control_ids.unsqueeze(1),
        torch.ones(control_ids.shape[0], 1, device=device, dtype=embed_weights.dtype)
    )
    one_hot.requires_grad_(True)

    # Turn one-hot into embeddings, shape [1, L_ctrl, D]
    control_embeds = (one_hot @ embed_weights).unsqueeze(0)

    # Stitch with the rest of the input embeddings
    with torch.no_grad():
        base_embeds = get_embeddings(model, input_ids.unsqueeze(0))  # [1, L, D]

    full_embeds = torch.cat(
        [base_embeds[:, :input_slice.start, :],
         control_embeds,
         base_embeds[:, input_slice.stop:, :]],
        dim=1
    )

    # Forward, compute CE loss over selected region
    out = model(inputs_embeds=full_embeds, return_dict=True)
    logits = out.logits  # [1, L, V]

    targets = input_ids[target_slice]               # [L_loss]
    logits_slice = logits[0, loss_slice, :]         # [L_loss, V]

    if logits_slice.size(0) != targets.size(0):
        raise ValueError(
            f"Mismatch between logits_slice length ({logits_slice.size(0)}) "
            f"and targets length ({targets.size(0)}). "
            f"loss_slice={loss_slice}, target_slice={target_slice}"
        )

    loss = nn.CrossEntropyLoss()(logits_slice, targets)
    model.zero_grad(set_to_none=True)
    loss.backward()

    # Return gradient of one_hot (per-control-token × vocab)
    grad = one_hot.grad.clone()

    # Cleanup
    del out, logits, loss, base_embeds, control_embeds, full_embeds
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    gc.collect()

    if model_was_training:
        model.train()

    return grad


class GradientFeedback:
    @staticmethod
    @require_deps("torch", "transformers")
    def get_grad_of_control_tokens(
        model,
        input_ids,
        control_slice,
        target_slice,
        loss_slice=None,
    ):
        """
        Convenience wrapper around `token_gradients` that defaults loss_slice
        to the targets shifted by -1 (causal LM convention).
        """
        device = _model_device(model)
        input_ids = input_ids.to(device)
        if loss_slice is None:
            loss_slice = slice(target_slice.start - 1, target_slice.stop - 1)
        return token_gradients(
            model=model,
            input_ids=input_ids,
            input_slice=control_slice,
            target_slice=target_slice,
            loss_slice=loss_slice,
        )

    @staticmethod
    @require_deps("torch", "transformers")
    def compute_one_hot_gradient(
        model,
        embedding_matrix,
        prompt_with_output_encoded,
        output_indices,
        adv_indices,
        attention_mask=None,
        batch_size=None,
    ):
        """
        Builds differentiable one-hot vectors for `adv_indices`, runs a forward
        pass (batched, OOM-friendly) and backprops to obtain gradients on the
        one-hots. Returns both the one-hot tensor (with .grad populated) and
        model outputs.

        Args
        ----
        model : transformers.PreTrainedModel
        embedding_matrix : torch.Tensor [vocab, dim]
        prompt_with_output_encoded : torch.LongTensor [B, L]
        output_indices : list[int] or 1D tensor
        adv_indices : list[int] or 1D tensor
        attention_mask : torch.LongTensor [B, L], optional
        batch_size : int, optional (for forward_with_batches)

        Returns
        -------
        SimpleNamespace(one_hot=Tensor, outputs=dict)
        """
        device = _model_device(model)
        model_was_training = model.training
        model.eval()

        # Labels mask: only score positions in `output_indices`
        labels = prepare_labels(
            prompt_with_output_encoded.to(device),
            output_indices,
            ignore_index=-100,
        )

        # Differentiable one-hot + stitched input embeddings
        one_hot, input_embeddings = prepare_input_embeddings(
            prompt_with_output_encoded.to(device),
            embedding_matrix.to(device),
            adv_indices,
        )

        # Forward (batched) with backprop to populate one_hot.grad
        outputs = forward_with_batches(
            model=model,
            input_embeddings=input_embeddings,
            labels=labels,
            attention_mask=attention_mask.to(device) if attention_mask is not None else None,
            do_backward=True,
            batch_size=batch_size,
        )

        # Cleanup
        if device.type == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()

        if model_was_training:
            model.train()

        return SimpleNamespace(
            one_hot=one_hot,   # gradient lives on one_hot.grad
            outputs=outputs,   # {"logits": ...}
        )
