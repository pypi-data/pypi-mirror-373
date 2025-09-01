"""
FFI Wrapper for Go Steel Calculations

Provides Python interface to Go shared library via ctypes.
"""

import ctypes
import json
import platform
from pathlib import Path
from typing import Dict, Any

class SteelCalculatorFFI:
    """Python interface to Go steel calculation library via FFI."""
    
    def __init__(self) -> None:
        self.lib = None
        self._load_library()
    
    def _load_library(self) -> None:
        """Load the appropriate shared library for the current platform."""
        
        # Find library in cgo_lib bin directory
        bin_dir: Path = Path(__file__).parent.parent / "bin"
        
        # Determine library name based on platform
        system: str = platform.system().lower()
        if system == "linux":
            lib_name = "libsimple.so"
        elif system == "darwin":  # macOS
            lib_name = "libsimple.dylib"
        elif system == "windows":
            lib_name = "libsimple.dll"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
        
        lib_path: Path = bin_dir / lib_name
        
        if not lib_path.exists():
            raise FileNotFoundError(
                f"Steel calculation library not found: {lib_path}\n"
                f"Run 'make cgo-ffi' to build the library"
            )
        
        try:
            self.lib = ctypes.CDLL(str(lib_path))
            self._setup_function_signatures()
        except Exception as e:
            raise RuntimeError(f"Failed to load library {lib_path}: {e}")
    
    def _setup_function_signatures(self) -> None:
        """Set up function signatures for type safety."""
        if not self.lib:
            raise RuntimeError("Library not loaded")
        self.lib.calculate.argtypes = [ctypes.c_char_p]
        self.lib.calculate.restype = ctypes.c_char_p
    
    def calculate_moment_resistance(self, section_modulus: float, yield_strength: float) -> Dict[str, Any]:
        """
        Calculate moment resistance for a steel section.
        
        Args:
            section_modulus: Section modulus (cm³)
            yield_strength: Yield strength (N/mm²)
        
        Returns:
            Dict containing calculation results
        """
        if not self.lib:
            raise RuntimeError("Library not loaded")
        
        # Prepare input
        input_data = {
            "section_modulus": section_modulus,
            "yield_strength": yield_strength
        }
        
        # Convert to JSON string
        json_input = json.dumps(input_data).encode('utf-8')
        
        # Call Go function
        result_ptr = self.lib.calculate(json_input)
        result_bytes = ctypes.c_char_p(result_ptr).value
        
        if result_bytes is None:
            raise RuntimeError("Go function returned null pointer")
        
        result_str = result_bytes.decode('utf-8')
        
        # Parse JSON result
        return json.loads(result_str)


# Convenience function for easy import
def calculate_steel_moment(section_modulus: float, yield_strength: float) -> Dict[str, Any]:
    """Convenience function for steel moment calculation via FFI."""
    calculator = SteelCalculatorFFI()
    return calculator.calculate_moment_resistance(section_modulus, yield_strength)


if __name__ == "__main__":
    # Example usage
    print("=== Testing Steel Calculator FFI ===")
    
    try:
        result = calculate_steel_moment(6420.0, 355.0)
        print("Calculation successful!")
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        print("To test FFI: run 'make cgo-ffi' in the analysis directory")
