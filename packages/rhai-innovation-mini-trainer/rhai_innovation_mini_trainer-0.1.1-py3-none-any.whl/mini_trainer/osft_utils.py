import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch.distributed as dist
import typing as t
from typing import Protocol

from tqdm import tqdm

from mini_trainer.utils import log_rank_0, check_distributed_is_synchronized

import os

# Memory optimization constants
OSFT_CACHE_CLEAR_INTERVAL = int(os.getenv(
    "OSFT_CACHE_CLEAR_INTERVAL", 5
))  # Clear GPU cache every N parameters during matrix reconstruction


class SVDDictBase(t.TypedDict):
    U_high: torch.Tensor
    S_high: torch.Tensor
    V_high: torch.Tensor
    U_low: nn.Parameter
    S_low: nn.Parameter
    V_low: nn.Parameter


class SVDDecompositionDict(SVDDictBase, total=False):
    rank_high: int


class OSFTModelProtocol(Protocol):
    """
    Protocol defining the interface for models with OSFT capabilities.

    This allows type hints throughout the codebase without depending on the dynamically
    created class from create_osft_model_class().
    """

    osft_config: dict[str, int]
    name_mapping: dict[str, str]
    osft_params: nn.ModuleDict
    upcast_dtype: torch.dtype
    output_dtype: torch.dtype

    def reinitialize_osft(
        self,
        decompose_existing_weights: bool,
        assigned_params: list[tuple[str, torch.Tensor]] | None = None,
    ) -> None: ...

    def reinitialize_osft_distributed(self) -> None: ...

    def project_gradients(self) -> None: ...

    def _reconstruct_weight_by_safe_name(
        self,
        safe_name: str,
        upcast_dtype: torch.dtype | None = None,
        output_dtype: torch.dtype | None = None,
    ) -> torch.Tensor: ...

    def _reconstruct_weight(
        self,
        original_name: str,
        upcast_dtype: torch.dtype | None = None,
        output_dtype: torch.dtype | None = None,
    ) -> torch.Tensor: ...


# Type alias for any model that implements OSFT
OSFTModel = OSFTModelProtocol


# Pre-defined model configurations for common architectures
MODEL_CONFIGS = {
    "llama": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj", 
            "self_attn.v_proj",
            "self_attn.o_proj",
            "mlp.gate_proj",
            "mlp.down_proj",
            "mlp.up_proj",
        ]
    },
    "mistral": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj",
            "self_attn.v_proj",
            "self_attn.o_proj",
            "mlp.gate_proj",
            "mlp.up_proj",
            "mlp.down_proj",
        ]
    },
    "gpt-j": {
        "patterns": [
            "attn.q_proj",
            "attn.k_proj",
            "attn.v_proj", 
            "attn.out_proj",
            "mlp.fc_in",
            "mlp.fc_out",
        ]
    },
    "gpt-neo": {
        "patterns": [
            "attn.attention.q_proj",
            "attn.attention.k_proj",
            "attn.attention.v_proj",
            "attn.attention.out_proj", 
            "mlp.c_fc",
            "mlp.c_proj",
        ]
    },
    "opt": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj",
            "self_attn.v_proj",
            "self_attn.out_proj",
            "fc1",
            "fc2",
        ]
    },
    "qwen": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj",
            "self_attn.v_proj", 
            "self_attn.o_proj",
            "mlp.gate_proj",
            "mlp.down_proj",
            "mlp.up_proj",
        ]
    },
    "gemma": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj",
            "self_attn.v_proj",
            "self_attn.o_proj",
            "mlp.gate_proj",
            "mlp.up_proj",
            "mlp.down_proj",
        ],
    },
    "phi3": {
        "patterns": [
            "self_attn.o_proj",
            "self_attn.qkv_proj",
            "mlp.gate_up_proj",
            "mlp.down_proj",
        ]
    },
    # granite-4 architecture may change so this will likely
    # need to be updated then
    "granite": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj",
            "self_attn.v_proj",
            "self_attn.o_proj",
            "mlp.gate_proj",
            "mlp.down_proj",
            "mlp.up_proj",
        ]
    },
    "default": {
        "patterns": [
            "self_attn.q_proj",
            "self_attn.k_proj",
            "self_attn.v_proj",
            "self_attn.o_proj", 
            "mlp.gate_proj",
            "mlp.down_proj",
            "mlp.up_proj",
        ]
    }
}

# Define model name mappings at module level
MODEL_NAME_MAPPINGS = {
    "llama": "llama",
    "gpt-j": "gpt-j", 
    "gptj": "gpt-j",  # Handle both "gpt-j" and "gptj" variants
    "gpt-neo": "gpt-neo",
    "gptneo": "gpt-neo",  # Handle both "gpt-neo" and "gptneo" variants
    "opt": "opt",
    "qwen": "qwen",
    "gemma": "gemma",
    "phi4": "phi3",
    "phi-4": "phi3",  # this should handle phi-4, phi-4-mini, and phi-4-mini-instruct
    "phi3": "phi3",
    "phi-3": "phi3",
    "mistral": "mistral",
    "granite": "granite",
    # Easy to add more mappings
    # "phi": "phi", 
}


