ENVIRONMENT = dev

.PHONY: help prepare test test_smoke lint pyfmt
help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  prepare - install callisto to virtual environment"
	@echo "  test - run pytest"
	@echo "  test_smoke - run smoke tests in kind cluster"
	@echo "  lint - run available linters"
	@echo "  pyfmt - run available formatters"

prepare:
	@if [ "${ENVIRONMENT}" = "prod" ]; then \
		uv sync --locked --no-dev --no-editable; \
	else \
		uv sync; \
	fi

test:
	uv run pytest -v tests/integration --cov=callisto

test_smoke:
	uv run pytest -v --callisto-endpoint http://127.0.0.1:8080 tests/smoke

lint:
	uv run ruff check
	uv run ruff format --diff
	uv run mypy callisto

pyfmt:
	uv run ruff format
	uv run ruff check --fix
