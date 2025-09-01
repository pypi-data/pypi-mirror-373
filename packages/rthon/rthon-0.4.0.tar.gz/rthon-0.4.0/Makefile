.PHONY: build clean test install dev-install help

# Default Python interpreter (use the miniforge3 one that's working)
PYTHON ?= /Users/samswitz/miniforge3/bin/python

help:
	@echo "Available targets:"
	@echo "  build        - Build the C extension"
	@echo "  clean        - Clean build artifacts"
	@echo "  test         - Run tests"
	@echo "  install      - Install the package"
	@echo "  dev-install  - Install in development mode"
	@echo "  integration  - Run integration tests"
	@echo "  help         - Show this help"

build:
	@echo "Building rthon C extension..."
	$(PYTHON) build_extension.py

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ src/**/*.so src/**/__pycache__/ **/*.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

test: build
	@echo "Running tests..."
	$(PYTHON) tests/test_lm.py

integration: build
	@echo "Running integration tests..."
	$(PYTHON) test_integration.py

install: build
	@echo "Installing rthon..."
	$(PYTHON) -m pip install .

dev-install: build
	@echo "Installing rthon in development mode..."
	$(PYTHON) -m pip install -e .

# Shortcut targets
c: clean
b: build
t: test
i: integration