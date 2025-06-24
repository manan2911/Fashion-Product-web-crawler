# 1. Start from a small Python image
FROM python:3.11-slim-bullseye

# 2. Set our working directory for the install
WORKDIR /code

# 3. Install system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Copy & install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your repo into /code
COPY . .

# 6. Switch into the Django app directory
WORKDIR /code/backend

# 7. Expose port and default start command via gunicorn
EXPOSE 8000
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
