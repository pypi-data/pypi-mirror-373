# pip install litellm tqdm loguru
from __future__ import annotations

import re
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger
import time

import litellm
from litellm import (
    completion,
    batch_completion,
    batch_completion_models,
    batch_completion_models_all_responses,
)

from .base import Model

Message = Dict[str, str]
Messages = List[Message]
BatchMessages = List[Union[str, Messages]]

# ---------------- Provider / capability helpers ---------------- #

def _detect_provider(model_name: str) -> Tuple[str, str]:
    """
    Returns (provider, bare_model).
    E.g. "groq/deepseek-r1-distill-llama-70b" -> ("groq", "deepseek-r1-distill-llama-70b")
         "openai/gpt-4o-mini-2024-07-18"     -> ("openai", "gpt-4o-mini-2024-07-18")
         "gpt-4o-mini"                        -> ("openai", "gpt-4o-mini")  # default
    """
    if "/" in model_name:
        provider, bare = model_name.split("/", 1)
        return provider.lower(), bare
    # Bare names: assume OpenAI-compatible unless wrapped elsewhere.
    return "openai", model_name


def _supports_logprobs(model_name: str) -> bool:
    """
    Central switch for logprobs support.
    Extend with allow/deny lists as needed.
    """
    provider, _ = _detect_provider(model_name)
    # As of now, Groq's OpenAI-compatible API rejects `logprobs`.
    if provider == "groq":
        return False
    return True


def _mentions_logprobs_error(err: BaseException) -> bool:
    s = str(err).lower()
    return ("logprobs" in s) or ("top_logprobs" in s)


def _extract_logprobs_from_response(r: litellm.ModelResponse) -> Optional[list]:
    """
    Litellm response structures can vary; treat logprobs as optional.
    Returns a list[dict[token -> logprob]] per generated token, or None.
    """
    try:
        lp_obj = getattr(r.choices[0], "logprobs", None)
        if not lp_obj:
            return None
        content = getattr(lp_obj, "content", None)
        if not content:
            return None
        out = []
        for tok in content:
            tops = getattr(tok, "top_logprobs", None) or []
            out.append({t.token: t.logprob for t in tops})
        return out
    except Exception:
        return None


# ---------------- The model ---------------- #

