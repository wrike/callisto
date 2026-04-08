ARG PYTHON_IMAGE
ARG UV_VERSION

FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv

FROM $PYTHON_IMAGE AS build-stage

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/venv

# install system build dependencies
RUN apk update && \
   apk add --no-cache libffi-dev build-base gcc

# install uv
COPY --from=uv /uv /bin/

# copy package files needed for building
COPY uv.lock pyproject.toml /app/

WORKDIR /app

# install app dependencies, without the app itself
RUN uv sync --locked --no-dev --no-install-project

# copy package files needed for building
COPY callisto /app/callisto

# Install the app itself
# https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs
RUN uv sync --locked --no-dev --no-editable


FROM $PYTHON_IMAGE

LABEL maintainer="Wrike DevOps team <devops+oss@team.wrike.com>"

ENV PYTHONUNBUFFERED=1

COPY --from=build-stage /venv /venv

CMD ["/venv/bin/python", "-m", "callisto"]
