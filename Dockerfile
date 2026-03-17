FROM python:3.12-slim

WORKDIR /app

# Install Redis server needed by current local Celery/cache configuration.
RUN apt-get update \
    && apt-get install -y --no-install-recommends redis-server \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Start local Redis and Flask app via Gunicorn on Render-provided port.
CMD ["sh", "-c", "redis-server --daemonize yes; gunicorn app:app --bind 0.0.0.0:${PORT:-10000}"]