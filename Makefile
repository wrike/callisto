PYTHON_MODULE := callisto
TESTS_PATH := tests
PYTHON_BIN := python3
VENV_NAME := .venv
ENVIRONMENT = dev
POETRY_VERSION := 1.0.9

.PHONY: help prepare tests tests_smoke lint pyfmt
help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  tests - run pytest"
	@echo "  lint - run available linters"
	@echo "  pyfmt - run available formatters (now only isort)"

prepare:
	${PYTHON_BIN} -m venv ${VENV_NAME} \
	&& . ${VENV_NAME}/bin/activate \
	&& curl -sSL https://raw.githubusercontent.com/sdispater/poetry/${POETRY_VERSION}/get-poetry.py > get-poetry.py \
	&& cat get-poetry.py | sha256sum -c poetry-${POETRY_VERSION}.checksum \
	&& python get-poetry.py -y --version ${POETRY_VERSION} \
	&& . ${HOME}/.poetry/env \
	\
	&& (if [ "${ENVIRONMENT}" = "prod" ]; \
		then poetry install --no-dev; \
		else poetry install; \
	fi)

tests:
	${PYTHON_BIN} -m pytest ${TESTS_PATH}/integration

tests_smoke:
	${PYTHON_BIN} -m pytest --callisto-endpoint http://127.0.0.1:8080 ${TESTS_PATH}/smoke

lint:
	${PYTHON_BIN} -m mypy ${PYTHON_MODULE}
	${PYTHON_BIN} -m flake8 --max-line-length=120 ${PYTHON_MODULE} ${TESTS_PATH}
	${PYTHON_BIN} -m isort --diff --check-only ${PYTHON_MODULE} ${TESTS_PATH}

pyfmt:
	${PYTHON_BIN} -m isort ${PYTHON_MODULE} ${TESTS_PATH}
