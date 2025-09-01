# CGO Stdio Module Makefile  
# Builds Go binary for stdio communication

.PHONY: all clean build

# Build standalone binary
build:
	@echo "Building CGO stdio binary..."
	@mkdir -p ../bin
	go build -o ../bin/stdio_calc steel_calc.go
	@echo "Built ../bin/stdio_calc"

# Test the stdio wrapper
test:
	@echo "Testing CGO stdio wrapper..."
	python stdio_wrapper.py

# Clean build artifacts
clean:
	rm -f ../bin/stdio_calc

all: build
