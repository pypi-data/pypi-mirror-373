FROM ghcr.io/astral-sh/uv:0.8.14-python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=0 UV_NO_CACHE=1
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=marge,target=marge \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --frozen --no-default-groups --no-editable

FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y \
    git-core \
    && \
    rm -rf /var/lib/apt/lists/* && \
    adduser --home /var/lib/marge-bot --system --group marge-bot

COPY --from=builder --chown=marge-bot:marge-bot /app/.venv /app/.venv

USER marge-bot

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["marge"]
