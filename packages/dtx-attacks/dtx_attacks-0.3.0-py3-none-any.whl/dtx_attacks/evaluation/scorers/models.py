from __future__ import annotations
from typing import Any, List

from dataclasses import dataclass
from typing import Optional, Union

from .base import ModelBackend, ChatMessage


# Optional config containers
@dataclass
class HFConfig:
    model_path: str
    tokenizer_path: Optional[str] = None
    device: Union[str, "torch.device"] = "cuda:0"
    torch_dtype: Optional[str] = "bfloat16"  # "float16" | "bfloat16" | None
    trust_remote_code: bool = True


@dataclass
class OpenAIConfig:
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


# --- Helper: minimal chat->prompt adapter when tokenizer lacks a template ----
def _fallback_apply_chat_template(messages: List[ChatMessage]) -> str:
    """Fallback for models without a native chat template.

    Produces a simple conversation transcript that many instruct models accept.
    Adjust here per model family if needed.
    """
    lines: List[str] = []
    for m in messages:
        role = m["role"]
        if role == "system":
            lines.append("[SYSTEM]\n" + m["content"].strip() + "\n")
        elif role == "user":
            lines.append("[USER]\n" + m["content"].strip() + "\n")
        else:  # assistant
            lines.append("[ASSISTANT]\n" + m["content"].strip() + "\n")
    # Add a generation cue
    lines.append("[ASSISTANT]\n")
    return "\n".join(lines)


class HFTransformersBackend(ModelBackend):
    def __init__(self, cfg: HFConfig):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._torch = torch
        self._device = torch.device(cfg.device) if torch.cuda.is_available() else torch.device("cpu")

        tokenizer_path = cfg.tokenizer_path or cfg.model_path
        self._tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path, trust_remote_code=cfg.trust_remote_code
        )

        dtype = None
        if cfg.torch_dtype == "float16":
            dtype = torch.float16
        elif cfg.torch_dtype == "bfloat16":
            dtype = torch.bfloat16

        self._model = AutoModelForCausalLM.from_pretrained(
            cfg.model_path,
            trust_remote_code=cfg.trust_remote_code,
            torch_dtype=dtype,
        ).to(self._device).eval()

        # Ensure pad token id for batched generate
        if self._tokenizer.pad_token_id is None:
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

    def _render_prompt(self, messages: List[ChatMessage]) -> str:
        # Prefer tokenizer-native chat template if available
        apply = getattr(self._tokenizer, "apply_chat_template", None)
        if callable(apply):
            try:
                return apply(messages, tokenize=False, add_generation_prompt=True)  # type: ignore
            except Exception:
                pass
        # Fallback to a simple bracketed format
        return _fallback_apply_chat_template(messages)

    def generate_messages(
        self,
        messages: List[ChatMessage],
        *,
        max_new_tokens: int = 1,
        do_sample: bool = False,
        **gen_kwargs: Any,
    ) -> str:
        prompt = self._render_prompt(messages)
        torch = self._torch
        with torch.no_grad():
            inputs = self._tokenizer([prompt], return_tensors="pt", padding=True)
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            # Respect common sampling kwargs if provided
            temperature = gen_kwargs.get("temperature", 1.0 if do_sample else 0.0)
            top_p = gen_kwargs.get("top_p", 1.0)
            output_ids = self._model.generate(
                **inputs,
                do_sample=do_sample,
                temperature=temperature,
                top_p=top_p,
                max_new_tokens=max_new_tokens,
                pad_token_id=self._tokenizer.pad_token_id,
                eos_token_id=self._tokenizer.eos_token_id,
            )
            gen_only = output_ids[:, inputs["input_ids"].shape[1]:]
            return self._tokenizer.decode(gen_only[0], skip_special_tokens=True).strip()


class OpenAIChatBackend(ModelBackend):
    def __init__(self, cfg: OpenAIConfig):
        from openai import OpenAI
        self._client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url) if (cfg.api_key or cfg.base_url) else OpenAI()
        self._model = cfg.model

    def generate_messages(
        self,
        messages: List[ChatMessage],
        *,
        max_new_tokens: int = 1,
        do_sample: bool = False,
        **gen_kwargs: Any,
    ) -> str:
        # Map do_sample/temperature into OpenAI params
        temperature = gen_kwargs.get("temperature", 0.7 if do_sample else 0.0)
        top_p = gen_kwargs.get("top_p", 1.0)

        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # OpenAI-format messages
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            **{k: v for k, v in gen_kwargs.items() if k not in {"temperature", "top_p"}},
        )
        return (resp.choices[0].message.content or "").strip()
