import os
from pathlib import Path
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'replace-this')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "fashion-product-web-crawler.onrender.com",
]

# CSRF must trust your frontend origin
CSRF_TRUSTED_ORIGINS = [
    "https://fashion-product-web-crawler.onrender.com",
]
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'crawler',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,           # keep connections open
        ssl_require=not DEBUG       # enforce SSL in production
    )
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # or [BASE_DIR / 'templates'] if you want a project-level templates folder
        'APP_DIRS': True,  # tells Django to look for a "templates/" folder in each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static & Media
STATIC_URL = '/static/'

# Celery: Run tasks eagerly in development (when DEBUG is True)
CELERY_TASK_ALWAYS_EAGER = True

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL')
