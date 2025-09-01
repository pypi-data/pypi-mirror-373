from .local_model import LocalModel

def load_model(model=None, tokenizer=None, model_display_name=None, generation_config=None, model_path=None, tokenizer_path=None, device=None, vllm_mode=False):
    return LocalModel(model, tokenizer, model_display_name, generation_config, model_path, tokenizer_path, device, vllm_mode)
    