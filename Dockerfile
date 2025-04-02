FROM python:3.10-slim-buster AS base

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=off VIRTUAL_ENV=/venv PATH="/venv/bin:${PATH}"

FROM base AS build

WORKDIR /app

COPY ./pyproject.toml ./pyproject.toml


COPY ./src ./src

RUN set -eux; \
    python -m venv /venv; \
    /venv/bin/pip install build; \
    /venv/bin/python -m build -w; \
    /venv/bin/pip install --no-cache-dir dist/*.whl

FROM base

COPY --from=build /venv /venv

CMD ["bots"]
