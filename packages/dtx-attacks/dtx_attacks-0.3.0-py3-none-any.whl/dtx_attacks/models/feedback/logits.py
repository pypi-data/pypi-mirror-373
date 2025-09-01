from __future__ import annotations

import gc
from typing import List, Union

from dtx_attacks.base.gates import require_deps, torch

require_deps("torch")


class LogitsFeedback:
    @staticmethod
    @torch.no_grad()
    def get_logits_with_control_tokens(
        model,
        input_ids: torch.Tensor,
        test_controls: Union[torch.Tensor, List[str]],
        control_slice: slice,
        tokenizer=None,
        return_ids: bool = False,
    ):
        """
        Replace the control region of `input_ids[control_slice]` with each candidate
        control sequence and run the model in a single batched forward pass.

        Args:
            model: HF-style causal LM with .to(device) and forward(input_ids, attention_mask)
            input_ids: (seq_len,) Long tensor (single example) on any device
            test_controls: Either:
               - Tensor[batch, control_len] Long
               - Tensor[control_len] Long
               - List[str] (will be tokenized; requires `tokenizer`)
            control_slice: slice covering the control tokens to replace (start:stop)
            tokenizer: HF tokenizer; required if `test_controls` is List[str]
            return_ids: If True, also return the batched input ids

        Returns:
            logits: Tensor[batch, seq_len, vocab]
            (optionally) ids: Tensor[batch, seq_len]
        """
        device = next(model.parameters()).device if hasattr(model, "parameters") else getattr(model, "device", "cpu")
        seq_len = int(input_ids.shape[0])
        ctrl_len = int(control_slice.stop - control_slice.start)
        if ctrl_len <= 0:
            raise ValueError(f"Invalid control_slice {control_slice} for seq_len={seq_len}")

        # --- Normalize candidates into a 2D Long tensor [B, ctrl_len]
        pad_tok: int = -1  # <0 means: no padding mask required
        if isinstance(test_controls, torch.Tensor):
            test_ids = test_controls
            if test_ids.ndim == 1:
                test_ids = test_ids.unsqueeze(0)
            if test_ids.size(1) != ctrl_len:
                raise ValueError(f"Tensor controls must have length {ctrl_len}, got {list(test_ids.shape)}")
            test_ids = test_ids.to(device=device, dtype=torch.long)

        elif isinstance(test_controls, list):
            if len(test_controls) == 0:
                raise ValueError("test_controls is an empty list.")
            if tokenizer is None:
                raise ValueError("tokenizer is required when test_controls is a list of strings.")

            # tokenize & truncate to ctrl_len
            enc_ids: List[List[int]] = []
            for s in test_controls:
                ids = tokenizer(s, add_special_tokens=False).input_ids[:ctrl_len]
                # right-pad to ctrl_len (with temporary pad_tok placeholder)
                enc_ids.append(ids)

            # choose a temporary padding id that doesn't collide with existing ids
            # start from 0 and go up until it's absent everywhere
            pad_tok = 0
            base_ids_set = set(input_ids.tolist())
            while (pad_tok in base_ids_set) or any(pad_tok in row for row in enc_ids):
                pad_tok += 1

            # build [B, ctrl_len] tensor filled with pad_tok, then copy real ids
            test_ids = torch.full(
                (len(enc_ids), ctrl_len), pad_tok, dtype=torch.long, device=device
            )
            for i, row in enumerate(enc_ids):
                if not row:
                    continue
                trunc = row[:ctrl_len]
                test_ids[i, :len(trunc)] = torch.tensor(trunc, dtype=torch.long, device=device)

        else:
            raise ValueError(f"Unsupported test_controls type: {type(test_controls)}")

        # --- Construct the batched ids by scattering the control region
        input_ids = input_ids.to(device=device, dtype=torch.long)
        batch = test_ids.size(0)
        ids = input_ids.unsqueeze(0).repeat(batch, 1)  # [B, seq_len]

        # indices for the control slice
        locs = torch.arange(control_slice.start, control_slice.stop, device=device, dtype=torch.long)
        locs = locs.unsqueeze(0).repeat(batch, 1)  # [B, ctrl_len]

        ids = torch.scatter(ids, dim=1, index=locs, src=test_ids)

        # Attention mask if we introduced a pad token
        if pad_tok >= 0:
            attention_mask = (ids != pad_tok).long()
        else:
            attention_mask = None

        # --- Forward
        out = model(input_ids=ids, attention_mask=attention_mask)
        logits = out.logits  # [B, seq_len, vocab]

        # Best-effort cleanup (esp. for CUDA)
        del out, locs, test_ids
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        if return_ids:
            return logits, ids
        return logits
