# module_utils.py
from functools import wraps
from types import SimpleNamespace
import gc

from loguru import logger

from dtx_attacks.base.gates import (
    require_deps,
    MissingDependencyError,
    HAVE_TORCH,
    HAVE_PEFT,
    AutoModelForCausalLM,
    AutoTokenizer,
    LoraConfig,
    PeftModel,
    GPT2LMHeadModel,
    GPTJForCausalLM,
)

# Import torch/nn/F guarded via gates
from dtx_attacks.base.gates import torch, F, nn  # type: ignore


# -------------------------------
# Small helpers / safe utilities
# -------------------------------
def _model_type(model) -> str:
    """
    Prefer config.model_type when available; fallback to class-name heuristics.
    """
    mt = getattr(getattr(model, "config", None), "model_type", None)
    if isinstance(mt, str):
        return mt
    name = model.__class__.__name__.lower()
    return (
        "gptj" if "gptj" in name else
        "gpt2" if "gpt2" in name else
        "llama" if "llama" in name else
        "gpt_neox" if "neox" in name else
        "falcon" if "falcon" in name else
        "mistral" if "mistral" in name else
        "gemma" if "gemma" in name else
        "qwen2" if "qwen2" in name else
        "unknown"
    )

def get_developer(model_name: str) -> str:
    r"""
    Guess the model developer/organization from a model name or HF repo id.
    Falls back to "ModelKeeper" when unknown.

    Examples:
      - "llama-2" → "Meta"
      - "meta-llama/Llama-3-8B-Instruct" → "Meta"
      - "vicuna-13b-v1.5" → "LMSYS"
      - "mistralai/Mixtral-8x7B-Instruct-v0.1" → "Mistral AI"
      - "Qwen/Qwen2-7B-Instruct" → "Alibaba (Qwen)"
      - "tiiuae/falcon-40b" → "TII"
      - "google/gemma-7b" → "Google"
      - "EleutherAI/gpt-neox-20b" → "EleutherAI"
      - "mosaicml/mpt-7b" → "MosaicML (Databricks)"
      - "microsoft/phi-2" → "Microsoft"
      - "01-ai/Yi-34B" → "01.AI"
      - "deepseek-ai/deepseek-llm-7b" → "DeepSeek-AI"
      - "bigscience/bloom" → "BigScience"
      - "allenai/OLMo-7B" → "Allen Institute for AI"
      - "baichuan-inc/Baichuan2-13B-Chat" → "Baichuan Inc."
    """
    if not model_name:
        return "ModelKeeper"

    name = str(model_name).strip()
    lower = name.lower()

    # If it's an HF-style "org/model" id, capture org
    org = lower.split("/", 1)[0] if "/" in lower else ""

    # 1) Fast path for known org prefixes
    org_map = {
        "meta-llama": "Meta",
        "meta": "Meta",
        "mistralai": "Mistral AI",
        "qwen": "Alibaba (Qwen)",
        "alibaba": "Alibaba (Qwen)",
        "google": "Google",
        "tiiuae": "TII",
        "eleutherai": "EleutherAI",
        "mosaicml": "MosaicML (Databricks)",
        "databricks": "Databricks",
        "microsoft": "Microsoft",
        "01-ai": "01.AI",
        "deepseek-ai": "DeepSeek-AI",
        "bigscience": "BigScience",
        "allenai": "Allen Institute for AI",
        "baichuan-inc": "Baichuan Inc.",
        "huggingfaceh4": "Hugging Face (H4)",
        "cerebras": "Cerebras",
    }
    if org in org_map:
        return org_map[org]

    # 2) Exact/legacy names
    exact = {
        "llama-2": "Meta",
        "vicuna": "LMSYS",
    }
    if lower in exact:
        return exact[lower]

    # 3) Family/contains patterns (order matters)
    contains = [
        ("llama", "Meta"),
        ("vicuna", "LMSYS"),
        ("alpaca", "Stanford CRFM"),
        ("mistral", "Mistral AI"),
        ("mixtral", "Mistral AI"),
        ("qwen2", "Alibaba (Qwen)"),
        ("qwen", "Alibaba (Qwen)"),
        ("gemma", "Google"),
        ("falcon", "TII"),
        ("mpt", "MosaicML (Databricks)"),
        ("phi", "Microsoft"),
        ("yi", "01.AI"),
        ("deepseek", "DeepSeek-AI"),
        ("bloom", "BigScience"),
        ("olmo", "Allen Institute for AI"),
        ("gpt-neox", "EleutherAI"),
        ("neox", "EleutherAI"),
        ("gpt-j", "EleutherAI"),
        ("gpt-neo", "EleutherAI"),
        ("pythia", "EleutherAI"),
        ("zephyr", "Hugging Face (H4)"),
        ("cerebras", "Cerebras"),
        ("baichuan", "Baichuan Inc."),
    ]
    for key, dev in contains:
        if key in lower:
            return dev

    # 4) Default
    return "ModelKeeper"