class LiteLLMModel(Model):
    def __init__(
        self,
        model_name: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.generation_config = dict(generation_config or {})

        # knobs
        self.API_RETRY_SLEEP = 10
        self.API_ERROR_OUTPUT = "$ERROR$"
        self.API_QUERY_SLEEP = 0.5
        self.API_MAX_RETRY = 5
        self.API_TIMEOUT = 20
        self.API_LOGPROBS = True
        self.API_TOP_LOGPROBS = 20

        # Provider-derived capability flags
        self._provider, _ = _detect_provider(self.model_name)
        if not _supports_logprobs(self.model_name):
            self.API_LOGPROBS = False  # clamp default if provider doesn't support it

        self.generation_config.setdefault("request_timeout", self.API_TIMEOUT)
        self._system_message: Optional[str] = None

    def set_system_message(self, system_message: str):
        self._system_message = system_message

    def _prepare_messages(self, messages: Union[str, Messages]) -> Messages:
        if isinstance(messages, str):
            msgs: Messages = [{"role": "user", "content": messages}]
        else:
            msgs = messages
        if self._system_message:
            if not msgs or msgs[0].get("role") != "system":
                msgs = [{"role": "system", "content": self._system_message}] + msgs
        return msgs

    def _merge_cfg(self, want_logprobs: Optional[bool] = None, **kwargs) -> Dict[str, Any]:
        """
        Merge base generation_config with per-call kwargs.
        Respect provider capability for logprobs and allow per-call override via want_logprobs.
        """
        cfg = self.generation_config.copy()
        if kwargs:
            cfg.update(kwargs)

        # Decide whether to request logprobs
        can_lp = _supports_logprobs(self.model_name)
        default_lp = self.API_LOGPROBS and can_lp
        req_lp = default_lp if want_logprobs is None else (want_logprobs and can_lp)

        if req_lp:
            cfg["logprobs"] = True
            cfg.setdefault("top_logprobs", self.API_TOP_LOGPROBS)
        else:
            cfg.pop("logprobs", None)
            cfg.pop("top_logprobs", None)

        return cfg

    def _completion_with_logprobs_fallback(
        self, *, messages: Messages, cfg: Dict[str, Any]
    ) -> litellm.ModelResponse:
        """
        Calls `completion`, and if an error mentions logprobs, retries once without it.
        """
        try:
            return completion(
                model=self.model_name,
                messages=messages,
                api_base=self.base_url,
                api_key=self.api_key,
                **cfg,
            )
        except Exception as e:
            if _mentions_logprobs_error(e) and cfg.get("logprobs"):
                # strip and retry once
                stripped = dict(cfg)
                stripped.pop("logprobs", None)
                stripped.pop("top_logprobs", None)
                return completion(
                    model=self.model_name,
                    messages=messages,
                    api_base=self.base_url,
                    api_key=self.api_key,
                    **stripped,
                )
            raise

    def _batch_completion_with_logprobs_fallback(
        self, *, batched_messages: List[Messages], cfg: Dict[str, Any]
    ) -> List[litellm.ModelResponse]:
        """
        Calls `batch_completion`, retrying once without logprobs if needed.
        """
        try:
            return batch_completion(
                model=self.model_name,
                messages=batched_messages,
                api_base=self.base_url,
                api_key=self.api_key,
                **cfg,
            )
        except Exception as e:
            if _mentions_logprobs_error(e) and cfg.get("logprobs"):
                stripped = dict(cfg)
                stripped.pop("logprobs", None)
                stripped.pop("top_logprobs", None)
                return batch_completion(
                    model=self.model_name,
                    messages=batched_messages,
                    api_base=self.base_url,
                    api_key=self.api_key,
                    **stripped,
                )
            raise

    def _chat_once(self, messages: Messages, **kwargs) -> litellm.ModelResponse:
        cfg = self._merge_cfg(**kwargs)
        return self._completion_with_logprobs_fallback(messages=messages, cfg=cfg)

    # -------- single call ----------
    def generate(
        self,
        messages: Union[str, Messages],
        clear_old_history: bool = True,
        max_try: int = 30,
        try_gap: int = 5,
        gap_increase: int = 5,
        **kwargs,
    ) -> str:
        processed = self._prepare_messages(messages)
        cur = 0
        sleep_gap = try_gap
        last_err: Optional[BaseException] = None

        while cur < max_try:
            try:
                resp = self._chat_once(processed, **kwargs)
                content = resp.choices[0].message.get("content")
                if not content:
                    raise RuntimeError("Empty response content")
                return content
            except Exception as e:
                last_err = e
                logger.error(f"[LiteLLMModel.generate] try {cur+1}/{max_try} error: {e}")
                cur += 1
                if cur < max_try:
                    time.sleep(sleep_gap)
                    sleep_gap += gap_increase
        raise RuntimeError("Failed to generate response") from last_err

    def chat(self, messages, clear_old_history=True, max_try=30, try_gap=5, **kwargs):
        return self.generate(messages, clear_old_history, max_try, try_gap, **kwargs)

    def generate_clean(
        self,
        messages: Union[str, Messages],
        **kwargs,
    ) -> str:
        """
        Runs a generation, then strips out any <think>...</think> tags and returns the cleaned text.
        """
        raw = self.generate(messages, **kwargs)
        # remove everything between <think> and </think>
        cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        return cleaned.strip()


    # -------- native LiteLLM batching (many -> one model) ----------
    def batch_chat(
        self,
        batch_messages: BatchMessages,
        clear_old_history: bool = True,
        max_try: int = 5,
        try_gap: int = 3,
        max_workers: int = 10,       # kept for signature parity; not used
        show_progress: bool = True,  # kept for signature parity; not used
        **kwargs,
    ) -> List[str]:
        """
        Uses litellm.batch_completion to process multiple prompts for ONE model in a single call.
        """
        if not batch_messages:
            return []

        # Normalize to List[List[{"role":..., "content":...}]]
        batched: List[Messages] = [self._prepare_messages(m) for m in batch_messages]

        cfg = self._merge_cfg(**kwargs)

        # Retry the WHOLE batch if needed (simplest + most efficient)
        for attempt in range(1, max_try + 1):
            try:
                responses = self._batch_completion_with_logprobs_fallback(
                    batched_messages=batched, cfg=cfg
                )
                outputs: List[str] = []
                for i, r in enumerate(responses):
                    try:
                        outputs.append(r.choices[0].message.get("content", "") or "")
                    except Exception as e:
                        logger.error(f"[LiteLLMModel.batch_chat] parse error at idx {i}: {e}")
                        outputs.append(f"ERROR: {e}")
                return outputs
            except Exception as e:
                logger.error(f"[LiteLLMModel.batch_chat] attempt {attempt}/{max_try} failed: {e}")
                if attempt < max_try:
                    time.sleep(try_gap)
                else:
                    # as a fallback, degrade to per-item calls to salvage results
                    logger.warning("[LiteLLMModel.batch_chat] falling back to per-item calls")
                    return [
                        self.chat(m, clear_old_history, max_try=30, try_gap=try_gap, **kwargs)
                        for m in batch_messages
                    ]

    # -------- multi-model helpers (one prompt -> many models) ----------
    def chat_fastest_across_models(
        self,
        models: List[str],
        messages: Union[str, Messages],
        **kwargs,
    ) -> str:
        """
        Race multiple models and return the FIRST response.
        Note: we cannot easily retry-without-logprobs per model here; instead, clamp cfg.
        """
        processed = self._prepare_messages(messages)
        cfg = self._merge_cfg(**kwargs)
        # For cross-model, safest is to avoid logprobs entirely to reduce incompat errors.
        cfg.pop("logprobs", None)
        cfg.pop("top_logprobs", None)

        resp = batch_completion_models(
            models=models,
            messages=processed,
            api_base=self.base_url,   # LiteLLM can still use env-specific keys per provider
            api_key=self.api_key,
            **cfg,
        )
        return resp.choices[0].message.get("content", "") or ""

    def chat_all_across_models(
        self,
        models: List[str],
        messages: Union[str, Messages],
        **kwargs,
    ) -> List[str]:
        """
        Call multiple models in parallel and return ALL responses (as strings).
        """
        processed = self._prepare_messages(messages)
        cfg = self._merge_cfg(**kwargs)
        # Same rationale: cross-provider, strip logprobs to avoid unsupported-parameter failures.
        cfg.pop("logprobs", None)
        cfg.pop("top_logprobs", None)

        resps = batch_completion_models_all_responses(
            models=models,
            messages=processed,
            api_base=self.base_url,
            api_key=self.api_key,
            **cfg,
        )
        return [r.choices[0].message.get("content", "") or "" for r in resps]

    # -------- vectorized get_response using batch_completion ----------
    def get_response(
        self,
        prompts_list: List[Union[str, Messages]],
        max_n_tokens: Optional[int] = None,
        no_template: bool = False,
        gen_config: Dict[str, Any] = {},
    ) -> List[Any]:
        # normalize to messages-per-item
        if isinstance(prompts_list[0], str):
            convs: List[Messages] = [[{"role": "user", "content": p}] for p in prompts_list]  # type: ignore
        else:
            convs = prompts_list  # type: ignore

        convs = [self._prepare_messages(c) for c in convs]

        cfg = self._merge_cfg(**gen_config)
        if max_n_tokens is not None:
            cfg["max_tokens"] = max_n_tokens

        # Try one-shot batch (with logprobs fallback)
        try:
            resps = self._batch_completion_with_logprobs_fallback(
                batched_messages=convs, cfg=cfg
            )
            outs = []
            for r in resps:
                usage = getattr(r, "usage", None)
                outs.append({
                    "text": r.choices[0].message.get("content", ""),
                    "logprobs": _extract_logprobs_from_response(r),
                    "n_input_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
                    "n_output_tokens": getattr(usage, "completion_tokens", None) if usage else None,
                })
            return outs
        except Exception as e:
            logger.error(f"[LiteLLMModel.get_response] batch error: {e}")

        # Fallback: per-item with retries (parity with your original behavior)
        outputs: List[Any] = []
        for conv in convs:
            output: Any = self.API_ERROR_OUTPUT
            for _ in range(self.API_MAX_RETRY):
                try:
                    r = self._chat_once(conv, **cfg)
                    usage = getattr(r, "usage", None)
                    output = {
                        "text": r.choices[0].message.get("content", ""),
                        "logprobs": _extract_logprobs_from_response(r),
                        "n_input_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
                        "n_output_tokens": getattr(usage, "completion_tokens", None) if usage else None,
                    }
                    break
                except Exception as e2:
                    logger.error(f"[LiteLLMModel.get_response] single error: {e2}")
                    time.sleep(self.API_RETRY_SLEEP)
                time.sleep(self.API_QUERY_SLEEP)
            outputs.append(output)
        return outputs
