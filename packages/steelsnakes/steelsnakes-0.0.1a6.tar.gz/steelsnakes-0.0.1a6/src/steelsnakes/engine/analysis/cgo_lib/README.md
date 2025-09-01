# CGO Library Module

High-performance steel calculations using Go binaries called from Python, following the same pattern as Polars with Rust.

## Architecture

```
cgo_lib/
├── __init__.py                    # Main interface (SteelCalculatorFFI, SteelCalculatorStdio)
├── cgo_ffi/                       # FFI Implementation (7.2x faster)
│   ├── __init__.py               # FFI exports
│   ├── ffi_wrapper.py            # Python ctypes interface  
│   ├── steel_calc.go             # Go shared library source
│   └── Makefile                  # FFI build system
└── cgo_stdio/                    # Stdio Implementation (process isolation)
    ├── __init__.py               # Stdio exports
    ├── stdio_wrapper.py          # Python subprocess interface
    ├── steel_calc.go             # Go binary source  
    └── Makefile                  # Stdio build system
```

## Build Artifacts

```
analysis/
├── bin/
│   ├── libsimple.so              # FFI shared library (2.8MB)
│   └── stdio_calc*               # Stdio binary (2.7MB)
└── headers/
    └── libsimple.h               # C headers for external FFI
```

## Usage

### Quick Start

```python
# Import both implementations
from cgo_lib import SteelCalculatorFFI, SteelCalculatorStdio

# FFI approach (faster)
ffi_calc = SteelCalculatorFFI()
result = ffi_calc.calculate_moment_resistance(6420, 355)
# → {'moment_capacity': 2279100000, 'message': 'Success'}

# Stdio approach (isolated)
stdio_calc = SteelCalculatorStdio() 
result = stdio_calc.calculate_moment_resistance(6420, 355)
# → {'moment_capacity': 2279100000, 'message': 'Success'}
```

### Convenience Functions

```python
from cgo_lib import calculate_steel_moment, calculate_via_stdio

# One-liner FFI
result = calculate_steel_moment(6420, 355)

# One-liner stdio  
result = calculate_via_stdio(6420, 355)
```

## Building

```bash
# Build both implementations
make all

# Build specific implementation
make cgo-ffi     # FFI shared library
make cgo-stdio   # Stdio binary

# Test implementations
make test

# Clean all artifacts
make clean
```

## Performance

**Benchmark**: 100 calculations of M = S × fy × 1000

| Implementation | Time     | Speed        | Use Case                    |
|---------------|----------|--------------|----------------------------|
| **FFI**       | 0.038s   | 2613 calc/s  | High-frequency calculations |
| **Stdio**     | 0.276s   | 362 calc/s   | Process isolation, safety   |

**FFI is 7.2x faster** but stdio provides better isolation for untrusted calculations.

## Integration with SteelSnakes

```python
from steelsnakes.UK.universal import UB
from cgo_lib import calculate_steel_moment

# Get section from SteelSnakes
beam = UB(designation="762x267x197")

# High-performance calculation via Go
result = calculate_steel_moment(beam.W_el_yy, 355)
print(f"M_Rd = {result['moment_capacity']:,.0f} Nmm")
```

## JSON Interface

Both implementations use the same JSON interface:

**Input:**
```json
{
  "section_modulus": 6420.0,
  "yield_strength": 355.0
}
```

**Output:**
```json
{
  "moment_capacity": 2279100000,
  "message": "Success"
}
```

## Design Philosophy

1. **Performance**: Go provides 10-100x speedup over pure Python
2. **Modularity**: Separate FFI and stdio implementations  
3. **Compatibility**: Same interface, different backends
4. **Distribution**: Ship native binaries like Polars does
5. **Safety**: Stdio provides process isolation when needed

This demonstrates how to effectively integrate compiled languages into Python packages for performance-critical operations while maintaining Python's ease of use.


