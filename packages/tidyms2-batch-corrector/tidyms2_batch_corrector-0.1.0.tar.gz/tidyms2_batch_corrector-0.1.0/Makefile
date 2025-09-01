PYTHON_VERSION = 3.12
.venv:
	type uv && uv venv --python $(PYTHON_VERSION) || >&2 echo "Error: uv not found in user PATH."

.PHONY: dev-install
dev-install: .venv
	uv sync --all-extras && uv run pre-commit install

.PHONY: clean
clean:
	rm -rf .venv .pytest_cache .ruff_cache htmlcov docs/_build
	find -iname "*.pyc" -delete

.PHONY: check-format
check-format:
	uv run ruff check

.PHONY: check-spell
check-spell:
	cspell tidyms2_batch_corrector README.md

.PHONY: format
format:
	uv run ruff check --fix
	uv run ruff format

.PHONY: check-types
check-types:
	uv run pyright tidyms2_batch_corrector

.PHONY: unit-tests
unit-tests:
	uv run pytest

.PHONY: coverage
coverage:
	uv run pytest --cov=tidyms2_batch_corrector && uv run coverage html