# -------------------------------
# Label / Embedding preparation
# -------------------------------
@require_deps("torch")
def prepare_labels(prompt_with_output_encoded, output_indices, ignore_index=-100):
    """Mask non-output tokens with ignore_index; keep only tokens at output_indices."""
    labels_all = prompt_with_output_encoded.clone()
    labels = torch.full_like(labels_all, ignore_index)
    labels[..., output_indices] = labels_all[..., output_indices]
    return labels

@require_deps("torch")
def prepare_input_embeddings(prompt_with_output_encoded, embedding_matrix, adv_indices):
    """
    Replace adversarial positions with one-hot-derived embeddings (keeps grad).
    """
    num_classes = embedding_matrix.size(0)
    input_embeddings = embedding_matrix[prompt_with_output_encoded]
    adv_token_ids = prompt_with_output_encoded[..., adv_indices]  # (B, adv_len)

    one_hot = (
        F.one_hot(adv_token_ids, num_classes=num_classes)
        .to(dtype=embedding_matrix.dtype, device=embedding_matrix.device)
        .clone()
        .detach()
        .requires_grad_(True)
    )
    adv_embeddings = torch.matmul(one_hot, embedding_matrix)  # (B, adv_len, D)
    input_embeddings = input_embeddings.clone()  # avoid in-place on view
    input_embeddings[..., adv_indices, :] = adv_embeddings
    return one_hot, input_embeddings

# -------------------------------
# Memory helpers
# -------------------------------
@require_deps("torch")
def calculate_tensor_size(tensor):
    if isinstance(tensor, torch.Tensor):
        return tensor.numel() * tensor.element_size()
    elif isinstance(tensor, (tuple, list)):
        return sum(calculate_tensor_size(t) for t in tensor)
    elif isinstance(tensor, dict):
        return sum(calculate_tensor_size(v) for v in tensor.values())
    return 0

@require_deps("torch")
def get_total_allocated_memory():
    if not torch.cuda.is_available():
        return 0.0
    devices = torch.cuda.device_count()
    total_allocated_memory = 0
    for i in range(devices):
        total_allocated_memory += torch.cuda.memory_allocated(f"cuda:{i}")
    return total_allocated_memory / 1e9

