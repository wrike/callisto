MAX_LINE_LENGTH := 120
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
	uv run flake8 --max-line-length=${MAX_LINE_LENGTH} --ignore E203,E501,W503,A003,E701 callisto tests
	uv run black -l ${MAX_LINE_LENGTH} --check callisto tests
	uv run isort --diff --check-only callisto tests
	uv run mypy callisto

pyfmt:
	uv run black -l ${MAX_LINE_LENGTH} callisto tests
	uv run isort callisto tests
	uv run flake8 --max-line-length=${MAX_LINE_LENGTH} --ignore E203,E501,W503,A003,E701 callisto tests
	uv run mypy callisto
