# Makefile for go-bm25 package

# Set CGO flags to avoid deprecated -Ofast flag and use gcc
export CGO_CFLAGS=-Wno-deprecated-declarations
export CC=gcc
# Detect architecture automatically
export CGO_ENABLED=1
export PATH := /usr/local/go/bin:$(PATH)

# Detect Python executable (python3, python, or py)
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || command -v py 2>/dev/null || echo python3)
PIP := $(shell command -v pip3 2>/dev/null || command -v pip 2>/dev/null || echo pip3)

.PHONY: help clean build install test publish clean-python build-python install-python

# Default target
help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  clean        - Clean all build artifacts"
	@echo "  build        - Build Go bindings and Python package"
	@echo "  build-go-bindings - Generate Go Python bindings only"
	@echo "  build-python - Build Python package only"
	@echo "  install      - Install package in development mode"
	@echo "  test         - Run tests"
	@echo "  test-bindings - Test Python bindings with Go library"
	@echo "  publish      - Build and publish to PyPI (requires credentials)"
	@echo "  clean-python - Clean Python build artifacts only"
	@echo "  clean-go-bindings - Clean Go bindings only"
	@echo "  install-python - Install Python package only"

# Clean all build artifacts
clean: clean-python clean-go-bindings
	@echo "Cleaning complete"

# Clean Go bindings
clean-go-bindings:
	@echo "Cleaning Go build artifacts..."
	cd bm25 && rm -rf *.so *.dylib *.c *.h __pycache__/ build/ dist/ *.egg-info/ 2>/dev/null || true
	@echo "Go bindings cleaned"

# Clean Python build artifacts only
clean-python:
	@echo "Cleaning Python build artifacts..."
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Python build artifacts cleaned"

# Build Go bindings and Python package
build: build-go-bindings build-python
	@echo "Build complete"

# Build Go bindings
build-go-bindings:
	@echo "Building Go shared library..."
	mkdir -p bm25
	@echo "Detected OS: $(shell uname -s)"
	@echo "Detected architecture: $(shell uname -m)"
	@echo "Go version: $(shell go version 2>/dev/null || echo "Go not found")"
ifeq ($(shell uname -s),Darwin)
	@echo "Building for macOS..."
	env PATH="/usr/local/go/bin:$$PATH" CGO_CFLAGS="-O3 -Wno-deprecated-declarations" go build -buildmode=c-shared -o bm25/libbm25.dylib bm25.go main.go
	@echo "Created libbm25.dylib for macOS"
else
	@echo "Building for Linux..."
	env PATH="/usr/local/go/bin:$$PATH" CGO_CFLAGS="-O3 -Wno-deprecated-declarations" go build -buildmode=c-shared -o bm25/libbm25.so bm25.go main.go
	@echo "Created libbm25.so for Linux"
endif
	@echo "Python wrapper ready - use ctypes to access Go library"

# Build Python package only
build-python: build-go-bindings
	@echo "Building Python package using $(PYTHON)..."
	$(PYTHON) -m build
	@echo "Python package built successfully"

# Install package in development mode
install: build-python
	@echo "Installing package in development mode using $(PIP)..."
	$(PIP) install -e .
	@echo "Package installed successfully"

# Install Python package only
install-python: build-python
	@echo "Installing Python package in development mode using $(PIP)..."
	$(PIP) install -e .
	@echo "Python package installed successfully"

# Run tests
test:
	@echo "Running tests using $(PYTHON)..."
	$(PYTHON) -m pytest tests/ -v
	@echo "Tests complete"

# Build and publish to PyPI (requires credentials)
publish: clean build-python
	@echo "Publishing to PyPI using $(PYTHON)..."
	$(PYTHON) -m twine upload dist/*
	@echo "Package published successfully"

# Development setup
dev-setup:
	@echo "Setting up development environment using $(PIP)..."
	$(PIP) install -e ".[dev]"
	@echo "Development environment setup complete"

# Check package
check:
	@echo "Checking package using $(PYTHON)..."
	$(PYTHON) -m build --check
	@echo "Package check complete"

# Show package info
info:
	@echo "Package information:"
	@$(PYTHON) -c "import bm25; print(f'Version: {bm25.__version__}')" 2>/dev/null || echo "Package not installed"

# Test Python bindings
test-bindings:
	@echo "Testing Python bindings using $(PYTHON)..."
	@$(PYTHON) -c "import bm25; print('✓ BM25 package imported successfully'); print(f'✓ Version: {bm25.__version__}')" 2>/dev/null || echo "✗ Failed to import BM25 package"
	@echo "Testing Go library connection..."
	@$(PYTHON) -c "import bm25; result = bm25.hello_bm25(); print(f'✓ Go library response: {result}')" 2>/dev/null || echo "✗ Failed to connect to Go library"
	