# -------------------------------
# Batched forward (OOM-friendly)
# -------------------------------
@require_deps("torch", "transformers")
def forward_with_batches(
    model,
    input_ids=None,
    input_embeddings=None,
    labels=None,
    do_backward=False,
    batch_size=None,
    attention_mask=None,
    **kwargs,
):
    """
    Forward with auto-batching; CPU and no-CUDA safe; minimal assumptions.
    """
    device = next(model.parameters()).device
    if input_embeddings is not None:
        input_embeddings = input_embeddings.to(device)
    if labels is not None:
        labels = labels.to(device)
    if input_ids is not None:
        input_ids = input_ids.to(device)
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    # Auto batch-size estimation (CUDA only). CPU: default to 1 if not provided.
    if batch_size is None:
        if device.type == "cuda" and torch.cuda.is_available():
            kwargs0 = dict(return_dict=True, output_hidden_states=False, output_attentions=False)
            if input_embeddings is not None:
                kwargs0["inputs_embeds"] = input_embeddings[:1]
            if input_ids is not None:
                kwargs0["input_ids"] = input_ids[:1]
            if attention_mask is not None:
                kwargs0["attention_mask"] = attention_mask[:1]
            if labels is not None:
                kwargs0["labels"] = labels[:1]
            with torch.inference_mode():
                dummy_output = model(**kwargs0)
            dummy_output_size = calculate_tensor_size(dummy_output)
            props = torch.cuda.get_device_properties(device)
            reserved = torch.cuda.memory_reserved(device)
            available = props.total_memory - reserved
            batch_size = max(1, int(available / max(dummy_output_size, 1) / 16))
        else:
            batch_size = 1

    batch_outputs_logits = []
    tot_len = (input_embeddings.size(0) if input_embeddings is not None else input_ids.size(0))

    for start_idx in range(0, tot_len, batch_size):
        end_idx = start_idx + batch_size
        batch_kwargs = dict(return_dict=True)
        if input_ids is not None:
            batch_kwargs["input_ids"] = input_ids[start_idx:end_idx]
        if input_embeddings is not None:
            batch_kwargs["inputs_embeds"] = input_embeddings[start_idx:end_idx]
        if labels is not None:
            batch_kwargs["labels"] = labels[start_idx:end_idx]
        if attention_mask is not None:
            batch_kwargs["attention_mask"] = attention_mask[start_idx:end_idx]
        batch_kwargs.update(kwargs)

        batch_output = model(**batch_kwargs)
        if do_backward and "loss" in batch_output:
            batch_output["loss"].backward()
        batch_outputs_logits.append(batch_output["logits"].detach())

        del batch_output
        if device.type == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()

    combined_outputs = {"logits": torch.cat(batch_outputs_logits, dim=0)}
    return combined_outputs

# -------------------------------
# Per-position loss helpers
# -------------------------------
@require_deps("torch", "transformers")
def foward_with_separated_losses(
    model,
    input_embeddings_chunk,
    labels_chunk,
    output_indices,
    attention_mask_chunk,
    past_key_values_chunk=None,
):
    print("output_indices", output_indices)
    past_input_length = (past_key_values_chunk[0][0].shape[2] if past_key_values_chunk is not None else 0)
    output_indices = [i - past_input_length for i in output_indices]
    print("past_innput_length", past_input_length)
    print("output_indices", output_indices)
    print("labels_chunk.shape", labels_chunk.shape)
    labels_chunk = labels_chunk[..., past_input_length:]
    print("labels_chunk.shape", labels_chunk.shape)

    outputs = model.forward(
        inputs_embeds=input_embeddings_chunk,
        attention_mask=attention_mask_chunk,
        return_dict=True,
        output_attentions=False,
        output_hidden_states=False,
        past_key_values=past_key_values_chunk,
    )
    logits = outputs["logits"]
    past_key_values = outputs.get("past_key_values", None)

    shift_logits = logits[..., :-1, :].contiguous().transpose(1, 2)
    shift_labels = labels_chunk[..., 1:].contiguous()
    loss_fct = nn.CrossEntropyLoss(reduction="none")
    loss = loss_fct(shift_logits, shift_labels.to(shift_logits.device))
    loss = loss[..., output_indices].mean(-1)

    del outputs, shift_logits, shift_labels
    if logits.device.type == "cuda":
        torch.cuda.empty_cache()
    gc.collect()

    return SimpleNamespace(loss=loss, past_key_values=past_key_values, logits=logits)

