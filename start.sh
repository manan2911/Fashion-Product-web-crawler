#!/usr/bin/env sh
# start both celery worker (in background) and gunicorn (in foreground)

# Start Celery worker
celery -A backend worker --loglevel=info --concurrency=2 &

# Now exec Gunicorn as the “main” process so container logs and shutdowns
exec gunicorn backend.wsgi \
     --bind 0.0.0.0:${PORT:-8000} \
     --workers 3 \
     --log-level info
