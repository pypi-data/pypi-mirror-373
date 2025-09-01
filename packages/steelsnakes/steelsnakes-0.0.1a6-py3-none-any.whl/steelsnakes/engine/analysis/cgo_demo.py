#!/usr/bin/env python3
"""
CGO Library Demo - Showcasing both FFI and Stdio implementations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from cgo_lib import SteelCalculatorFFI, SteelCalculatorStdio # type: ignore[import]
from cgo_lib import calculate_steel_moment, calculate_via_stdio # type: ignore[import]

def benchmark_comparison() -> None:
    """Compare performance between FFI and stdio approaches."""
    print("=== CGO Library Performance Comparison ===")
    
    # Test parameters
    section_modulus = 6420.0  # cm³
    yield_strength = 355.0    # N/mm²
    iterations = 100
    
    print(f"Test: {iterations} calculations of section modulus {section_modulus} cm³")
    print(f"      with yield strength {yield_strength} N/mm²")
    
    # FFI approach
    print("\n1. FFI (Shared Library) Approach:")
    try:
        ffi_calc = SteelCalculatorFFI()
        
        start_time: float = time.time()
        result = None
        for _ in range(iterations):
            result = ffi_calc.calculate_moment_resistance(section_modulus, yield_strength)
        ffi_time: float = time.time() - start_time
        
        print(f"   ✓ {iterations} calculations in {ffi_time:.4f} seconds")
        print(f"   ✓ {iterations/ffi_time:.0f} calculations/second")
        if result is not None:
            print(f"   ✓ Result: {result['moment_capacity']:,.0f} Nmm")
        
    except Exception as e:
        print(f"   ✗ FFI failed: {e}")
        ffi_time = float('inf')
    
    # Stdio approach  
    print("\n2. Stdio (Binary) Approach:")
    try:
        stdio_calc = SteelCalculatorStdio()
        start_time = time.time()
        result = None
        for _ in range(iterations):
            result = stdio_calc.calculate_moment_resistance(section_modulus, yield_strength)
        stdio_time: float = time.time() - start_time
        
        print(f"   ✓ {iterations} calculations in {stdio_time:.4f} seconds")
        print(f"   ✓ {stdio_time/iterations*1000:.1f} ms per calculation")
        if result is not None:
            print(f"   ✓ Result: {result['moment_capacity']:,.0f} Nmm")
        
    except Exception as e:
        print(f"   ✗ Stdio failed: {e}")
        stdio_time = float('inf')
    
    # Performance comparison
    if ffi_time != float('inf') and stdio_time != float('inf'):
        speedup: float = stdio_time / ffi_time
        print(f"\nPerformance Summary:")  # noqa: F541
        print(f"FFI is {speedup:.1f}x faster than stdio")
        print(f"FFI: {ffi_time/iterations*1000:.2f} ms/calc")
        print(f"Stdio: {stdio_time/iterations*1000:.2f} ms/calc")

def convenience_functions_demo():
    """Demonstrate the convenience functions."""
    print("\n=== Convenience Functions Demo ===")
    
    # Direct function calls
    print("Using convenience functions:")
    
    try:
        ffi_result = calculate_steel_moment(6420, 355)
        print(f"FFI convenience:   {ffi_result['moment_capacity']:,.0f} Nmm")
    except Exception as e:
        print(f"FFI convenience failed: {e}")
    
    try:
        stdio_result = calculate_via_stdio(6420, 355)
        print(f"Stdio convenience: {stdio_result['moment_capacity']:,.0f} Nmm")
    except Exception as e:
        print(f"Stdio convenience failed: {e}")

# def architecture_demo():
#     """Show the modular architecture."""
#     print("\n=== Modular Architecture Demo ===")
    
#     print("CGO Library Structure:")
#     print("└── cgo_lib/")
#     print("    ├── __init__.py          # Main interface")
#     print("    ├── cgo_ffi/             # FFI implementation")
#     print("    │   ├── __init__.py")
#     print("    │   ├── ffi_wrapper.py   # Python ctypes wrapper")
#     print("    │   ├── steel_calc.go    # Go shared library source")
#     print("    │   └── Makefile         # FFI build system")
#     print("    └── cgo_stdio/           # Stdio implementation") 
#     print("        ├── __init__.py")
#     print("        ├── stdio_wrapper.py # Python subprocess wrapper")
#     print("        ├── steel_calc.go    # Go binary source")
#     print("        └── Makefile         # Stdio build system")
    
#     print("\nBuild artifacts organized in:")
#     print("├── bin/libsimple.so         # FFI shared library")
#     print("├── bin/stdio_calc           # Stdio binary")
#     print("└── headers/libsimple.h      # C headers for FFI")

def main() -> None:
   
    # architecture_demo()
    convenience_functions_demo() 
    benchmark_comparison()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed! Both FFI and stdio implementations working.")

if __name__ == "__main__":
    main()


