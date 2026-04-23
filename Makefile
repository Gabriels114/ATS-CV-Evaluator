.PHONY: install test lint fmt check

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

fmt:
	ruff format src tests

check: lint test
