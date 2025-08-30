from loguru import logger
from tqdm import trange
import gc
import numpy as np

# --- Optional deps via gates (safe, lazy failure) -----------------------------
from dtx_attacks.base.gates import (
    require_deps,
    MissingDependencyError,
    torch,
    AutoModelForCausalLM,
    AutoTokenizer,
)

from typing import Any, Dict, Tuple, Optional
try:
    from transformers import GenerationConfig as HFGenerationConfig  # optional import
except Exception:
    HFGenerationConfig = None

# Optional: vLLM
try:
    from vllm import SamplingParams as _SamplingParams  # type: ignore
    from vllm import LLM as _VLLM  # type: ignore
    _HAVE_VLLM = True
except Exception:  # pragma: no cover
    _SamplingParams = None
    _VLLM = None
    _HAVE_VLLM = False

# Optional: FastChat template
try:
    from fastchat.conversation import get_conv_template as _get_conv_template  # type: ignore
    _HAVE_FASTCHAT = True
except Exception:  # pragma: no cover
    _HAVE_FASTCHAT = False
    def _get_conv_template(name: str):
        raise MissingDependencyError(
            "Conversation templates require fastchat. Try: pip install 'fschat[model_worker]'"
        )

from .base import Model


# --- Minimal HF conversation adapter ---------------------------------
from types import SimpleNamespace

class _HFConversationAdapter:
    """
    Lightweight adapter that offers a FastChat-like API:
    - .roles (tuple[str, str])
    - .messages (list[dict(role, content)])
    - .append_message(role, content)
    - .update_last_message(content)
    - .get_prompt()
    - .copy()
    - .set_system_message(text)
    Also exposes .name, .sep, .sep2, and .template.roles for compatibility.
    """
    def __init__(self, tokenizer, roles=("user", "assistant"), name="hf_tokenizer"):
        self.tokenizer = tokenizer
        self.roles = tuple(roles)
        self.name = name
        self.messages = []
        self.sep = "\n"
        self.sep2 = "\n"
        self.system_message = None
        self.template = SimpleNamespace(roles=list(self.roles))

    def set_system_message(self, text: str):
        self.system_message = text

    def append_message(self, role, content):
        role = role if role in self.roles else str(role)
        self.messages.append({"role": role, "content": content})

    def update_last_message(self, content):
        if not self.messages:
            raise IndexError("No messages to update.")
        self.messages[-1]["content"] = content

    def get_prompt(self):
        msgs = []
        if self.system_message:
            msgs.append({"role": "system", "content": self.system_message})
        # Replace None with "" so apply_chat_template can still render a prefix
        msgs.extend({"role": m["role"], "content": (m["content"] or "")} for m in self.messages)
        try:
            return self.tokenizer.apply_chat_template(msgs, tokenize=False)
        except Exception:
            # Plain fallback if tokenizer lacks a chat_template
            parts = []
            if self.system_message:
                parts.append(f"System: {self.system_message}")
            for m in msgs:
                label = "User" if m["role"] == self.roles[0] else "Assistant"
                parts.append(f"{label}: {m['content']}")
            return "\n".join(parts)

    def copy(self):
        new = _HFConversationAdapter(self.tokenizer, self.roles, self.name)
        new.sep = self.sep
        new.sep2 = self.sep2
        new.system_message = self.system_message
        new.messages = [dict(m) for m in self.messages]
        return new


