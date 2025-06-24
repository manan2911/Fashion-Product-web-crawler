buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
web: gunicorn backend.wsgi --log-file -
worker: celery -A backend worker --loglevel=info