def is_osft_param(name: str, param: torch.Tensor, osft_config: dict) -> bool:
    """
    Utility function to make it easier to classify OSFT parameters.
    """
    return len(param.shape) == 2 and name in osft_config and osft_config[name] > 0


def is_osft_model(model: torch.nn.Module) -> bool:
    """
    Check if a model implements the OSFT interface.

    Args:
        model: The model to check

    Returns:
        True if the model has OSFT capabilities, False otherwise
    """
    required_attrs = [
        "osft_config",
        "osft_params",
        "project_gradients",
        "reinitialize_osft",
    ]
    return all(hasattr(model, attr) for attr in required_attrs)


def cast_to_osft_model(model: torch.nn.Module) -> OSFTModel:
    """
    Cast a model to OSFTModel type for type checkers.

    Args:
        model: The model to cast (should implement OSFTModelProtocol)

    Returns:
        The same model, but typed as OSFTModel

    Raises:
        TypeError: If the model doesn't implement the OSFT interface
    """
    if not is_osft_model(model):
        raise TypeError(f"Model {type(model)} does not implement OSFT interface")
    return model  # type: ignore

def create_svd_dict(
    weight: torch.Tensor,
    top_k: int,
    decompose_existing: bool = True,
    upcast_dtype: torch.dtype = torch.float32,
    output_dtype: torch.dtype | None = None,
) -> SVDDecompositionDict:
    """
    Decomposes a 2D weight matrix into two components using Singular Value Decomposition (SVD):
    - The top `top_k` singular components (U_high, S_high, V_high) are treated as frozen and encode
      critical directions that should not be updated in new tasks.
    - The remaining components (U_low, S_low, V_low) are made trainable and are used to learn new tasks.

    This decomposition separates the weight space into high-rank subspaces for knowledge retention
    and low-rank subspaces for task-specific adaptation, helping to mitigate catastrophic forgetting
    in continual learning scenarios.
    """
    device_local = weight.device

    # handle casting data-types
    if not output_dtype:
        output_dtype = upcast_dtype

    if weight.ndim != 2:
        raise ValueError(
            "creating SVD dict from a non-2D tensor is currently unsupported!"
        )

    # N: output dim, M: input dim
    N, M = weight.shape

    if decompose_existing:
        # To minimize numerical error, we perform the SVD decomposition
        # in high precision, before casting back to the original data-type
        # since FSDP requires homogenous data-types.
        W = weight.to(upcast_dtype)  # Ensure numerical stability for SVD
        U, S, Vt = torch.linalg.svd(W, full_matrices=False)
        if upcast_dtype != output_dtype:
            U = U.to(output_dtype)
            S = S.to(output_dtype)
            Vt = Vt.to(output_dtype)
    else:
        # Note(osilkin):
        # Here we create dummy versions of the weights initialized to 0
        # So that we can later populate them with the SVD from another process
        # this is how pytorch reshapes the SVD matrices with `full_matrices=False`
        R = min(N, M)

        # recreate how the matrices would be shaped inside of pytorch
        U = torch.zeros((N, R), dtype=output_dtype)
        S = torch.zeros((R,), dtype=output_dtype)
        Vt = torch.zeros((R, M), dtype=output_dtype)

    k = min(top_k, S.shape[0])  # Cap to matrix rank

    # Split high-rank (frozen) and low-rank (trainable) subspaces
    svd = {
        "U_high": U[:, :k].contiguous().detach().to(device=device_local),
        "S_high": S[:k].contiguous().detach().to(device=device_local),
        "V_high": Vt[:k, :].contiguous().detach().to(device=device_local),
        "U_low": nn.Parameter(U[:, k:].contiguous().detach().to(device=device_local)),
        "S_low": nn.Parameter(S[k:].contiguous().detach().to(device=device_local)),
        "V_low": nn.Parameter(Vt[k:, :].contiguous().detach().to(device=device_local)),
        "rank_high": k, # Store for later use in orthogonal projection
    }
    return svd


