ARG PY_IMAGE=python:3.12-slim
FROM ${PY_IMAGE}

ARG POETRY_VERSION=1.8.3
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=${POETRY_VERSION}


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    pip install "poetry==$POETRY_VERSION" && \
    apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry lock --no-update \
    && poetry install --no-interaction --no-ansi --no-root
COPY . .


RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles

EXPOSE 8000
