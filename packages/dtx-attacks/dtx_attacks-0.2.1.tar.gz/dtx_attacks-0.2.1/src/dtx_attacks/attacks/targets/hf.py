from __future__ import annotations
from typing import Optional, Any
from typing import Dict

from dtx_attacks.base.gates import (
    require_deps,
    MissingDependencyError,
    torch,
    AutoModelForCausalLM,
    AutoTokenizer,
)
from dtx_attacks.models import load_model  # returns LocalModel wrapper

from .base import WhiteboxTargetModel, GenerationConfig, PromptLike


class HFTargetModel(WhiteboxTargetModel):
    """
    Whitebox Target that CONSTRUCTs its own HF model + tokenizer from names/paths.

    It wraps the created pair with your project’s LocalModel via `load_model(...)`,
    and exposes the whitebox contract (model/tokenizer/device/conversation/generate).
    """

    @require_deps("transformers", "torch")
    def __init__(
        self,
        *,
        model_name_or_path: str,
        tokenizer_name_or_path: Optional[str] = None,
        model_display_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        device: Optional[str] = None,
        torch_dtype: str = "float16",
        trust_remote_code: bool = True,
        vllm_mode: bool = False,
        generation_config: Optional[dict] = None,
    ) -> None:
        # --- build raw HF objects ---
        if AutoModelForCausalLM is None or AutoTokenizer is None:
            raise MissingDependencyError("transformers not installed. Try: pip install transformers")

        dtype = getattr(torch, torch_dtype) if isinstance(torch_dtype, str) else torch_dtype
        _device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        base_model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            torch_dtype=dtype,
        ).eval().to(_device)

        tok = AutoTokenizer.from_pretrained(
            tokenizer_name_or_path or model_name_or_path,
            padding_side="left",
            trust_remote_code=trust_remote_code,
        )
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
            tok.pad_token_id = tok.eos_token_id

        # --- wrap with project LocalModel via load_model ---
        self._wrapper = load_model(
            model=base_model,
            tokenizer=tok,
            model_display_name=model_display_name,
            generation_config=generation_config,
            model_path=None,
            tokenizer_path=None,
            device=_device,
            vllm_mode=vllm_mode,
        )

        self._sys = system_prompt or "You are a helpful, safe assistant."
        self._tok = tok
        self._conv = getattr(self._wrapper, "conversation", None)

    # -------- Whitebox contract --------
    @property
    def model(self) -> Any:
        return getattr(self._wrapper, "model")

    @property
    def tokenizer(self) -> Any:
        return self._tok

    @property
    def device(self) -> Any:
        # LocalModel already computes device
        return getattr(self._wrapper, "device", "cpu")

    @property
    def conversation(self) -> Any:
        return self._conv

    def _genconfig_to_dict(self, cfg: Optional[GenerationConfig]) -> Optional[Dict[str, Any]]:
        """
        Convert project GenerationConfig -> dict expected by LocalModel.generate.
        Uses HF-style names (max_new_tokens, temperature, top_p). Includes 'stop' and any 'extra'.
        """
        if cfg is None:
            return None
        as_dict: Dict[str, Any] = {
            "max_new_tokens": cfg.max_new_tokens,
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
        }
        if cfg.stop is not None:
            as_dict["stop"] = cfg.stop
        # Merge any extras, without clobbering the required keys unless explicitly provided
        if cfg.extra:
            as_dict.update(dict(cfg.extra))
        return as_dict

    def generate(
        self,
        input_ids,
        config: Optional[GenerationConfig] = None,
        *,
        batch: bool = False,
    ):
        """
        Generate tokens from input_ids. If a project GenerationConfig is provided, convert it
        to a dict and pass through to the LocalModel.generate. Otherwise, defer to defaults.
        """
        # NB: per your request, we *pass a dict* to the local model if config is provided.
        gen_cfg_dict = self._genconfig_to_dict(config)

        # Surface a clear error in vLLM mode (LocalModel.generate doesn't implement batch=True either)
        if getattr(self._wrapper, "vllm_mode", False):
            raise NotImplementedError("generate(input_ids=...) is not supported in vLLM mode; use chat()/batch_chat().")

        if gen_cfg_dict is None:
            return self._wrapper.generate(input_ids, batch=batch)

        return self._wrapper.generate(input_ids, gen_config=gen_cfg_dict, batch=batch)

    # Optional: make query() forward the same GenerationConfig cleanly
    def query(self, prompt: PromptLike, config: Optional[GenerationConfig] = None) -> str:
        text = self._to_text(prompt)
        gen = config or GenerationConfig()

        if hasattr(self._wrapper, "generate_text"):
            # If your LocalModel.generate_text accepts OpenAI-style names, reuse openai_format()
            return self._wrapper.generate_text(
                text,
                **gen.openai_format(include_none=False)
            ).strip()

        input_ids = self._tok(text, return_tensors="pt").input_ids.to(self.device)
        output_ids = self.generate(input_ids, config=gen)
        decoded = self._tok.decode(output_ids, skip_special_tokens=True)
        return decoded.strip()

    # -------- TargetModel API --------
    @property
    def name(self) -> str:
        return (
            getattr(self._wrapper, "model_display_name", None)
            or getattr(self._wrapper, "name", None)
            or getattr(self._wrapper, "model_name", "hf/local")
        )

    def reset(self) -> None:
        pass
