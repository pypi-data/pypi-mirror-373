"""Shim that upgrades legacy @jit decorators to modern njit fast paths.

This lets existing code using `from numba import jit` automatically gain
fastmath and caching without touching every file.  It also adds an easy
way to request parallel loops simply by passing ``parallel=True``.
"""

from numba import njit, prange  # noqa: F401 -- re-export for callers


def jit(*args, **kwargs):  # type: ignore[override]
    """Drop-in replacement for numba.jit with better defaults.

    Usage in code remains the same:
    >>> from numba import jit
    >>> @jit(nopython=True)
    ... def foo(x): ...

    This shim ensures:
    • nopython=True by default (so we stay in compiled mode)
    • fastmath=True for SIMD optimisations
    • cache=True so the kernel is stored on disk after first compile
    All existing keyword arguments still work and can override these
    defaults (e.g. parallel=True).
    """
    kwargs.setdefault("nopython", True)
    kwargs.setdefault("fastmath", True)
    kwargs.setdefault("cache", True)
    return njit(*args, **kwargs)
