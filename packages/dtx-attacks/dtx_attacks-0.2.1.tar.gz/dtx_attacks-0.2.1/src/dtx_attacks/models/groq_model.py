from .litellm_model import LiteLLMModel
from typing import Dict, Any, Optional


def _ensure_groq_model_name(name: str) -> str:
    # don't touch fully-qualified names or ones already prefixed
    if "/" in name:
        return name
    if name.startswith("groq/"):
        return name
    return f"groq/{name}"

class GroqAIModel(LiteLLMModel):
    """
    Accepts bare OpenAI model names (e.g., 'gpt-4o-mini') and prefixes 'openai/'.
    """
    def __init__(
        self,
        model_name: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            model_name=_ensure_groq_model_name(model_name),
            base_url=base_url,
            api_key=api_key,
            generation_config=generation_config,
        )
