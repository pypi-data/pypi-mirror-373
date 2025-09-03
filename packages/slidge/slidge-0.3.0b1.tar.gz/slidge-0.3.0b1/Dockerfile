ARG PYTHONVER=3.13
ARG DISTRO=bookworm-slim

## Install dependencies in a virtual env
FROM ghcr.io/astral-sh/uv:python$PYTHONVER-$DISTRO AS builder
ENV UV_PROJECT_ENVIRONMENT=/venv
RUN uv venv $UV_PROJECT_ENVIRONMENT
COPY uv.lock pyproject.toml .
RUN uv sync --all-groups --all-extras --no-install-project

## CI environment for slidge, where we move /venv to .venv
FROM ghcr.io/astral-sh/uv:python$PYTHONVER-$DISTRO AS ci
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/woodpecker/src/codeberg.org/slidge/slidge/.venv
ENV PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        git \
        make \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.cache /root/.cache

## Dev container
FROM builder AS dev
ENV PATH="/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
# libmagic1: to guess mime type from files
# media-types: to determine file name suffix based on file type
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libmagic1 \
        media-types \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
# prosody certificate for localhost
COPY --from=codeberg.org/slidge/prosody-slidge-dev:latest \
  /etc/prosody/certs/localhost.crt \
  /usr/local/share/ca-certificates/
RUN update-ca-certificates
RUN pip install watchdog[watchmedo]
WORKDIR /io
COPY ./dev/hot-reload.sh .
ENTRYPOINT ["./hot-reload.sh"]
