"""
CGO Library Module - Go FFI Integration for SteelSnakes

This module provides Go language integration via CGO for high-performance
steel calculations, following the same pattern as Polars with Rust binaries.

Submodules:
- cgo_ffi: FFI (Foreign Function Interface) using shared libraries
- cgo_stdio: Stdio-based communication using standalone binaries
"""

from .cgo_ffi import SteelCalculatorFFI, calculate_steel_moment
from .cgo_stdio import SteelCalculatorStdio, calculate_via_stdio

__all__ = [
    'SteelCalculatorFFI',
    'calculate_steel_moment', 
    'SteelCalculatorStdio',
    'calculate_via_stdio'
]

__version__ = "0.1.0"
__author__ = "SteelSnakes Project"