@require_deps("torch", "transformers")
def foward_with_separated_losses_advprompter(
    model,
    input_embeddings_chunk,
    labels_chunk,
    output_indices,
    attention_mask_chunk,
    past_key_values_chunk=None,
    suffix_indices=None,
):
    print("output_indices", output_indices)
    past_input_length = (past_key_values_chunk[0][0].shape[2] if past_key_values_chunk is not None else 0)
    output_indices = [i - past_input_length for i in output_indices]
    print("past_innput_length", past_input_length)
    print("output_indices", output_indices)
    print("labels_chunk.shape", labels_chunk.shape)
    labels_chunk = labels_chunk[..., past_input_length:]
    print("labels_chunk.shape", labels_chunk.shape)

    outputs = model.forward(
        inputs_embeds=input_embeddings_chunk,
        attention_mask=attention_mask_chunk,
        return_dict=True,
        output_attentions=False,
        output_hidden_states=False,
        past_key_values=past_key_values_chunk,
    )
    logits = outputs["logits"]
    past_key_values = outputs.get("past_key_values", None)

    shift_logits = logits[..., :-1, :].contiguous().transpose(1, 2)
    shift_labels = labels_chunk[..., 1:].contiguous()
    loss_fct = nn.CrossEntropyLoss(reduction="none")
    token_losses = loss_fct(shift_logits, shift_labels.to(shift_logits.device))
    suffix_loss = (token_losses[..., suffix_indices].mean(-1) if suffix_indices is not None else 0)

    # gamma_t = 1/(t+1)
    sequence_length = len(output_indices)
    weights = torch.tensor(
        [1.0 / (t + 1) for t in range(sequence_length)],
        device=token_losses.device,
        dtype=token_losses.dtype,
    )
    output_loss = (token_losses[..., output_indices] * weights).mean(-1)
    lambda_reg = 1.0
    loss = output_loss + lambda_reg * suffix_loss

    del outputs, shift_logits, shift_labels
    if logits.device.type == "cuda":
        torch.cuda.empty_cache()
    gc.collect()

    return SimpleNamespace(loss=loss, past_key_values=past_key_values, logits=logits)

# -------------------------------
# Sampling helper
# -------------------------------
@require_deps("torch", "transformers")
def beam_sample_next_token(
    model, num_samples_per_beam, input_ids, attention_mask, temperature=1.0
):
    model_forward_res = model(input_ids=input_ids, attention_mask=attention_mask, return_dict=True)
    next_token_logits = model_forward_res.logits[:, -1, :]
    next_token_probs = torch.softmax(next_token_logits / temperature, dim=-1)
    next_token_ids = torch.multinomial(next_token_probs, num_samples=num_samples_per_beam)

    input_ids = input_ids.repeat_interleave(num_samples_per_beam, dim=0)
    beam_expanded = torch.cat([input_ids, next_token_ids.flatten().unsqueeze(-1)], dim=-1)
    return SimpleNamespace(next_token_ids=next_token_ids, beam_expanded=beam_expanded)

# -------------------------------
# Embedding helpers
# -------------------------------
@require_deps("torch", "transformers")
def get_embedding_layer(model):
    mt = _model_type(model)
    if mt in {"gptj"} or (GPTJForCausalLM and isinstance(model, GPTJForCausalLM)) \
       or (GPT2LMHeadModel and isinstance(model, GPT2LMHeadModel)):
        return model.transformer.wte
    if mt in {"llama", "gemma", "mistral", "qwen2"}:
        return model.model.embed_tokens
    if mt in {"gpt_neox"}:
        return model.base_model.embed_in
    if mt in {"falcon"}:
        return model.transformer.word_embeddings
    raise ValueError(f"Unknown/unsupported model_type={mt!r}")

@require_deps("torch", "transformers")
def get_embedding_matrix(model):
    mt = _model_type(model)
    if mt in {"gptj", "gpt2"}:
        return model.transformer.wte.weight
    if mt in {"llama", "mistral", "gemma", "qwen2"}:
        return model.model.embed_tokens.weight
    if mt in {"gpt_neox"}:
        return model.base_model.embed_in.weight
    if mt in {"falcon"}:
        return model.transformer.word_embeddings.weight
    raise ValueError(f"Unknown/unsupported model_type={mt!r}")

