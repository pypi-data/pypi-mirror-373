"""
AMP utilities with promote-only default, view/meta no-cast, and cast de-dup cache.
"""
from __future__ import annotations
import weakref
from typing import Set, Tuple, Dict, Optional
import neurograd as ng
from neurograd.tensor import Tensor
from .autocast import autocast

# ---- Policy buckets ---------------------------------------------------------

# Numerically sensitive ops that must run in FP32 end-to-end.
_FP32_OPS: Set[str] = {
    "log","exp","sqrt","cbrt","log10","log2",
    "sin","cos","tan",
    "softmax",
    "sum","mean","std","var",
    "batchnormalizer",
    "mse","rmse","mae","binarycrossentropy","categoricalcrossentropy",
    "cast",
    "pow",
}

# Ops that *benefit* from lower precision throughput (downcast if feasible).
_FP16_PREFERRED_OPS: Set[str] = {
    "add","sub","mul","div",
    "matmul","dot","linear","tensordot","einsum",
    # elementwise
    "abs","clip","max","min",
    # activations (excluding softmax)
    "relu","relu6","leakyrelu","sigmoid","tanh","passthrough",
    # padding can stay as is; if you really want it fp16, keep it here
    "pad",
}

# Pure view/meta ops: absolutely no casting (dtype-agnostic).
_VIEW_OR_META_OPS: Set[str] = {
    "reshape","flatten","squeeze","expanddims","transpose","slidingwindowview",
}

# Skip casting for very small tensors (bytes). Tweak as needed.
_MIN_CAST_BYTES = 4096

# ---- Small weak cache to avoid re-casting the same tensor repeatedly --------

# key: (id(source_tensor.data), target_dtype.name) -> weakref to casted Tensor
_CAST_CACHE: Dict[Tuple[int, str], "weakref.ReferenceType[Tensor]"] = {}

def _get_cached_cast(src: Tensor, target_dtype) -> Optional[Tensor]:
    key = (id(src.data), str(target_dtype))
    ref = _CAST_CACHE.get(key)
    if ref is not None:
        obj = ref()
        if obj is not None:
            return obj
        else:
            _CAST_CACHE.pop(key, None)
    return None

def _put_cached_cast(src: Tensor, casted: Tensor, target_dtype) -> None:
    key = (id(src.data), str(target_dtype))
    _CAST_CACHE[key] = weakref.ref(casted)

# Optional helper you can call at the start of each forward pass if you want:
def clear_autocast_cache():
    _CAST_CACHE.clear()

# ---- Decision helpers -------------------------------------------------------

class _Decision:
    KEEP = 0      # do not change dtype
    TO_FP16 = 1   # cast to autocast dtype (fp16/bf16)
    TO_FP32 = 2   # cast to fp32

def _decide(op_name: Optional[str]) -> int:
    if not op_name:
        return _Decision.KEEP
    name = op_name.lower()
    if name in _VIEW_OR_META_OPS:
        return _Decision.KEEP
    if name in _FP32_OPS:
        return _Decision.TO_FP32
    if name in _FP16_PREFERRED_OPS:
        return _Decision.TO_FP16
    # Unknown ops: keep dtype to prevent ping-pong
    return _Decision.KEEP

# ---- Public API (backwards-compatible helpers) ------------------------------

def should_cast_to_fp16(op_name: str) -> bool:
    """
    Kept for backwards compatibility but now reflects the promote-only policy:
    returns True only if op is in the FP16-preferred bucket.
    """
    if not autocast.is_enabled():
        return False
    return _decide(op_name) == _Decision.TO_FP16

def maybe_cast_tensor(tensor: object, target_dtype=None, op_name: str = "unknown") -> Tensor | object:
    """
    Cast tensor to appropriate dtype based on autocast policy.
    - View/meta ops never trigger casts.
    - Unknown ops keep dtype.
    - FP32 bucket promotes to float32.
    - FP16-preferred bucket casts to autocast dtype.
    - Tiny tensors skip casting.
    """
    if not isinstance(tensor, Tensor):
        return tensor

    if not autocast.is_enabled():
        return tensor

    # Non-float tensors: leave them alone
    dt = getattr(tensor.data, "dtype", None)
    if dt is None or dt.kind not in ("f",):  # float kinds only
        return tensor

    # Size guard
    if getattr(tensor.data, "nbytes", 0) < _MIN_CAST_BYTES:
        return tensor

    decision = _decide(op_name)

    # If caller explicitly asked a dtype, obey it (but still de-dup)
    if target_dtype is not None:
        if tensor.data.dtype == target_dtype:
            return tensor
        cached = _get_cached_cast(tensor, target_dtype)
        if cached is not None:
            return cached
        out = tensor.cast(target_dtype)
        _put_cached_cast(tensor, out, target_dtype)
        return out

    # Otherwise, follow policy
    if decision == _Decision.KEEP:
        return tensor
    elif decision == _Decision.TO_FP32:
        if tensor.data.dtype == ng.float32:
            return tensor
        cached = _get_cached_cast(tensor, ng.float32)
        if cached is not None:
            return cached
        out = tensor.cast(ng.float32)
        _put_cached_cast(tensor, out, ng.float32)
        return out
    else:  # TO_FP16
        ac_dtype = autocast.get_autocast_dtype()
        if tensor.data.dtype == ac_dtype:
            return tensor
        cached = _get_cached_cast(tensor, ac_dtype)
        if cached is not None:
            return cached
        out = tensor.cast(ac_dtype)
        _put_cached_cast(tensor, out, ac_dtype)
        return out

def get_fp32_ops() -> Set[str]:
    return _FP32_OPS.copy()

def get_fp16_safe_ops() -> Set[str]:
    # kept for compatibility; returns the preferred set
    return _FP16_PREFERRED_OPS.copy()

def add_fp32_op(op_name: str) -> None:
    _FP32_OPS.add(op_name.lower())

def add_fp16_safe_op(op_name: str) -> None:
    _FP16_PREFERRED_OPS.add(op_name.lower())

def remove_fp32_op(op_name: str) -> None:
    _FP32_OPS.discard(op_name.lower())

def remove_fp16_safe_op(op_name: str) -> None:
    _FP16_PREFERRED_OPS.discard(op_name.lower())
