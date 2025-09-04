# -*- coding: utf-8 -*-
"""
OpenAlgo Python Library
"""

from .orders import OrderAPI
from .data import DataAPI
from .account import AccountAPI
from .strategy import Strategy
from .feed import FeedAPI
from .indicators import ta

# ------------------------------------------------------------------
# Speed patch: upgrade all legacy @jit decorators project-wide
# ------------------------------------------------------------------
from .numba_shim import jit as _jit_shim  # noqa: E402
import numba as _nb  # noqa: E402
from numba import prange as _prange  # noqa: E402

_nb.jit = _jit_shim  # monkey-patch once at import time

# Make shim available as openalgo.nbjit if users want it explicitly
nbjit = _jit_shim
prange = _prange

class api(OrderAPI, DataAPI, AccountAPI, FeedAPI):
    """
    OpenAlgo API client class
    """
    pass

__version__ = "1.0.30"

# Export main components for easy access
__all__ = ['api', 'Strategy', 'ta', 'nbjit', 'prange']