@require_deps("torch", "transformers")
def get_embeddings(model, input_ids):
    mt = _model_type(model)
    if mt in {"gptj", "gpt2"}:
        return model.transformer.wte(input_ids).half()
    if mt in {"llama", "mistral", "gemma", "qwen2"}:
        return model.model.embed_tokens(input_ids)
    if mt in {"gpt_neox"}:
        return model.base_model.embed_in(input_ids).half()
    # fallback
    return model.model.embed_tokens(input_ids)

# -------------------------------
# Token filters / penalties / metrics
# -------------------------------
@require_deps("torch")
def get_nonascii_toks(tokenizer, device="cpu"):
    def is_ascii(s): return s.isascii() and s.isprintable()
    ascii_toks = []
    for i in range(3, tokenizer.vocab_size):
        if not is_ascii(tokenizer.decode([i])):
            ascii_toks.append(i)
    for tid in (tokenizer.bos_token_id, tokenizer.eos_token_id, tokenizer.pad_token_id, tokenizer.unk_token_id):
        if tid is not None:
            ascii_toks.append(tid)
    return torch.tensor(ascii_toks, device=device)

@require_deps("torch")
def apply_repetition_penalty(logits, prev_ids, penalty):
    _logits = torch.gather(input=logits, dim=1, index=prev_ids)
    _logits = torch.where(_logits < 0, _logits * penalty, _logits / penalty)
    logits_penalized = torch.scatter(input=logits, dim=1, index=prev_ids, src=_logits)
    return logits_penalized

@require_deps("torch")
def compute_perplexity(id_seq, likelihood_seq):
    logprobs = torch.gather(likelihood_seq.logprobs, dim=2, index=id_seq.ids.unsqueeze(2)).squeeze(2)
    perplexity_per_token_masked = torch.exp(-logprobs) * id_seq.mask
    perplexity = torch.exp(-torch.sum(logprobs * id_seq.mask, dim=1) / (torch.sum(id_seq.mask, dim=1) + 1e-8))
    return perplexity, perplexity_per_token_masked

# -------------------------------
# Light ReturnStruct & CE loss
# -------------------------------
class ReturnStruct:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def clone(self):
        new_kwargs = {}
        for k, v in self.__dict__.items():
            try: new_kwargs[k] = v.clone()
            except: new_kwargs[k] = v
        return ReturnStruct(**new_kwargs)
    def detach(self):
        new_kwargs = {}
        for k, v in self.__dict__.items():
            try: new_kwargs[k] = v.detach()
            except: new_kwargs[k] = v
        return ReturnStruct(**new_kwargs)
    def _detach(self):
        for k, v in self.__dict__.items():
            try: v._detach()
            except: pass
    @require_deps("torch")
    def to(self, device):
        new_kwargs = {}
        for k, v in self.__dict__.items():
            try: new_kwargs[k] = v.to(device)
            except: new_kwargs[k] = v
        return ReturnStruct(**new_kwargs)

@require_deps("torch")
def ce_loss(pred_seq, target_seq, hard_labels, reweight_loss=False, **kwargs):
    if hard_labels:
        loss = F.cross_entropy(pred_seq.logits.transpose(1, 2), target_seq.ids, reduction="none", **kwargs)
    else:
        loss = F.cross_entropy(
            pred_seq.logits.transpose(1, 2),
            target_seq.probs.transpose(1, 2),
            reduction="none",
            **kwargs,
        )
    if reweight_loss:
        factor = torch.arange(loss.shape[1], dtype=loss.dtype, device=loss.device) + 1
        loss = loss / factor[None, :]
    return loss