def reconstruct_weight_matrix(
    svd_dict: SVDDecompositionDict,
    upcast_dtype: torch.dtype,
    output_dtype: torch.dtype | None = None,
):
    """
    Reconstructs the original weight matrix from its SVD components.

    Used for replacing linear layers during inference or forward pass to preserve the weight structure.
    The final matrix is the sum of contributions from both the high-rank (frozen) and low-rank (trainable) components.
    """
    U_high = svd_dict["U_high"].to(upcast_dtype)
    S_high = svd_dict["S_high"].to(upcast_dtype)
    V_high = svd_dict["V_high"].to(upcast_dtype)
    U_low = svd_dict["U_low"].to(upcast_dtype)
    S_low = svd_dict["S_low"].to(upcast_dtype)
    V_low = svd_dict["V_low"].to(upcast_dtype)

    # Reconstruct high-rank component (frozen during continual learning)
    if U_high.numel() > 0 and S_high.numel() > 0:
        high_part = torch.mm(U_high * S_high.unsqueeze(0), V_high)
    else:
        high_part = torch.zeros(
            U_low.size(0), V_low.size(1), device=U_high.device, dtype=upcast_dtype
        )

    # Reconstruct low-rank component (receives task-specific updates)
    if U_low.numel() > 0 and S_low.numel() > 0:
        low_part = torch.mm(U_low * S_low.unsqueeze(0), V_low)
    else:
        low_part = torch.zeros(
            U_high.size(0),
            V_high.size(1),
            device=U_low.device,
            dtype=upcast_dtype,
        )

    # Combine the low-rank & high-rank components
    reconstructed = high_part + low_part
    if output_dtype:
        reconstructed = reconstructed.to(output_dtype)
    return reconstructed


def project_gradient_to_orthogonal_space(svd_dict: SVDDecompositionDict):
    """
    Projects the gradient of the low-rank parameters (U_low, V_low) to be orthogonal to the frozen high-rank subspace.

    This step ensures that learning new tasks does not interfere with previously learned representations by enforcing an orthogonality constraint.

    TODO(osilkin): Add mixed-precision gradients here
    """
    # Skip if no gradients present (sanity check)
    if (
        svd_dict["U_low"].grad is None
        and svd_dict["S_low"].grad is None
        and svd_dict["V_low"].grad is None
    ):
        return

    U_high = svd_dict["U_high"]
    V_high = svd_dict["V_high"]

    # Project U_low gradients to space orthogonal to U_high
    if svd_dict["U_low"].grad is not None:
        dU = svd_dict["U_low"].grad
        # Support distributed tensors by operating on the local shard
        local_U_high = getattr(U_high, "to_local", lambda: U_high)()
        local_dU = getattr(dU, "to_local", lambda: dU)()
        # Handle sharded tensors in distributed training
        if local_U_high.size(0) != local_dU.size(0):
            global_rank = torch.distributed.get_rank()
            start = global_rank * local_dU.size(0)
            end = start + local_dU.size(0)
            local_U_high = local_U_high[start:end]
        
        # Perform projection computation using memory-efficient operations
        # Memory-optimized projection: dU = dU - U_high @ (U_high.T @ dU)
        # Use addmm_ for efficient in-place operation
        proj_coeff = torch.mm(local_U_high.transpose(0, 1), local_dU)
        local_dU.addmm_(local_U_high, proj_coeff, alpha=-1.0)
        
        if hasattr(dU, "_local_tensor"):
            dU._local_tensor.copy_(local_dU)
        else:
            dU.copy_(local_dU)

    # Repeat projection for V_low using V_high
    if svd_dict["V_low"].grad is not None:
        dV = svd_dict["V_low"].grad
        local_V_high = getattr(V_high, "to_local", lambda: V_high)()
        local_dV = getattr(dV, "to_local", lambda: dV)()
        if local_V_high.size(1) != local_dV.size(1):
            global_rank = torch.distributed.get_rank()
            start = global_rank * local_dV.size(1)
            end = start + local_dV.size(1)
            local_V_high = local_V_high[:, start:end]
        
        # Perform projection computation using memory-efficient operations
        # Memory-optimized projection: dV = dV - (dV @ V_high.T) @ V_high
        # Use addmm_ for efficient in-place operation
        proj_coeff = torch.mm(local_dV, local_V_high.transpose(0, 1))
        local_dV.addmm_(proj_coeff, local_V_high, alpha=-1.0)
        
        if hasattr(dV, "_local_tensor"):
            dV._local_tensor.copy_(local_dV)
        else:
            dV.copy_(local_dV)


def get_osft_target_parameters(model, osft_config):
    """
    Determines which parameters will be OSFT decomposed based on the OSFT configuration.

    Returns a list of (name, param) tuples for parameters that will be decomposed.
    """
    target_params = []
    for name, param in model.named_parameters():
        # TODO(osilkin): Right now we are only training 2D parameters, but some 1D parameters (like bias vectors)
        # are vectors stored as a list, but may be interpreted as a (1, N) or (N, 1) matrix.
        # SVD can processs these in general, but maybe they should be targeted normally
        if is_osft_param(name, param, osft_config):
            target_params.append((name, param))
    return target_params


def partition_svd_computation(target_params, world_size):
    """
    Partitions the SVD computation work across all ranks.

    Args:
        target_params: List of (name, param) tuples to be decomposed
        world_size: Number of distributed processes

    Returns:
        List of parameter assignments for each rank
    """
    # Create a list of parameter assignments for each rank
    assignments = [[] for _ in range(world_size)]

    # Simple round-robin assignment to balance work
    for i, (name, param) in enumerate(target_params):
        rank = i % world_size
        assignments[rank].append((name, param))

    return assignments


