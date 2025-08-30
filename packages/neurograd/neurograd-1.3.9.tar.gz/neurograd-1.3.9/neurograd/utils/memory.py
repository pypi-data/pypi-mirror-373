"""
Lightweight, opt-in GPU memory monitor.

Usage:
    from neurograd.utils.memory import MemoryMonitor
    with MemoryMonitor():
        # run code; each NeuroGrad op logs a one-line memory snapshot

Default off: When not inside the context, overhead is near-zero
(a single boolean check per op).

Notes:
- On CUDA (CuPy), prints driver used VRAM, CuPy pool used/total, and optional FFT
  plan cache info if available.
- On CPU (NumPy), logs only the op tag without memory figures.
"""

from __future__ import annotations

import threading
from typing import Callable, Iterable, Optional


_TLS = threading.local()
_TLS.enabled = False
_TLS.print_fn = print  # type: ignore
_TLS.prefix = "[OP]"
_TLS.include_driver = True
_TLS.include_pool = True
_TLS.include_fft = False


def _get_backend() -> str:
    try:
        import neurograd as ng  # local import to avoid cycles

        return ng.DEVICE
    except Exception:
        return "cpu"


def _fmt_gb(x: float) -> str:
    return f"{x/1e9:.2f} GB"


def _gpu_stats() -> Optional[str]:
    if _get_backend() != "cuda":
        return None
    try:
        import cupy as cp  # type: ignore
    except Exception:
        return None

    parts = []
    try:
        if getattr(_TLS, "include_driver", True):
            free, total = cp.cuda.runtime.memGetInfo()
            used = total - free
            parts.append(f"drv used/total={_fmt_gb(used)}/{_fmt_gb(total)}")
    except Exception:
        pass

    try:
        if getattr(_TLS, "include_pool", True):
            mp = cp.get_default_memory_pool()
            used_b = mp.used_bytes()
            tot_b = mp.total_bytes()
            parts.append(f"pool used/total={_fmt_gb(used_b)}/{_fmt_gb(tot_b)}")
    except Exception:
        pass

    if getattr(_TLS, "include_fft", False):
        try:
            from cupyx.scipy import fft as cufft  # type: ignore

            pc = cufft.get_plan_cache()
            parts.append(f"fft plans={pc.get_size()} mem={_fmt_gb(pc.get_memsize())}")
        except Exception:
            pass

    return " | ".join(parts) if parts else None


def is_enabled() -> bool:
    return bool(getattr(_TLS, "enabled", False))


def maybe_log_op_memory(op_name: str, inputs: Iterable, output) -> None:
    """
    Fast no-op when disabled. Called by the Function machinery after each op.
    """
    if not is_enabled():
        return

    try:
        pf: Callable[[str], None] = getattr(_TLS, "print_fn", print)  # type: ignore
        prefix: str = getattr(_TLS, "prefix", "[OP]")  # type: ignore

        in_shapes = []
        for t in inputs or []:
            try:
                in_shapes.append(tuple(getattr(t, "shape", ())))
            except Exception:
                in_shapes.append(())
        out_shape = None
        try:
            out_shape = tuple(getattr(output, "shape", ()))
        except Exception:
            out_shape = ()

        gpu = _gpu_stats()
        msg = f"{prefix} {op_name}: in={in_shapes} -> out={out_shape}"
        if gpu:
            msg += f" | {gpu}"
        pf(msg)
    except Exception:
        # Never let diagnostics break the main path
        return


class MemoryMonitor:
    """Context manager to enable per-op memory logging."""

    def __init__(
        self,
        *,
        print_fn: Optional[Callable[[str], None]] = None,
        prefix: str = "[OP]",
        include_driver: bool = True,
        include_pool: bool = True,
        include_fft: bool = False,
    ) -> None:
        self._prev = {}
        self.print_fn = print_fn or print
        self.prefix = prefix
        self.include_driver = include_driver
        self.include_pool = include_pool
        self.include_fft = include_fft

    def __enter__(self):
        self._prev = {
            "enabled": getattr(_TLS, "enabled", False),
            "print_fn": getattr(_TLS, "print_fn", print),
            "prefix": getattr(_TLS, "prefix", "[OP]"),
            "include_driver": getattr(_TLS, "include_driver", True),
            "include_pool": getattr(_TLS, "include_pool", True),
            "include_fft": getattr(_TLS, "include_fft", False),
        }
        _TLS.enabled = True
        _TLS.print_fn = self.print_fn  # type: ignore
        _TLS.prefix = self.prefix
        _TLS.include_driver = self.include_driver
        _TLS.include_pool = self.include_pool
        _TLS.include_fft = self.include_fft
        return self

    def __exit__(self, exc_type, exc, tb):
        for k, v in self._prev.items():
            setattr(_TLS, k, v)
        return False


def log_point(tag: str) -> None:
    """Manual memory log marker."""
    if not is_enabled():
        return
    gpu = _gpu_stats()
    pf: Callable[[str], None] = getattr(_TLS, "print_fn", print)  # type: ignore
    prefix: str = getattr(_TLS, "prefix", "[OP]")  # type: ignore
    msg = f"{prefix} {tag}"
    if gpu:
        msg += f" | {gpu}"
    pf(msg)

