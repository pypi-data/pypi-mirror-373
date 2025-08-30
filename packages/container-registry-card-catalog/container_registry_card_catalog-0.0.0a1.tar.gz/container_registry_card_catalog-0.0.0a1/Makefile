# Container Registry Card Catalog - Build System
#
# AIA: EAI Hin R Claude Code v1.0
# Vibe-Coder: Andrew Potozniak <potozniak@redhat.com>
# Session Date: 2025-08-28

.PHONY: build clean install test test-install help

# Build the package
build:
	uv build

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/

# Install locally for development
install:
	pip install -e .

# Test the package build and installation
test-install: clean build
	python -m venv test-env
	test-env/bin/pip install dist/*.whl
	test-env/bin/container-registry-card-catalog --help
	test-env/bin/container-registry-card-catalog --mock &
	sleep 2
	pkill -f container-registry-card-catalog || true
	rm -rf test-env/
	@echo "✅ Package test successful!"

# Quick test - just build and check
test: clean build
	@echo "✅ Build successful!"

# Upload to PyPI (requires twine and PyPI credentials)
upload: clean build
	twine upload dist/*

# Help
help:
	@echo "Available targets:"
	@echo "  build        - Build the package"
	@echo "  clean        - Remove build artifacts"
	@echo "  install      - Install for development (editable)"
	@echo "  test         - Build and verify success"
	@echo "  test-install - Full test with temp venv"
	@echo "  upload       - Upload to PyPI"
	@echo "  help         - Show this help"