def broadcast_svd_results(model, assignments, world_size):
    """
    Broadcasts SVD computation results from each rank to all other ranks.

    Args:
        model: The model with SVD parameters
        assignments: List of parameter assignments for each rank
        world_size: Number of distributed processes
    """
    # Create a mapping from parameter name to the rank that computed it
    param_to_rank = {}
    for rank, params in enumerate(assignments):
        for name, _ in params:
            param_to_rank[name] = rank

    # Broadcast each parameter from its computing rank
    for name in param_to_rank:
        src_rank = param_to_rank[name]
        safe_name = name.replace(".", "_")

        # Broadcast buffer components (high-rank frozen components)
        buffer_components = [
            f"{safe_name}_U_high",
            f"{safe_name}_S_high",
            f"{safe_name}_V_high",
        ]

        # In this loop, all of the processes broadcast their
        # respective SVD components that they generated.
        for component_name in buffer_components:
            if hasattr(model, component_name):
                tensor = getattr(model, component_name)
                dist.broadcast(tensor, src=src_rank)
            else:
                raise AttributeError(f"Warning: Buffer {component_name} not found in model")

        # wait for all processes to synchronize
        dist.barrier()

        # Broadcast trainable components (low-rank parameters)
        if safe_name in model.osft_params:
            svd_module = model.osft_params[safe_name]

            # Broadcast U_low, S_low, V_low
            dist.broadcast(svd_module.U_low, src=src_rank)
            dist.broadcast(svd_module.S_low, src=src_rank)
            dist.broadcast(svd_module.V_low, src=src_rank)
        else:
            raise AttributeError(f"Warning: OSFT module {safe_name} not found in model.osft_params")

    # wait for all processes to synchronize
    dist.barrier()

def _get_model_patterns_from_name(name: str) -> list:
    """
    Get model patterns from a model name string.
    
    Args:
        name: Model name string
        
    Returns:
        List of patterns for the model
    """
    # Find first matching model type
    for identifier, config_key in MODEL_NAME_MAPPINGS.items():
        if identifier in name.lower():
            return MODEL_CONFIGS[config_key]["patterns"]
    
    # Default fallback
    return MODEL_CONFIGS["default"]["patterns"]

def get_model_patterns(model_name_or_class):
    """Get patterns for a model from name string or class object."""
    # Handle string model names
    name = model_name_or_class
    if not isinstance(name, str):
        if hasattr(name, "__name__"):
            name = name.__name__
        else:
            raise ValueError(f"Invalid model name or class: {model_name_or_class} (expected str or class object)")
    
    return _get_model_patterns_from_name(name)


def get_model_config(model_name_or_class=None, target_patterns=None):
    """
    Get SVD target patterns for a model.
    
    Args:
        model_name_or_class: Model name/class to get predefined patterns for, or None
        target_patterns: Custom list of patterns to use instead of predefined ones
        
    Returns:
        List of patterns to match against parameter names
    """
    if target_patterns is not None:
        return target_patterns
        
    if model_name_or_class is None:
        return MODEL_CONFIGS["default"]["patterns"]
    
    return get_model_patterns(model_name_or_class)


def auto_generate_target_osft_config(
    model, model_name_or_class=None, target_patterns=None, rank_ratio=0.5
) -> dict[str, int]:
    """
    Automatically selects which weight matrices to decompose for OSFT and determines their top-k values.

    Args:
        model: The model to analyze
        model_name_or_class: Model name/class to get predefined patterns for, or None for auto-detection
        target_patterns: Custom list of patterns to use instead of predefined ones
        rank_ratio: Ratio of the smaller dimension to use for top-k rank (default: 0.5)
        
    Returns:
        Dictionary mapping parameter names to their top-k values
    """
    target_patterns = get_model_config(model_name_or_class, target_patterns)
    
    config = {}
    for name, param in model.named_parameters():
        if any(pat in name for pat in target_patterns) and len(param.shape) == 2:
            # Use specified ratio of effective rank
            top_k = int(np.floor(min(param.shape) * rank_ratio))
            full_rank = min(param.shape)
            if top_k >= full_rank:
                top_k = full_rank - 1
            config[name] = top_k
    return config


