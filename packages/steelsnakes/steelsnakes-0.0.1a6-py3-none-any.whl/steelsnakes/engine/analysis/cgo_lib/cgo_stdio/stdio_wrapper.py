"""
Stdio Wrapper for Go Steel Calculations

Provides Python interface to Go binary via stdin/stdout communication.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any

class SteelCalculatorStdio:
    """Python interface to Go steel calculation binary via stdio."""
    
    def __init__(self):
        self.binary_path = self._find_binary()
    
    def _find_binary(self) -> Path:
        """Find the Go binary in the cgo_lib bin directory."""
        bin_dir = Path(__file__).parent.parent / "bin"
        binary_path = bin_dir / "stdio_calc"
        
        if not binary_path.exists():
            raise FileNotFoundError(
                f"Steel calculation binary not found: {binary_path}\n"
                f"Run 'make cgo-stdio' to build the binary"
            )
        
        return binary_path
    
    def calculate_moment_resistance(self, section_modulus: float, yield_strength: float) -> Dict[str, Any]:
        """
        Calculate moment resistance for a steel section.
        
        Args:
            section_modulus: Section modulus (cm³)
            yield_strength: Yield strength (N/mm²)
        
        Returns:
            Dict containing calculation results
        """
        # Prepare input data
        input_data = {
            "section_modulus": section_modulus,
            "yield_strength": yield_strength
        }
        
        try:
            # Call Go binary with JSON input
            process = subprocess.run(
                [str(self.binary_path)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse JSON output
            result = json.loads(process.stdout)
            return result
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Go binary execution failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Go binary output: {e}")
        except Exception as e:
            raise RuntimeError(f"Stdio calculation failed: {e}")


# Convenience function for easy import
def calculate_via_stdio(section_modulus: float, yield_strength: float) -> Dict[str, Any]:
    """Convenience function for steel moment calculation via stdio."""
    calculator = SteelCalculatorStdio()
    return calculator.calculate_moment_resistance(section_modulus, yield_strength)


if __name__ == "__main__":
    # Example usage
    print("=== Testing Steel Calculator Stdio ===")
    
    try:
        result = calculate_via_stdio(6420.0, 355.0)
        print("Calculation successful!")
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        print("To test stdio: run 'make cgo-stdio' in the analysis directory")
