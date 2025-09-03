import math
import os
from typing import Optional, Dict, Any
import torch
import torch.distributed as dist
from torch.distributed.fsdp import MixedPrecisionPolicy, fully_shard
from torch.distributed.algorithms._checkpoint.checkpoint_wrapper import (
    checkpoint_wrapper as ptd_checkpoint_wrapper,
)
from torch.distributed.device_mesh import init_device_mesh
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from mini_trainer.utils import log_rank_0, patch_target_module
from mini_trainer.osft_utils import OSFTModel



# New simple HF-only activation-checkpointing + FSDP2 wrapper
# This mirrors TorchTitan: checkpoint each block, then shard each block and the full model.
def wrap_fsdp2(model: torch.nn.Module) -> torch.nn.Module:
    # Move model to GPU and disable HuggingFace cache
    if model.device.type != 'cuda':
        # Move the model to the GPU if it's not already there
        local_rank = int(os.environ['LOCAL_RANK'])
        device = torch.device('cuda', local_rank)
        model.to(device)

    if hasattr(model, 'config'):
        try:
            model.config.use_cache = False
        except Exception as e:
            print(
                f"WARNING: Failed to disable HuggingFace cache for model {model.__class__.__name__}: {e}"
            )
            pass
    # 1) Find the HF transformer block container (GPT2: transformer.h, Llama: model.layers)
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        layers = model.model.layers
    else:
        raise ValueError("Cannot find transformer block container on model")
    # 2) Activation checkpoint each block
    for idx, block in enumerate(layers):
        layers[idx] = ptd_checkpoint_wrapper(block, preserve_rng_state=False)

    # 3) Build a 1D device mesh over all ranks
    world_size = dist.get_world_size()
    mesh = init_device_mesh("cuda", [world_size], mesh_dim_names=["fsdp"])

    # 4) Mixed-precision policy (bf16)
    mp_policy = MixedPrecisionPolicy(
        param_dtype=torch.bfloat16, 
        reduce_dtype=torch.float32,
    )

    # 4) FSDP2 wrap each block
    for idx, block in enumerate(layers):
        reshard = idx < len(layers) - 1
        fully_shard(block, mesh=mesh, mp_policy=mp_policy, reshard_after_forward=reshard)

    # 5) FSDP2 wrap full model
    fully_shard(model, mesh=mesh, mp_policy=mp_policy, reshard_after_forward=True)
    return model

def align_model_and_tokenizer(model, tokenizer):
    """
    Aligns the model's vocabulary and special tokens with the tokenizer.
    """
    if len(tokenizer) > model.config.vocab_size:
        print(
            f"WARNING: tokenizer has {len(tokenizer)} tokens but model has {model.config.vocab_size} vocab size"
        )
        model.resize_token_embeddings(
            int(8 * math.ceil(len(tokenizer) / 8.0))
        )  # make the vocab size multiple of 8 for sharding the embedding layer.

    # Fix any discrepancy between model and tokenizer
    special_tokens = {
        'pad': ('pad_token_id', 'Fixing model pad token id'),
        'bos': ('bos_token_id', 'Fixing model bos token id'),
        'eos': ('eos_token_id', 'Fixing model eos token id')
    }

    for token_type, (token_attr, message) in special_tokens.items():
        model_token = getattr(model.config, token_attr)
        tokenizer_token = getattr(tokenizer, token_attr)
        
        if (model_token is not None and tokenizer_token is not None 
            and model_token != tokenizer_token):
            log_rank_0(
                "\033[38;5;226m"
                f"WARNING: There is a mismatch between {token_type} token id of "
                f"model({model_token}) and tokenizer({tokenizer_token}). "
                f"{message} to be same as tokenizer's {token_type} token id"
                "\033[0m"
            )
            setattr(model.config, token_attr, tokenizer_token)

    return model


