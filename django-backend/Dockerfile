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
COPY start.sh /start.sh
ENTRYPOINT ["/start.sh"]

# 5. Expose port and default command
# EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# 5. Expose port and default CMD
EXPOSE 8000

# Replace the CMD with our launcher
COPY start.sh /start.sh
ENTRYPOINT ["/start.sh"]