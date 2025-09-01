# Analysis Engine

High-performance steel calculations using Go binaries integrated with Python, following the Polars model of shipping native binaries for performance-critical operations. The analysis engine provides two approaches for calling Go from Python: **FFI** (Foreign Function Interface) for maximum performance, and **stdio** for process isolation. Both use JSON for seamless data exchange.

1. Cgo and Python (Datadog) <https://www.datadoghq.com/blog/engineering/cgo-and-python/>
2. Faster Python with Go shared objects (kchung) <https://blog.kchung.co/faster-python-with-go-shared-objects/>

```python
from cgo_lib import calculate_steel_moment, calculate_via_stdio

# High-performance FFI calculation (7.2x faster)
result = calculate_steel_moment(6420, 355)  # section_modulus, yield_strength
print(f"M_Rd = {result['moment_capacity']:,.0f} Nmm")

# Process-isolated stdio calculation  
result = calculate_via_stdio(6420, 355)
print(f"M_Rd = {result['moment_capacity']:,.0f} Nmm")
```

The analysis engine is built with the following structure:

```
cgo_lib/
├── cgo_ffi/          # FFI implementation (shared library)
├── cgo_stdio/        # Stdio implementation (binary) 
├── bin/              # Compiled artifacts
└── headers/          # C headers for external FFI
```

Both implementations provide identical Python interfaces but use different backend communication methods.

```bash
make all      # Build both FFI and stdio implementations
make demo     # Run performance comparison demo
make clean    # Clean all build artifacts
```

**Benchmark**: 100 calculations of moment resistance

- **FFI**: 0.38 ms/calculation (2613 calc/s) 
- **Stdio**: 2.76 ms/calculation (362 calc/s)

FFI is **7.2x faster** than stdio, while stdio provides better process isolation for safety-critical applications.

Works seamlessly with existing SteelSnakes section objects:

```python
from steelsnakes.UK.universal import UB
from cgo_lib import calculate_steel_moment

beam = UB(designation="762x267x197")
result = calculate_steel_moment(beam.W_el_yy, 355)
```

This demonstrates effective integration of compiled languages into Python packages for performance-critical operations.
