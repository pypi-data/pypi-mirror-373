.PHONY: help install dev-install clean test lint format build upload upload-test release release-test

# Default target
help:
	@echo "📦 Mentorstec - Comandos disponíveis:"
	@echo ""
	@echo "🔧 Desenvolvimento:"
	@echo "  install      - Instala o pacote"
	@echo "  dev-install  - Instala dependências de desenvolvimento"
	@echo "  clean        - Remove arquivos de build"
	@echo ""
	@echo "🧪 Qualidade:"
	@echo "  test         - Executa testes"
	@echo "  lint         - Executa linting"
	@echo "  format       - Formata código"
	@echo ""
	@echo "📦 Build e Deploy:"
	@echo "  build        - Constrói o pacote"
	@echo "  upload       - Upload para PyPI"
	@echo "  upload-test  - Upload para TestPyPI"
	@echo "  release      - Release completo (PyPI)"
	@echo "  release-test - Release completo (TestPyPI)"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

# Cleaning
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete

# Quality checks
test:
	python -m pytest tests/ -v --cov=mentorstec

lint:
	ruff check mentorstec/
	mypy mentorstec/

format:
	black mentorstec/
	ruff check --fix mentorstec/

# Building
build: clean
	python -m build

# PyPI upload (requires PYPI_TOKEN environment variable)
upload: build
	@echo "🚀 Fazendo upload para PyPI..."
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "❌ Configure PYPI_TOKEN: export PYPI_TOKEN=pypi-..."; \
		exit 1; \
	fi
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TOKEN twine upload dist/*

# TestPyPI upload (requires PYPI_TEST_TOKEN environment variable)
upload-test: build
	@echo "🚀 Fazendo upload para TestPyPI..."
	@if [ -z "$$PYPI_TEST_TOKEN" ]; then \
		echo "❌ Configure PYPI_TEST_TOKEN: export PYPI_TEST_TOKEN=pypi-..."; \
		exit 1; \
	fi
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TEST_TOKEN TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/ twine upload dist/*

# Complete release process
release:
	python scripts/release.py

release-test:
	python scripts/release.py --test