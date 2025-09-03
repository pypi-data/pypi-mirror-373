# ./Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1) Install deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# 2) Copy code so the image can run even without a bind mount
#    (Bind mount in compose will override these files during dev)
#    NOTE: speculate is now a PACKAGE (directory), not a single file.
COPY . /app

# Optional: ensure package is importable without relying on cwd
ENV PYTHONPATH=/app

# Default command; docker-compose can override with entrypoint if desired
CMD ["python", "-m", "speculate.cli", "./scenarios"]
