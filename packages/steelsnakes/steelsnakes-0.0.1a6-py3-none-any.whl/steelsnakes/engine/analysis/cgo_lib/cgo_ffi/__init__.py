"""
CGO FFI (Foreign Function Interface) Module

Provides Python interface to Go shared libraries via ctypes.
Uses shared libraries (.so/.dll/.dylib) for zero-copy performance.
"""

from .ffi_wrapper import SteelCalculatorFFI, calculate_steel_moment

__all__ = ['SteelCalculatorFFI', 'calculate_steel_moment']
