ARG IMAGE="python:3.7.6-alpine3.11"

FROM $IMAGE as build-stage

LABEL maintainer="Wrike DevOps team <devops+oss@team.wrike.com>"

ARG ENVIRONMENT=dev
ARG PYTHON_MODULE=callisto

ENV PYTHONUNBUFFERED 1
ENV PATH="/venv/bin:${PATH}"
ENV POETRY_VERSION=1.0.9

# install system build dependencies
RUN apk update && \
   apk add --no-cache libffi-dev build-base gcc make curl

WORKDIR /app

# copy package files needed for building
COPY poetry.lock pyproject.toml poetry-${POETRY_VERSION}.checksum /app/

# install app dependencies, without the app itself
RUN set -o pipefail \
   && python3 -m venv /venv \
   && . /venv/bin/activate \
   && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/${POETRY_VERSION}/get-poetry.py > get-poetry.py \
   && cat get-poetry.py | sha256sum -c /app/poetry-${POETRY_VERSION}.checksum \
   && python get-poetry.py --version ${POETRY_VERSION} \
   && . $HOME/.poetry/env \
   && (if [ "${ENVIRONMENT}" = "prod" ]; \
        then poetry install --no-root --no-dev; \
        else poetry install --no-root; \
       fi)

# copy package files needed for building
COPY ${PYTHON_MODULE} /app/${PYTHON_MODULE}
COPY tests /app/tests
COPY mypy.ini Makefile pytest.ini /app/

# Install the app in the editable mode
# (after we copied package sources, poetry will install them)
# App is installed in editable mode even in production - poetry cannot
# install it as a normal package.
# Alternative is building a wheel with poetry and install it with pip,
# but there is no real reason to.
RUN set -o pipefail \
    && . /venv/bin/activate \
    && . $HOME/.poetry/env \
    && (if [ "${ENVIRONMENT}" = "prod" ]; \
        then poetry install --no-dev; \
        else poetry install; \
        fi)


FROM $IMAGE

ARG PYTHON_MODULE=callisto

ENV PYTHONUNBUFFERED 1
ENV PATH="/venv/bin:${PATH}"

# since package is installed in editable mode, we need to
# copy its sources to the same location
COPY --from=build-stage /app/${PYTHON_MODULE} /app/${PYTHON_MODULE}
COPY --from=build-stage /app/${PYTHON_MODULE}.egg-info /app/${PYTHON_MODULE}.egg-info
COPY --from=build-stage /venv /venv

WORKDIR /app

CMD ["/venv/bin/python", "-m", "callisto"]
