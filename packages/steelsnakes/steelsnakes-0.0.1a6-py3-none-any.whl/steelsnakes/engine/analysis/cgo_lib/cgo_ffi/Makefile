# CGO FFI Module Makefile
# Builds Go shared library for FFI integration

.PHONY: all clean build

# Build shared library
build:
	@echo "Building CGO FFI shared library..."
	@mkdir -p ../bin ../headers
	go build -buildmode=c-shared -o ../bin/libsimple.so steel_calc.go
	@mv ../bin/libsimple.h ../headers/ 2>/dev/null || true
	@echo "Built ../bin/libsimple.so with ../headers/libsimple.h"

# Test the FFI wrapper
test:
	@echo "Testing CGO FFI wrapper..."
	python ffi_wrapper.py

# Clean build artifacts
clean:
	rm -f ../bin/libsimple.* ../headers/libsimple.h

all: build
