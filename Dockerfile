FROM python:3.10-slim-buster AS base

ENV PYTHONUNBUFFERED=1 \

    PYTHONDONTWRITEBYTECODE=1 \

    PIP_NO_CACHE_DIR=off \

    VIRTUAL_ENV=/venv \

    PATH="/venv/bin:${PATH}"

FROM base AS build

WORKDIR /app

COPY ./pyproject.toml ./pyproject.toml


COPY ./src /src

RUN python -m build -w; \
    python -m pip install --no-deps --no-cache-dir dist/*.whl

FROM base

ENV BOT_CONFIG_PATH=/app/botconf.toml

COPY ./botconf.toml ./botconf.toml
COPY --from=build /venv /venv

CMD ["bots"]
