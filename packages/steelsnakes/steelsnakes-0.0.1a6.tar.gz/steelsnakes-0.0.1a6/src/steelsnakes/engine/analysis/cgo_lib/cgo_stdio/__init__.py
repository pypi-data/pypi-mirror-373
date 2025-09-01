"""
CGO Stdio Module

Provides Python interface to Go binaries via stdin/stdout communication.
Uses subprocess calls with JSON data exchange for process isolation.
"""

from .stdio_wrapper import SteelCalculatorStdio, calculate_via_stdio

__all__ = ['SteelCalculatorStdio', 'calculate_via_stdio']