class LocalModel(Model):
    def __init__(
        self,
        model=None,
        tokenizer=None,
        model_display_name=None,
        generation_config=None,
        model_path=None,
        tokenizer_path=None,
        device=None,
        vllm_mode=False,
    ):
        # ----- Model ----------------------------------------------------------
        self.vllm_mode = bool(vllm_mode)
        logger.info(f"Using VLLM mode: {self.vllm_mode}")

        if model is not None:
            self.model = model
        else:
            assert model_path is not None, "model_path must be provided if model is not given"
            if self.vllm_mode:
                if not _HAVE_VLLM:
                    raise MissingDependencyError("vLLM not installed. Try: pip install vllm")
                self.model = _VLLM(model_path, device=device) if device is not None else _VLLM(model_path)
            else:
                if AutoModelForCausalLM is None:
                    raise MissingDependencyError("transformers not installed. Try: pip install transformers")
                mdl = AutoModelForCausalLM.from_pretrained(model_path)
                if device is None:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = mdl.to(device).eval()

        # ----- Tokenizer ------------------------------------------------------
        if tokenizer is not None:
            self.tokenizer = tokenizer
        else:
            if AutoTokenizer is None:
                raise MissingDependencyError("transformers not installed. Try: pip install transformers")
            if tokenizer_path is None:
                tokenizer_path = model_path
                logger.warning("tokenizer_path is not provided, using model_path as tokenizer_path")
            self.tokenizer = AutoTokenizer.from_pretrained(
                tokenizer_path,
                padding_side="left",
                trust_remote_code=True,
            )

        # ----- Name / device / misc ------------------------------------------
        self.model_display_name = model_display_name or getattr(self.model, "name_or_path", "unknown")
        if getattr(self.tokenizer, "pad_token", None) is None:
            logger.warning("tokenizer.pad_token is None, setting pad_token to eos_token")
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.pos_to_token_dict = {v: k.replace("▁", " ") for k, v in self.tokenizer.get_vocab().items()}
        self.eos_token_ids = [self.tokenizer.eos_token_id]
        self.pad_token_id = self.tokenizer.pad_token_id

        # ----- Conversation template (FastChat -> HF chat_template -> minimal) -----
        self.conversation = None
        try:
            _model_display_name = self.model_display_name
            if isinstance(_model_display_name, str) and "vicuna" in _model_display_name:
                _model_display_name = "vicuna_v1.1"
            if _HAVE_FASTCHAT:
                self.conversation = _get_conv_template(_model_display_name)
        except Exception:
            logger.warning("FastChat template unavailable; will try tokenizer chat_template.")

        if not self.conversation:
            if getattr(self.tokenizer, "chat_template", None):
                logger.info("Using tokenizer.chat_template via HF conversation adapter.")
                self.conversation = _HFConversationAdapter(self.tokenizer, name="hf_tokenizer")
            else:
                logger.warning("No FastChat template or tokenizer.chat_template; using minimal fallback conversation.")
                self.conversation = _HFConversationAdapter(self.tokenizer, name="fallback_template")

        # Minor compatibility tweaks (only if the attributes exist)
        if self.conversation and self.model_display_name == "llama-2" and hasattr(self.conversation, "sep2"):
            self.conversation.sep2 = (self.conversation.sep2 or "").strip()

        if self.conversation and self.model_display_name == "zero_shot" and hasattr(self.conversation, "template"):
            # Keep this safe for adapters
            try:
                self.conversation.roles = tuple(['### ' + r for r in self.conversation.template.roles])
                if hasattr(self.conversation, "sep"):
                    self.conversation.sep = "\n"
            except Exception:
                pass

        logger.debug(f"Conversation template in use: {getattr(self.conversation, 'name', '<none>')}")
                
        # Generation params (transformers or vLLM)
        if not self.vllm_mode:
            self.generation_config = generation_config or {}
        else:
            if not _HAVE_VLLM:
                raise MissingDependencyError("vLLM not installed. Try: pip install vllm")
            if generation_config is None:
                self.generation_config = _SamplingParams()
            elif isinstance(generation_config, _SamplingParams):
                self.generation_config = generation_config
            else:
                generation_config = self.transfer_generation_config_to_vllm(generation_config)
                self.generation_config = _SamplingParams(**generation_config)

        # Device
        if device:
            self.device = device
        else:
            if not self.vllm_mode:
                self.device = next(self.model.parameters()).device
            else:
                # vLLM internal device
                self.device = self.model.llm_engine.device_config.device

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def transfer_generation_config_to_vllm(self, generation_config):
        if not _HAVE_VLLM:
            raise MissingDependencyError("vLLM not installed. Try: pip install vllm")
        removed_keys = {"do_sample"}
        change_name_keys = {"max_new_tokens": "max_tokens"}
        new_cfg = {}
        for k, v in generation_config.items():
            if k == "top_k" and v == 0:
                new_cfg["top_k"] = -1
            elif k in removed_keys:
                continue
            elif k in change_name_keys:
                new_cfg[change_name_keys[k]] = v
            else:
                new_cfg[k] = v
        return new_cfg

    def set_system_message(self, system_message: str):
        if self.conversation is not None:
            self.conversation.system_message = system_message

    # -------------------------------------------------------------------------
    # Inference (transformers path)
    # -------------------------------------------------------------------------
    @require_deps("torch", "transformers")
    def get_response(self, prompts_list, max_n_tokens=None, no_template=False):
        """
        :param prompts_list: list[str] or list[list[chat dict]]
        :param max_n_tokens: int
        :param no_template: if False, prompts_list are used as-is; if True, apply chat template
        :return: list[dict]
        """
        if not no_template:
            full_prompts = prompts_list
        else:
            full_prompts = []
            for prompt in prompts_list:
                full_prompt = self.apply_chat_template(prompt)
                full_prompts.append(full_prompt)

        full_prompts_list = full_prompts
        if isinstance(self.model_display_name, str) and "llama" in self.model_display_name.lower():
            # +1 to account for the first special token for some LLaMA checkpoints
            if max_n_tokens is not None:
                max_n_tokens += 1

        batch_size = len(full_prompts_list)
        vocab_size = len(self.tokenizer.get_vocab())

        inputs = self.tokenizer(full_prompts_list, return_tensors="pt", padding=True).to(self.device)
        input_ids = inputs["input_ids"]

        output = self.model.generate(
            **inputs,
            max_new_tokens=max_n_tokens,
            do_sample=False,
            eos_token_id=self.tokenizer.eos_token_id,   # fixed (singular)
            pad_token_id=self.tokenizer.pad_token_id,
            output_scores=True,
            return_dict_in_generate=True,
            # apply ctor baseline kwargs if dict
            **(self.generation_config if isinstance(self.generation_config, dict) else {}),
        )
        
        output_ids = output.sequences
        if not self.model.config.is_encoder_decoder:
            output_ids = output_ids[:, input_ids.shape[1]:]
        if isinstance(self.model_display_name, str) and "llama2" in self.model_display_name.lower():
            output_ids = output_ids[:, 1:]

        generated_texts = self.tokenizer.batch_decode(output_ids)
        logprobs_tokens = [
            torch.nn.functional.log_softmax(output.scores[i_out], dim=-1).cpu().numpy()
            for i_out in range(len(output.scores))
        ]
        if isinstance(self.model_display_name, str) and "llama2" in self.model_display_name.lower():
            logprobs_tokens = logprobs_tokens[1:]

        logprob_dicts = [
            [
                {self.pos_to_token_dict[i_vocab]: logprobs_tokens[i_out][i_b][i_vocab]
                 for i_vocab in range(vocab_size)}
                for i_out in range(len(logprobs_tokens))
            ]
            for i_b in range(batch_size)
        ]

        outputs = [
            {
                "text": generated_texts[i_b],
                "logprobs": logprob_dicts[i_b],
                "n_input_tokens": int((input_ids[i_b] != 0).sum().item()),
                "n_output_tokens": int(output_ids[i_b].shape[0]),
            }
            for i_b in range(batch_size)
        ]

        for key in inputs:
            inputs[key] = inputs[key].to("cpu")
        output_ids = output_ids.to("cpu")
        del inputs, output_ids
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        return outputs

    def _normalize_gen_args(
        self,
        gen_config: Optional[Any] = None,
        **overrides: Any,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns (fixed_kwargs, passthrough_kwargs) for transformers.generate.

        - If gen_config is an HF GenerationConfig, pass via 'generation_config='.
        - If gen_config is a dict, expand it as kwargs (NOT via generation_config=).
        - If gen_config is None, only baseline + overrides are used.
        - Baseline comes from self.generation_config if it's a dict.
        - Strips unsupported keys like 'stop'.
        """
        fixed: Dict[str, Any] = {}
        kw: Dict[str, Any] = {}

        # baseline from ctor if dict
        base = {}
        if isinstance(self.generation_config, dict):
            base.update(self.generation_config)

        if gen_config is not None and HFGenerationConfig is not None and isinstance(gen_config, HFGenerationConfig):
            fixed["generation_config"] = gen_config
            kw.update(base)
            kw.update(overrides or {})
        elif isinstance(gen_config, dict):
            kw.update(base)
            kw.update(gen_config)
            kw.update(overrides or {})
        else:
            kw.update(base)
            kw.update(overrides or {})

        # transformers.generate doesn't accept 'stop' kwarg
        kw.pop("stop", None)
        return fixed, kw

    @require_deps("torch", "transformers")
    def generate(self, input_ids, gen_config=None, batch=False, **overrides):
        input_ids = input_ids.to(self.model.device)
        if batch:
            raise NotImplementedError

        attn_masks = torch.ones_like(input_ids).to(self.model.device)
        pad_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id

        fixed_kwargs, passthrough = self._normalize_gen_args(gen_config, **overrides)

        with torch.no_grad():
            out = self.model.generate(
                input_ids=input_ids,
                attention_mask=attn_masks,
                pad_token_id=pad_id,
                **fixed_kwargs,   # generation_config=... only if HF object
                **passthrough,    # dict-style cfg (max_new_tokens, temperature, top_p, etc.)
            )
        return out[0][input_ids.size(1):]

    # -------------------------------------------------------------------------
    # Prompt building
    # -------------------------------------------------------------------------
    def apply_chat_template(self, messages, force_prefill=False):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        prefill = (messages[-1]["role"] == "assistant") or force_prefill

        # Prefer tokenizer's own chat template when available
        try:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=not prefill,
            )
        except Exception:
            # Fallback: fastchat template (if present), else naive concat
            if self.conversation is not None:
                conversation = self.conversation.copy()
                if messages[-1]["role"] != "assistant":
                    messages.append({"role": "assistant", "content": None})
                if messages and messages[0]["role"] == "system":
                    conversation.set_system_message(messages[0]["content"])
                    messages = messages[1:]
                for msg in messages:
                    conversation.append_message(msg["role"], msg["content"])
                prompt = conversation.get_prompt()
                if conversation.name == "vicuna_v1.1":
                    prompt = prompt.replace("user:", "User:").replace("assistant:", "ASSISTANT:")
            else:
                # minimalistic: "<role>: <content>\n"
                parts = []
                for m in messages:
                    parts.append(f"{m['role']}: {m['content'] if m['content'] is not None else ''}")
                prompt = "\n".join(parts)

        # BOS handling
        if self.tokenizer.bos_token and prompt.startswith(self.tokenizer.bos_token):
            prompt = prompt.replace(self.tokenizer.bos_token, "", 1)
        if self.tokenizer.bos_token and not prompt.startswith(self.tokenizer.bos_token):
            prompt = self.tokenizer.bos_token + prompt

        logger.info(f"prompt before check prefill: {prompt}")
        if prefill:
            if self.tokenizer.eos_token and prompt.strip().endswith(self.tokenizer.eos_token):
                idx = prompt.rindex(self.tokenizer.eos_token)
                prompt = prompt[:idx].rstrip()
                logger.info(f"prompt after check prefill: {prompt}")

        return prompt

    @require_deps("torch", "transformers")
    def get_ppl(self, batch_messages):
        ppls = []
        device = self.model.device
        for messages in batch_messages:
            input_text = self.apply_chat_template(messages[:-1])
            output_text = self.apply_chat_template(messages).replace(input_text, "", 1).lstrip()

            inputs = self.tokenizer([input_text], return_tensors="pt", truncation=True, padding=True)
            input_ids = inputs["input_ids"].to(device)
            attention_mask = inputs["attention_mask"].to(device)

            outputs = self.tokenizer([output_text], return_tensors="pt", truncation=True, padding=True, add_special_tokens=False)
            output_ids = outputs["input_ids"].to(device)
            output_attention_mask = outputs["attention_mask"].to(device)

            concat_input_ids = torch.cat([input_ids, output_ids], dim=1)
            concat_attention_mask = torch.cat([attention_mask, output_attention_mask], dim=1)

            labels = concat_input_ids.clone()
            labels[labels == self.tokenizer.pad_token_id] = -100
            labels[:, : input_ids.shape[1]] = -100

            out = self.model(concat_input_ids, attention_mask=concat_attention_mask)
            logits = out.logits
            criterion = torch.nn.CrossEntropyLoss(reduction="none")

            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            shift_logits = shift_logits.permute(0, 2, 1)
            loss = criterion(shift_logits, shift_labels)

            ipt_len = input_ids.size(1)
            loss = loss[0, ipt_len - 1 :]
            ppl = float(np.exp(loss.mean().item()))
            ppls.append(ppl)
        return ppls

    # -------------------------------------------------------------------------
    # Batch chat
    # -------------------------------------------------------------------------
    def batch_chat(
        self,
        batch_messages,
        batch_size=8,
        skip_special_tokens=True,
        use_tqdm=True,
        force_prefill=False,
        **kwargs,
    ):
        prompts = [self.apply_chat_template(m, force_prefill=force_prefill) for m in batch_messages]
        responses = []

        if self.vllm_mode:
            if not _HAVE_VLLM:
                raise MissingDependencyError("vLLM not installed. Try: pip install vllm")

            if "sampling_params" in kwargs:
                temp_generation_config = kwargs["sampling_params"]
            else:
                temp_generation_config = self.generation_config.clone()
                v_kwargs = self.transfer_generation_config_to_vllm(kwargs)
                for k in v_kwargs:
                    if k in self.generation_config.__annotations__.keys():
                        setattr(temp_generation_config, k, v_kwargs[k])

            outputs = self.model.generate(prompts, temp_generation_config, use_tqdm=use_tqdm)
            responses = [out.outputs[0].text for out in outputs]
            return responses

        # transformers path — respect ctor baseline + per-call overrides
        fixed_kwargs, passthrough = self._normalize_gen_args(
            kwargs.get("generation_config"),
            **{k: v for k, v in kwargs.items() if k != "generation_config"}
        )

        rng = trange(0, len(prompts), batch_size) if use_tqdm else range(0, len(prompts), batch_size)
        for i in rng:
            batch_prompts = prompts[i : i + batch_size]
            inputs = self.tokenizer(batch_prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(self.device)
            with torch.no_grad():
                out = self.model.generate(
                    **inputs,
                    **fixed_kwargs,
                    **passthrough,
                )
            for j, input_ids in enumerate(inputs["input_ids"]):
                response = self.tokenizer.decode(out[j][len(input_ids) :], skip_special_tokens=skip_special_tokens)
                responses.append(response)
        return responses

    def chat(self, messages, use_chat_template=True, **kwargs):
        if isinstance(messages, str) and use_chat_template:
            messages = [{"role": "user", "content": messages}]

        prompt = self.apply_chat_template(messages) if use_chat_template else messages

        if self.vllm_mode:
            if not _HAVE_VLLM:
                raise MissingDependencyError("vLLM not installed. Try: pip install vllm")
            if "sampling_params" in kwargs:
                temp_generation_config = kwargs["sampling_params"]
            else:
                temp_generation_config = self.generation_config.clone()
                kwargs = self.transfer_generation_config_to_vllm(kwargs)
                for k in kwargs:
                    if k in self.generation_config.__annotations__.keys():
                        setattr(temp_generation_config, k, kwargs[k])

            outputs = self.model.generate([prompt], temp_generation_config)
            response = outputs[0].outputs[0].text
            logger.debug(f"In LocalModel chat (vLLM). Prompt: {prompt}\nResponse: {response}")
            return response

        # transformers path — normalized cfg handling
        inputs = self.tokenizer([prompt], return_tensors="pt", add_special_tokens=False).to(self.device)
        fixed_kwargs, passthrough = self._normalize_gen_args(
            kwargs.get("generation_config"),
            **{k: v for k, v in kwargs.items() if k != "generation_config"}
        )

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                **fixed_kwargs,
                **passthrough,
            )
        response = self.tokenizer.decode(out[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True)
        return response
