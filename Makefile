PYTHON_MODULE := callisto
TESTS_PATH := tests
PYTHON_BIN := python3
MAX_LINE_LENGTH := 120
VENV_NAME := .venv
ENVIRONMENT = dev
POETRY_VERSION := 2.0.1

.PHONY: help prepare test test_smoke lint pyfmt
help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  prepare - install poetry and callisto to virtual environment"
	@echo "  test - run pytest"
	@echo "  test_smoke - run smoke tests in kind cluster"
	@echo "  lint - run available linters"
	@echo "  pyfmt - run available formatters"

prepare:
	${PYTHON_BIN} -m venv ${VENV_NAME} \
	&& . ${VENV_NAME}/bin/activate \
	&& python -m pip install poetry==${POETRY_VERSION} \
	&& (if [ "${ENVIRONMENT}" = "prod" ]; \
		then python -m poetry install --only main --no-root -v \
		    && python3 -m poetry build --format=wheel \
			&& python3 -m pip install --no-deps dist/*.whl; \
		else python -m poetry install; \
	fi)

test:
	python -m pytest -v ${TESTS_PATH}/integration --cov=callisto

test_smoke:
	python -m pytest -v --callisto-endpoint http://127.0.0.1:8080 ${TESTS_PATH}/smoke

lint:
	python -m flake8 --max-line-length=${MAX_LINE_LENGTH} --ignore E203,E501,W503,A003,E701 ${PYTHON_MODULE} ${TESTS_PATH}
	python -m black -l ${MAX_LINE_LENGTH} --check ${PYTHON_MODULE} ${TESTS_PATH}
	python -m isort --diff --check-only ${PYTHON_MODULE} ${TESTS_PATH}
	python -m mypy ${PYTHON_MODULE}


pyfmt:
	python -m black -l ${MAX_LINE_LENGTH} ${PYTHON_MODULE} ${TESTS_PATH}
	python -m isort ${PYTHON_MODULE} tests
	python -m flake8 --max-line-length=${MAX_LINE_LENGTH} --ignore E203,E501,W503,A003,E701 ${PYTHON_MODULE} tests
	python -m mypy ${PYTHON_MODULE}
