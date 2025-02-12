ARG IMAGE="python:3.13.2-alpine3.21"

FROM $IMAGE as build-stage

LABEL maintainer="Wrike DevOps team <devops+oss@team.wrike.com>"

ARG ENVIRONMENT=dev
ARG PYTHON_MODULE=callisto

ENV PYTHONUNBUFFERED 1
ENV PATH="/venv/bin:${PATH}"
ENV POETRY_VERSION=2.0.1
ENV POETRY_VENV="/poetry_venv"
ENV POETRY_BIN="${POETRY_VENV}/bin/poetry"

# install system build dependencies
RUN apk update && \
   apk add --no-cache libffi-dev build-base gcc make curl

RUN python3 -m venv ${POETRY_VENV} \
    && . ${POETRY_VENV}/bin/activate \
    && pip install poetry==${POETRY_VERSION}

WORKDIR /app

# copy package files needed for building
COPY poetry.lock pyproject.toml /app/

# install app dependencies, without the app itself
RUN set -o pipefail \
    && python3 -m venv /venv \
    && . /venv/bin/activate \
    && (if [ "${ENVIRONMENT}" = "prod" ]; \
        then ${POETRY_BIN} install --only main --no-root; \
        else ${POETRY_BIN} install --no-root; \
        fi)

# copy package files needed for building
COPY ${PYTHON_MODULE} /app/${PYTHON_MODULE}
COPY tests /app/tests
COPY pyproject.toml /app/

# Install the app in the editable mode
# (after we copied package sources, poetry will install them)
# App is installed in editable mode even in production - poetry cannot
# install it as a normal package.
# Alternative is building a wheel with poetry and install it with pip,
# but there is no real reason to.
RUN set -o pipefail \
    && . /venv/bin/activate \
    && (if [ "${ENVIRONMENT}" = "prod" ]; \
        then ${POETRY_BIN} install --only main; \
        else ${POETRY_BIN} install; \
        fi)


FROM $IMAGE

ARG PYTHON_MODULE=callisto

ENV PYTHONUNBUFFERED 1
ENV PATH="/venv/bin:${PATH}"

# since package is installed in editable mode, we need to
# copy its sources to the same location
COPY --from=build-stage /app/${PYTHON_MODULE} /app/${PYTHON_MODULE}
COPY --from=build-stage /venv /venv

WORKDIR /app

CMD ["/venv/bin/python", "-m", "callisto"]
