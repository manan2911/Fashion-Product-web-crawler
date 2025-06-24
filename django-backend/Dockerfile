# 1. Use the Bullseye-based slim image to avoid Bookworm GPG errors
FROM python:3.11-slim-bullseye

WORKDIR /code

# 2. Install system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 3. Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy project files

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy everything
COPY . .

# change into your Django project subfolder
WORKDIR /code/backend

EXPOSE 8000
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--log-level", "info"]