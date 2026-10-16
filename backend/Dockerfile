FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /usr/local/bin/uv
WORKDIR /srv

# Install dependencies from the lockfile
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev
ENV PATH="/srv/.venv/bin:$PATH"

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Run as a non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000
# Migrate, load demo data (skipped if the DB already has data), then start the API
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
