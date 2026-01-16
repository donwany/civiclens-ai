# ---- Base ----
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (curl for healthchecks/logs; build deps minimal since we use psycopg binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y libpq-dev build-essential

WORKDIR /app

# Copy only requirements first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install psycopg2-binary

# Reinstall to ensure binary version is used

# Copy project files
COPY app/ /app/app/
COPY data/ /app/data/
# COPY .chainlit/ /app/.chainlit/
COPY public/ /app/public/

# Expose Chainlit port
EXPOSE 1776

# Set Python path to include /app
ENV PYTHONPATH=/app

# Default command: run Chainlit app
CMD ["chainlit", "run", "app/chainlit_app.py", "--host", "0.0.0.0", "--port", "1776", "--headless"]