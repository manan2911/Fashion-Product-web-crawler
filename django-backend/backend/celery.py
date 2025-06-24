# backend/celery.py

import os
from celery import Celery

# 1) Point Django at your settings module before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 2) Now you can safely import Django settings
from django.conf import settings

# 3) Create the Celery app and load config
app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4) Optionally override broker/result-backend directly
app.conf.broker_url       = settings.CELERY_BROKER_URL
app.conf.result_backend   = settings.CELERY_RESULT_BACKEND

# 5) Auto-discover tasks in installed apps
app.autodiscover_tasks()
