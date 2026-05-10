# Repo-root Dockerfile — produces a single self-contained image that serves
# the API AND the static frontend on port 5000 (same-origin, no CORS).
# Build from the repo root:
#     docker build -t manasi2210/the-jewel-nest-studio:latest .

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production \
    PORT=5000

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

# Install Python deps first (better layer caching when only code changes)
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Backend goes to /app, frontend goes to /frontend (matches app.py FRONTEND_DIR)
COPY --chown=app:app backend/ /app/
COPY --chown=app:app frontend/ /frontend/

RUN mkdir -p /app/uploads /app/logs /app/flask_session \
    && chown -R app:app /app/uploads /app/logs /app/flask_session

USER app

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=5 \
    CMD curl -fsS http://127.0.0.1:5000/api/health || exit 1

CMD ["sh", "-c", "exec gunicorn -w ${WEB_CONCURRENCY:-4} -b 0.0.0.0:${PORT:-5000} --access-logfile - --error-logfile - 'app:create_app()'"]