def create_osft_model_class(base_cls) -> type[OSFTModel]:
    """
    Dynamically creates a subclass of the given `base_cls` that replaces selected linear weights
    with low-rank + high-rank SVD-decomposed versions for OSFT training.

    This class:
    - Initializes frozen high-rank buffers and trainable low-rank parameters.
    - Replaces the forward pass of targeted modules to use reconstructed weights.
    - Projects gradients during training to enforce orthogonality with high-rank subspaces.

    This class enables constrained full fine-tuning using OSFT (Orthogonal Subspace Fine-Tuning).

    Returns:
        A class that implements OSFTModelProtocol and inherits from base_cls.
    """

    class ModelWithOSFT(base_cls):
        osft_config: dict[str, int]

        def __init__(
            self,
            config,
            osft_config: dict[str, int] | None = None,
            initialize_osft=True,
            upcast_dtype: torch.dtype = torch.float32,
            output_dtype: torch.dtype | None = None,
            **kwargs,
        ):
            super().__init__(config, **kwargs)
            self.osft_config = osft_config or {}  # Maps parameter names → top_k
            self.name_mapping = {}
            self.osft_params = (
                nn.ModuleDict()
            )  # Stores low-rank trainable OSFT components

            # We want to define how we will upcast & what precision we'll store the SVD
            # params in. Higher precision is best, but expensive during training, so
            # we use a higher precision data type for computing to/from SVD components
            # and store in the original data-type by default (usually bf16)
            self.upcast_dtype = upcast_dtype
            self.output_dtype = output_dtype if output_dtype is not None else self.dtype

            if initialize_osft:
                self._initialize_osft_parameters(decompose_existing_weights=True)

        @classmethod
        def from_pretrained(
            cls,
            pretrained_model_name_or_path,
            *model_args,
            osft_config: dict[str, int] | None = None,
            model_name_or_class=None,
            target_patterns=None,
            rank_ratio=0.5,
            **kwargs
        ) -> type[OSFTModel]:
            """Load pretrained weights and automatically initialize OSFT parameters."""
            # Do not initialize OSFT during the initial construction so we load
            # the original dense weights first
            # First load the base model normally without any OSFT kwargs
            init_cfg = osft_config if osft_config is not None else {}
            log_rank_0("\033[33m!!!! Calling from_pretrained !!!!\033[0m")
            initialize_osft = kwargs.pop('initialize_osft', False)
            model = super(ModelWithOSFT, cls).from_pretrained(
                pretrained_model_name_or_path,
                *model_args,
                osft_config=init_cfg,
                # we also have initialize_osft as an option in __init__, so disable it here
                initialize_osft=False,  
                **kwargs,
            )

            log_rank_0("\033[33m!!!! loading osft config !!!!\033[0m")
            # Auto-generate OSFT config if not provided
            if osft_config is None:
                # Use pretrained model name if no specific model_name_or_class provided
                if model_name_or_class is None:
                    model_name_or_class = pretrained_model_name_or_path
                osft_config = auto_generate_target_osft_config(
                    model, 
                    model_name_or_class=model_name_or_class,
                    target_patterns=target_patterns,
                    rank_ratio=rank_ratio
                )

            model.osft_config = osft_config

            # Decompose weights into high/low rank components
            if initialize_osft:
                log_rank_0("\033[33m!!!! reinitialize_osft !!!!\033[0m")
                model.reinitialize_osft(decompose_existing_weights=True)
            return model

        def reinitialize_osft(
            self, decompose_existing_weights: bool, assigned_params=None
        ):
            """
            Reinitializes the OSFT decomposition (e.g., when learning a new task in continual learning).

            Arguments:
                decompose_existing_weights (bool):
                    When true, the targeted weights are decomposed to create the OSFT params.
                    Otherwise, we simply create parameters with the expected shapes.
                assigned_params (list, optional):
                    List of (name, param) tuples to process. If None, processes all parameters.
            """
            self.name_mapping = {}
            self.osft_params = nn.ModuleDict()
            self._initialize_osft_parameters(
                decompose_existing_weights=decompose_existing_weights,
                assigned_params=assigned_params,
            )

        def reinitialize_osft_distributed(self):
            """
            Reinitializes OSFT using distributed SVD computation across all ranks.
            Each rank computes SVD for a subset of parameters and then broadcasts results.
            """
            if not torch.distributed.is_initialized():
                # Fall back to single-process initialization
                self.reinitialize_osft(decompose_existing_weights=True)
                return

            world_size = torch.distributed.get_world_size()
            global_rank = torch.distributed.get_rank()

            # Step 1: Determine which parameters will be decomposed
            target_params = get_osft_target_parameters(self, self.osft_config)

            # Step 2: Partition work across ranks
            assignments = partition_svd_computation(target_params, world_size)

            # Step 3: Each rank initializes dummy parameters for all target params
            # but only computes SVD for its assigned parameters
            self.name_mapping = {}
            self.osft_params = nn.ModuleDict()

            # Initialize all target parameters with dummy values first
            for name, param in target_params:
                # if (
                #     len(param.shape) == 2
                #     and name in self.osft_config
                #     and self.osft_config[name] > 0
                # ):
                top_k = self.osft_config[name]
                svd_dict = create_svd_dict(
                    param.data,
                    top_k=top_k,
                    decompose_existing=False,  # Create dummy parameters
                    upcast_dtype=self.upcast_dtype,
                    output_dtype=self.output_dtype,
                )
                safe_name = name.replace(".", "_")
                self.name_mapping[name] = safe_name

                # Register buffers and parameters
                self.register_buffer(f"{safe_name}_U_high", svd_dict["U_high"])
                self.register_buffer(f"{safe_name}_S_high", svd_dict["S_high"])
                self.register_buffer(f"{safe_name}_V_high", svd_dict["V_high"])

                module_svd = nn.Module()
                module_svd.U_low = svd_dict["U_low"]
                module_svd.S_low = svd_dict["S_low"]
                module_svd.V_low = svd_dict["V_low"]
                module_svd.rank_high = svd_dict["rank_high"]
                module_svd.safe_name = safe_name
                self.osft_params[safe_name] = module_svd

                # Replace forward method
                mod, attr = self._get_module_by_name(name)
                bias = mod.bias if hasattr(mod, "bias") else None

                def make_forward(sn, bias):
                    def forward(x):
                        svd_dict = self.get_svd_dict(sn)
                        return self._factorized_linear(x, svd_dict, bias)

                    return forward

                mod.forward = make_forward(safe_name, bias)
                param.requires_grad = False
                mod._parameters.pop(attr, None)

            # Step 4: Each rank computes SVD for its assigned parameters
            assigned_params = assignments[global_rank]
            if assigned_params:
                self._initialize_osft_parameters(
                    decompose_existing_weights=True, assigned_params=assigned_params
                )

            # Step 5: Broadcast results from each rank
            # It's possible for processes to be dysynchronized by this point due to the
            # uneven split of work when processing model layers in parallel.
            # So here we ensure that everything is synchronized before proceeding.
            check_distributed_is_synchronized() 
            broadcast_svd_results(self, assignments, world_size)
            torch.distributed.barrier()

            torch.cuda.empty_cache()

        def _get_module_by_name(self, name):
            """Helper to traverse and retrieve a module and its attribute by name string (e.g., `model.layers.0.attn.q_proj.weight`)."""
            parts = name.split(".")
            attr = parts[-1]
            mod = self
            for p in parts[:-1]:
                if hasattr(mod, p):
                    mod = getattr(mod, p)
                elif p.isdigit():
                    mod = mod[int(p)]
                else:
                    return None, None
            return mod, attr

        def _initialize_osft_parameters(
            self, decompose_existing_weights: bool, assigned_params=None
        ):
            """
            Applies SVD decomposition to targeted parameters for OSFT and replaces their forward logic.

            This is the key transformation that enables constrained full-parameter updates by:
            - Freezing high-rank components
            - Training only low-rank ones
            - Intercepting the forward pass to use the reconstructed matrix

            Arguments:
                decompose_existing_weights (bool):
                    When true, the targeted weights are decomposed to create the OSFT params.
                    Otherwise, we simply create parameters with the expected shapes.
                assigned_params (list, optional):
                    List of (name, param) tuples to process. If None, processes all parameters.
            """
            local_rank = int(os.getenv("LOCAL_RANK", 0))

            # If assigned_params is provided, only process those parameters
            if assigned_params is not None:
                named_params = assigned_params
            else:
                named_params = list(self.named_parameters())

            # Show progress bar only on the rank doing the work
            if assigned_params is not None and len(assigned_params) > 0:
                if torch.distributed.is_initialized():
                    global_rank = torch.distributed.get_rank()
                    named_params = tqdm(
                        named_params,
                        total=len(named_params),
                        desc=f"[OSFT Init Rank {global_rank}, Local Rank {local_rank}] Decomposing params",
                    )
                else:
                    named_params = tqdm(
                        named_params,
                        total=len(named_params),
                        desc="[OSFT Init] Decomposing params",
                    )

            log_rank_0("\033[33m!!!! Initializing OSFT Params!!!!\033[0m")
            for name, param in named_params:
                # Apply SVD only to 2D matrices in the target config (e.g., q_proj, down_proj, etc.)
                if is_osft_param(name, param, self.osft_config):
                    top_k = self.osft_config[name]
                    # log_rank_0(f"[OSFT Init] Decomposing {name} with top_k={top_k}")
                    svd_dict = create_svd_dict(
                        param.data,
                        top_k=top_k,
                        decompose_existing=decompose_existing_weights,
                        upcast_dtype=self.upcast_dtype,
                        output_dtype=self.output_dtype,
                    )
                    safe_name = name.replace(
                        ".", "_"
                    )  # Required for buffer/module naming in PyTorch
                    self.name_mapping[name] = safe_name

                    # Freeze top-k singular directions (U/S/V_high)
                    self.register_buffer(f"{safe_name}_U_high", svd_dict["U_high"])
                    self.register_buffer(f"{safe_name}_S_high", svd_dict["S_high"])
                    self.register_buffer(f"{safe_name}_V_high", svd_dict["V_high"])

                    # Wrapper to hold trainable components
                    module_svd = nn.Module()
                    module_svd.U_low = svd_dict["U_low"]
                    module_svd.S_low = svd_dict["S_low"]
                    module_svd.V_low = svd_dict["V_low"]
                    module_svd.rank_high = svd_dict["rank_high"]
                    module_svd.safe_name = safe_name
                    self.osft_params[safe_name] = module_svd

                    mod, attr = self._get_module_by_name(name)
                    bias = mod.bias if hasattr(mod, "bias") else None

                    # Override linear projection with dynamic reconstruction
                    def make_forward(sn, bias):
                        def forward(x):
                            svd_dict = self.get_svd_dict(sn)
                            return self._factorized_linear(x, svd_dict, bias)
                        return forward

                    mod.forward = make_forward(safe_name, bias)
                    param.requires_grad = False
                    # Remove original parameter so it doesn't get updated
                    mod._parameters.pop(attr, None)
                    torch.cuda.empty_cache()

            # Barrier for synchronization in distributed setting
            if dist.is_initialized():
                torch.distributed.barrier()

        def _reconstruct_weight_by_safe_name(
            self,
            safe_name,
            upcast_dtype: torch.dtype | None = None,
            output_dtype: torch.dtype | None = None,
        ):
            """
            Reconstructs a decomposed weight matrix from saved buffers + trainable low-rank parameters
            to rebuild the full matrix used in forward.
            """
            upcast_dtype = (
                upcast_dtype if upcast_dtype is not None else self.upcast_dtype
            )
            output_dtype = (
                output_dtype if output_dtype is not None else self.output_dtype
            )

            svd_dict = self.get_svd_dict(safe_name)
            return reconstruct_weight_matrix(
                svd_dict,
                upcast_dtype=upcast_dtype,
                output_dtype=output_dtype,
            )

        def _reconstruct_weight(
            self,
            original_name,
            upcast_dtype: torch.dtype | None = None,
            output_dtype: torch.dtype | None = None,
        ):
            """Convenience wrapper to reconstruct using the original parameter name."""
            return self._reconstruct_weight_by_safe_name(
                self.name_mapping[original_name],
                upcast_dtype=upcast_dtype,
                output_dtype=output_dtype,
            )

        def _factorized_linear(self, x, svd_dict, bias=None):
            """
            Memory-efficient factorized linear operation using SVD components.
            
            Computes: x @ (U_high @ S_high @ V_high + U_low @ S_low @ V_low)
            As: (x @ V_high.T) @ (S_high @ U_high.T) + (x @ V_low.T) @ (S_low @ U_low.T)
            
            This avoids reconstructing the full weight matrix, using only rank-sized intermediates.
            Handles both 2D and 3D input tensors (batch_size, seq_len, hidden_dim).
            """
            U_high = svd_dict["U_high"]
            S_high = svd_dict["S_high"]
            V_high = svd_dict["V_high"]
            U_low = svd_dict["U_low"]
            S_low = svd_dict["S_low"]
            V_low = svd_dict["V_low"]
            
            # Ensure all tensors are on the same device and dtype as input
            device = x.device
            dtype = x.dtype
            
            # Handle both 2D and 3D input tensors
            original_shape = x.shape
            if x.dim() == 3:
                # Flatten 3D input [batch, seq, hidden] -> [batch*seq, hidden] 
                batch_size, seq_len, hidden_dim = x.shape
                x_flat = x.view(-1, hidden_dim)
            elif x.dim() == 2:
                x_flat = x
                batch_size, seq_len = None, None
            else:
                raise ValueError(f"Input tensor must be 2D or 3D, got {x.dim()}D")
            
            # Cast to appropriate dtypes for computation
            upcast_dtype = self.upcast_dtype
            target_dtype = dtype
            
            # High-rank component: x @ V_high.T @ (S_high @ U_high.T)
            result = None
            if U_high.numel() > 0 and S_high.numel() > 0:
                # Cast to upcast dtype for numerical stability
                V_high_work = V_high.to(device=device, dtype=upcast_dtype)
                U_high_work = U_high.to(device=device, dtype=upcast_dtype)
                S_high_work = S_high.to(device=device, dtype=upcast_dtype)
                x_work = x_flat.to(upcast_dtype)
                
                # x @ V_high.T -> intermediate shape: (batch*seq, rank_high)
                x_V = torch.mm(x_work, V_high_work.transpose(0, 1))
                # (x @ V_high.T) @ (S_high @ U_high.T) -> final shape: (batch*seq, output_dim)
                high_contrib = torch.mm(x_V * S_high_work.unsqueeze(0), U_high_work.transpose(0, 1))
                result = high_contrib.to(target_dtype)
            
            # Low-rank component: x @ V_low.T @ (S_low @ U_low.T)
            if U_low.numel() > 0 and S_low.numel() > 0:
                # Cast to upcast dtype for numerical stability
                V_low_work = V_low.to(device=device, dtype=upcast_dtype)
                U_low_work = U_low.to(device=device, dtype=upcast_dtype)
                S_low_work = S_low.to(device=device, dtype=upcast_dtype)
                x_work = x_flat.to(upcast_dtype)
                
                # x @ V_low.T -> intermediate shape: (batch*seq, rank_low)
                x_V = torch.mm(x_work, V_low_work.transpose(0, 1))
                # (x @ V_low.T) @ (S_low @ U_low.T) -> final shape: (batch*seq, output_dim)
                low_contrib = torch.mm(x_V * S_low_work.unsqueeze(0), U_low_work.transpose(0, 1))
                low_contrib = low_contrib.to(target_dtype)
                
                if result is not None:
                    result = result + low_contrib
                else:
                    result = low_contrib
            
            # Handle case where both components are empty (shouldn't happen in practice)
            if result is None:
                # Create zero output with correct shape
                output_dim = U_high.size(0) if U_high.numel() > 0 else U_low.size(0)
                result = torch.zeros(x_flat.size(0), output_dim, device=device, dtype=target_dtype)
            
            # Add bias if present
            if bias is not None:
                bias_work = bias.to(device=device, dtype=target_dtype)
                result = result + bias_work.unsqueeze(0)
            
            # Restore original shape if input was 3D
            if len(original_shape) == 3:
                output_dim = result.size(-1)
                result = result.view(batch_size, seq_len, output_dim)
            
            return result

        def get_svd_dict(self, safe_name: str) -> SVDDecompositionDict:
            if safe_name not in self.osft_params:
                raise ValueError(f'{safe_name} doesnt exist in the OSFT parameters')

            module_svd = self.osft_params[safe_name]

            # we infer rank_high since it's just the number of high singular values
            S_high = getattr(self, f"{safe_name}_S_high") 
            rank_high = S_high.shape[0]  

            svd_dict: SVDDecompositionDict = {
                "U_high": getattr(self, f"{safe_name}_U_high"),
                "S_high": S_high,
                "V_high": getattr(self, f"{safe_name}_V_high"),
                "U_low": module_svd.U_low,
                "S_low": module_svd.S_low,
                "V_low": module_svd.V_low,
                "rank_high": rank_high
            }
            return svd_dict

        def project_gradients(self):
            """
            Applies orthogonal projection to gradients of low-rank components to avoid interfering
            with the high-rank subspace encoding prior task knowledge.

            This method should be called after backpropagation and before optimizer step.
            """
            for safe_name in self.osft_params.keys():
                svd_dict = self.get_svd_dict(safe_name)
                project_gradient_to_orthogonal_space(svd_dict)

        def prepare_state_dict_for_save(self, state_dict):
            """Reconstruct dense weights into ``state_dict`` for saving with memory optimization."""
            if not hasattr(self, "name_mapping"):
                return state_dict
            
            log_rank_0("Reconstructing OSFT weights for checkpoint saving...")
            
            # Process parameters one at a time to minimize peak memory usage
            main_local_rank = int(os.getenv("LOCAL_RANK", 0))
            for i, (orig, safe) in enumerate(
                tqdm(
                    self.name_mapping.items(),
                    desc="Reconstructing OSFT weights, this may take a while...",
                    disable=main_local_rank != 0,
                )
            ):
                # Extract SVD components
                U_high = state_dict.pop(f"{safe}_U_high")
                S_high = state_dict.pop(f"{safe}_S_high")
                V_high = state_dict.pop(f"{safe}_V_high")
                U_low = state_dict.pop(f"osft_params.{safe}.U_low")
                S_low = state_dict.pop(f"osft_params.{safe}.S_low")
                V_low = state_dict.pop(f"osft_params.{safe}.V_low")
                W = reconstruct_weight_matrix(
                    {
                        "U_high": U_high,
                        "S_high": S_high,
                        "V_high": V_high,
                        "U_low": U_low,
                        "S_low": S_low,
                        "V_low": V_low,
                    },
                    output_dtype=self.dtype,
                    upcast_dtype=self.upcast_dtype,
                )
                state_dict[orig] = W
                
                # Explicitly delete intermediate tensors to free memory
                del U_high, S_high, V_high, U_low, S_low, V_low
                
                # Clear GPU cache every few parameters to prevent accumulation
                if (i + 1) % OSFT_CACHE_CLEAR_INTERVAL == 0:
                    torch.cuda.empty_cache()
                    log_rank_0(f"Processed {i + 1}/{len(self.name_mapping)} OSFT parameters")
            
            # Final cleanup
            torch.cuda.empty_cache()
            log_rank_0(f"Finished reconstructing {len(self.name_mapping)} OSFT parameters")
            
            return state_dict

    ModelWithOSFT.__name__ = f"{base_cls.__name__}WithOSFT"
    return ModelWithOSFT


def optim_wrapper(optimizer, model):
    """Wrap optimizer.step to project gradients before each update."""
    if not hasattr(model, "project_gradients"):
        return optimizer

    import types
    orig_step = optimizer.step

    def step(self, *args, **kwargs):
        model.project_gradients()
        return orig_step(*args, **kwargs)

    optimizer.step = types.MethodType(step, optimizer)
    return optimizer