def get_model_save_dtype(save_dtype: str | torch.dtype | None, model_name_or_path: str) -> torch.dtype:
    """
    Given an HF model reference and an optional user-provided save_dtype, returns the PyTorch data type that it should
    be saved in.

    If the user does not provide a save_dtype, we will use the model's original dtype.
    However; if the data-type is not in the supported list, we will raise an error.

    If both the model `torch_dtype` and user-provided `save_dtype` are missing,
    we default to saving in BF16.

    Args:
        save_dtype (str | None): The dtype we should be saving the model as.
        model_name_or_path (str): The name or path of the model to load.
    Returns:
        The PyTorch data type that the model should be saved in.

    """
    dtype_map = {
        "float32": torch.float32,
        "float": torch.float32,
        "float64": torch.float64,
        "double": torch.float64,
        "float16": torch.float16,
        "half": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    default_dtype = torch.bfloat16
    
    # FSDP2 requires us to load the model in FP32 to begin with for the
    # correct mixed-precision settings. So to circumvent this, we load the 
    # original model's config separately 
    original_config = AutoConfig.from_pretrained(model_name_or_path)
    original_dtype = getattr(original_config, "torch_dtype", None)
    
    # HF models return a torch.dtype from this field, but docs mark it as an optional string
    if original_dtype is not None and isinstance(original_dtype, str):
        original_dtype = dtype_map[original_dtype]

    # this handles the case when save_dtype > original_dtype > bf16
    if not original_dtype and not save_dtype:
        log_rank_0(f"⚠️ Model does not have a setting for `torch_dtype` and not `save_dtype` was provided, falling back to '{default_dtype}'")
        return default_dtype

    # handles the case save_dtype > original_dtype
    if not save_dtype:
        return original_dtype
    
    # by now we know that we are going to use a custom data type, so we just validate
    if not isinstance(save_dtype, (str, torch.dtype)):
        raise ValueError(f"error: could not recognize '{save_dtype}' as a supported dtype for saving model checkpoints")
 
    # convert dtype to a str
    if isinstance(save_dtype, str):
        if save_dtype not in dtype_map:
            raise ValueError(f"error: could not recognize '{save_dtype}' as a supported dtype for saving model checkpoints")
        save_dtype = dtype_map[save_dtype]
    
    # alert the user when the dtype differs
    if original_dtype and original_dtype != save_dtype:
        log_rank_0(f"⚠️ Model's original dtype is '{original_dtype}', but new checkpoints will be saved as '{save_dtype}'. ⚠️")
    return save_dtype


def setup_model(
    model_name_or_path: str,
    osft: bool = False,
    local_rank: int = 0,
    save_dtype: str | torch.dtype | None = None,
    osft_upcast_dtype: torch.dtype = torch.float32,
    osft_output_dtype: torch.dtype | None = None,
    osft_rank_ratio: float | None = None,
    osft_target_patterns: list[str] | None = None,
    use_liger_kernels: bool = False,
) -> torch.nn.Module | OSFTModel:
    base_model_args = {
        "pretrained_model_name_or_path": model_name_or_path,
    }
    # Check if flash_attn is available, otherwise use eager
    # in practice we will need flash attention when running this repo
    try:
        import flash_attn
        base_model_args["attn_implementation"] = "flash_attention_2"
    except ImportError as e:
        if os.environ.get("TESTING", "false").lower() == "true":
            base_model_args["attn_implementation"] = "eager"
        else:
            raise e

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    if use_liger_kernels:
        """need to patch the loss function to not reduce, so we can reduce across all GPUs"""
        from mini_trainer.none_reduction_losses import (
            liger_fixed_fused_linear_cross_entropy_none_reduction,
        )

        patch_target_module(
            "liger_kernel.transformers.model.loss_utils.fixed_fused_linear_cross_entropy",
            liger_fixed_fused_linear_cross_entropy_none_reduction,
        )
        from liger_kernel.transformers import AutoLigerKernelForCausalLM as ModelClass
    else:
        from mini_trainer.none_reduction_losses import hf_fixed_cross_entropy_none_reduction
        patch_target_module(
            "transformers.loss.loss_utils.fixed_cross_entropy",
            hf_fixed_cross_entropy_none_reduction,
        )
        ModelClass = AutoModelForCausalLM
    
    def load_standard_model():
        model = ModelClass.from_pretrained(**base_model_args)
        return align_model_and_tokenizer(model, tokenizer)
    
    # Load a subclassed model that supports orthogonal subspace learning using SVD decomposition
    def load_osft_model():
        # Import utility to decompose weights and inject projected low-rank updates
        from mini_trainer.osft_utils import create_osft_model_class, auto_generate_target_osft_config

        tmp = ModelClass.from_pretrained(**base_model_args)
        tmp = align_model_and_tokenizer(tmp, tokenizer)
        # Dynamically subclass model to override linear layers with OSFT-decomposed versions
        osft_cls = create_osft_model_class(tmp.__class__)
        cfg = tmp.config
        del tmp
        torch.cuda.empty_cache()

        osft_kwargs = {}
        if osft_rank_ratio:
            osft_kwargs["rank_ratio"] = osft_rank_ratio
        if osft_target_patterns:
            osft_kwargs["target_patterns"] = osft_target_patterns

        model: OSFTModel = osft_cls.from_pretrained(
            **base_model_args,
            config=cfg,
            initialize_osft=False,
            **osft_kwargs,
        )
        
        # we need to set these as attributes because HF Transformers
        # doesn't like torch.dtype to be passed in through kwargs (aside from the `torch_dtype` kwarg)
        model.upcast_dtype = osft_upcast_dtype
        if osft_output_dtype:
            model.output_dtype = osft_output_dtype

        model = align_model_and_tokenizer(model, tokenizer)
        device = torch.device("cuda", local_rank)
        model = model.to(device)

        # NOTE(osilkin): SVD over large models is very expensive, to optimize we handle
        # each of these cases separately:
        # 1.) non-distributed --> assume single process
        # 2.) distributed, world-size=1 --> assume single process
        # 3.) distributed, world-size > 1 --> use distributed SVD computation

        if not dist.is_initialized() or dist.get_world_size() == 1:
            # simple cases #1 and #2
            model.reinitialize_osft(decompose_existing_weights=True)
            torch.cuda.empty_cache()
            return model

        # Use distributed SVD computation across all ranks
        log_rank_0("🚀 Computing distributed OSFT decomposition across all ranks")
        world_size = dist.get_world_size()
        log_rank_0(f"Distributing OSFT work across {world_size} ranks")

        # Initialize OSFT using distributed computation
        model.reinitialize_osft_distributed()

        log_rank_0("✅ Distributed OSFT decomposition complete")
        torch.cuda.empty_cache()
        return model
    
    # Choose whether to apply orthogonal subspace learning (OSL) based on `osft` flag
    # OSL enables continual fine-tuning by constraining updates to low-rank directions orthogonal to critical knowledge that is to be preserved
    model = load_osft_model() if osft else load_standard_model()

    # here we handle configuring the save_dtype
    model.config.torch_dtype = get_model_save_dtype(save_dtype, model_name_or_path)
    if not model.config.torch_dtype:
        raise ValueError("error: model does not have a `torch_dtype` setting, cannot save model in this dtype")

    if model.__class__.__name__ not in [
        "MistralForCausalLM",
        "GPTDolomiteForCausalLM", 
        "LlamaForCausalLM",
        "Starcoder2ForCausalLM",
        "GemmaForCausalLM",
        "MixtralForCausalLM",
        "GraniteForCausalLM",
    ]:
        log_rank_0(
            f"\033[38;2;255;255;0mWarning: Model class name: {model.__class__.__name__} is not in the list of supported models.\033[0m",
            to_print=True,
        )

    # NOTE: Don't enable HuggingFace gradient checkpointing with FSDP2
    # It causes conflicts. TorchTitan applies PyTorch's checkpoint wrapper
    # BEFORE FSDP2 wrapping if needed.
    # model.gradient_checkpointing_enable()
    # torch.compile(model)
    return model

def setup_training_components(
    model: torch.nn.Module,
    learning_rate: float,
    num_warmup_steps: int,
    lr_scheduler: str,
    num_training_steps: Optional[int] = None,
    scheduler_kwargs: Optional[Dict[str, Any]] = None,
) -> tuple[torch.nn.Module, torch.optim.Optimizer, torch.optim.lr_scheduler.LRScheduler]:
    """
    Set up training components including model wrapping, optimizer, and learning rate scheduler.
    
    Args:
        model: The model to be trained
        learning_rate: Peak learning rate for the optimizer
        num_warmup_steps: Number of warmup steps for the LR scheduler
        lr_scheduler: Type of learning rate scheduler to use
        num_training_steps: Total number of training steps (required for some schedulers)
        scheduler_kwargs: Additional scheduler-specific keyword arguments
    
    Returns:
        Tuple of (wrapped_model, optimizer, lr_scheduler)
    """
    from transformers import get_scheduler
    
    # Using FSDP2 wrapper
    log_rank_0("Using FSDP2 wrapper")
    model = wrap_fsdp2(model)
    
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        betas=(0.9, 0.95),
        weight_decay=0.0,
    )
    from mini_trainer.osft_utils import optim_wrapper
    optimizer = optim_wrapper(optimizer, model)
    # Prepare scheduler kwargs
    if scheduler_kwargs is None:
        scheduler_kwargs = {}
    
    lr_scheduler = get_scheduler(
        name=lr_scheduler,
        optimizer=optimizer,
        num_warmup_steps=num_warmup_steps,
        num_training_steps=num_training_steps,
        scheduler_specific_kwargs=scheduler_kwargs,
    )
    lr_scheduler.split_batches = True
    lr_scheduler.step() #the scheduler starts at 0 and there's no learning.
    return model, optimizer, lr_scheduler

