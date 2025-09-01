# CGO Library Main Makefile
# Orchestrates building of all CGO modules

.PHONY: all clean build test cgo-ffi cgo-stdio dirs

# Create directories
dirs:
	@mkdir -p cgo_lib/bin cgo_lib/headers

# Build CGO FFI module
cgo-ffi: dirs
	@echo "=== Building CGO FFI Module ==="
	$(MAKE) -C cgo_lib/cgo_ffi build

# Build CGO Stdio module  
cgo-stdio: dirs
	@echo "=== Building CGO Stdio Module ==="
	$(MAKE) -C cgo_lib/cgo_stdio build

# Build all modules
all: cgo-ffi cgo-stdio

# Demo the CGO library
demo: all
	@echo "=== Running CGO Library Demo ==="
	python cgo_demo.py

# Test all modules
test:
	@echo "=== Testing CGO FFI Module ==="
	$(MAKE) -C cgo_lib/cgo_ffi test
	@echo "=== Testing CGO Stdio Module ==="
	$(MAKE) -C cgo_lib/cgo_stdio test

# Clean all build artifacts
clean:
	@echo "Cleaning all CGO modules..."
	$(MAKE) -C cgo_lib/cgo_ffi clean
	$(MAKE) -C cgo_lib/cgo_stdio clean
	rm -rf cgo_lib/bin cgo_lib/headers __pycache__

# Initialize Go module (run once)  
init:
	go mod init steelcalc
	go mod tidy