@require_deps("torch")
def loss_seqs(pred_seq, target_seq, **loss_params):
    if torch.isnan(pred_seq.logits).any():
        raise ValueError(f"Nan in logits: {pred_seq.logits}")
    _loss = ce_loss(pred_seq, target_seq, **loss_params)
    mask = target_seq.mask
    loss_masked = _loss * mask
    loss_batch = torch.sum(loss_masked, dim=1) / (mask.sum(dim=1) + 1e-10)
    loss = loss_batch.mean()
    return ReturnStruct(
        loss=loss,
        loss_masked=loss_masked,
        loss_batch=loss_batch,
        pred=pred_seq,
        label=target_seq,
    )

# -------------------------------
# Logging helpers
# -------------------------------
@require_deps("torch")
def print_trainable_parameters(model):
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    logger.info(
        f" trainable params: {trainable_params} || all params: {all_param} || "
        f"trainable%: {100 * trainable_params / all_param:.2f}"
    )

# -------------------------------
# Autocast decorator (optional)
# -------------------------------
def autocast_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not HAVE_TORCH:
            raise MissingDependencyError("autocast_decorator requires torch")
        device_type = "cuda" if "cuda" in str(getattr(self, "device", "")) else "cpu"
        # dtype left to PyTorch default (bf16/fp16 if enabled)
        with torch.autocast(device_type=device_type):
            return func(self, *args, **kwargs)
    return wrapper

# -------------------------------
# LLM loader (optional deps)
# -------------------------------
@require_deps("torch", "transformers")
def llm_loader(checkpoint, dtype, device, freeze=False, lora_checkpoint=None, lora_config=None, verbose=False):
    logger.info(f" Loading model from {checkpoint}...")
    mem_before = get_total_allocated_memory()

    if isinstance(dtype, str):
        if dtype == "float32":
            dtype = torch.float32
        elif dtype == "float16":
            dtype = torch.float16
        else:
            raise ValueError(f"Cannot load model with dtype {dtype}")

    # Tokenizer
    use_fast = "pythia" in str(checkpoint).lower()
    tok_kwargs = dict(model_max_length=1024, padding_side="right", use_fast=use_fast, legacy=False)
    if checkpoint == "stas/tiny-random-llama-2":
        tok_kwargs.pop("model_max_length", None)
        tok_kwargs.pop("use_fast", None)
        tok_kwargs.pop("legacy", None)

    tokenizer = AutoTokenizer.from_pretrained(checkpoint, **tok_kwargs)

    # Model
    if checkpoint == "stas/tiny-random-llama-2":
        model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=dtype).to(device)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            checkpoint, low_cpu_mem_usage=True, torch_dtype=dtype, device_map=device
        )

    mem_after = get_total_allocated_memory()
    if verbose:
        logger.info(f" Loaded model: {model}")
    logger.info(
        f" Mem usage model: {mem_after - mem_before:.2f} GB | Total Mem usage: {mem_after:.2f} GB"
    )

    embedding_matrix = get_embedding_matrix(model).to(device)

    if freeze:
        logger.info(" Freezing model...")
        for _, v in model.named_parameters():
            v.requires_grad = False

    # LoRA (optional)
    if (lora_checkpoint is not None) or (lora_config is not None):
        if not HAVE_PEFT:
            raise MissingDependencyError("LoRA requested but PEFT is not installed. " +
                                         "Try: pip install peft")
        if lora_checkpoint is not None:
            logger.info(f" Loading LoRA checkpoint: {lora_checkpoint}")
            model = PeftModel.from_pretrained(model, lora_checkpoint, is_trainable=not freeze)
        else:
            logger.info(" Transforming to LoRA model...")
            cfg = dict(lora_config)
            cfg["target_modules"] = [m for m in lora_config["target_modules"]]
            lcfg = LoraConfig(**cfg)
            if hasattr(model, "add_adapter"):
                model.add_adapter(lcfg, adapter_name="lora")
                if hasattr(model, "enable_adapters"):
                    model.enable_adapters()
            else:
                model = PeftModel(model, lcfg)

    print_trainable_parameters(model)
    return model, tokenizer, embedding_matrix
