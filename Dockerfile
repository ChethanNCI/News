# Using a slim image to keep it lightweight
FROM python:3.12-slim

# Set environment variables to ensure Python output is sent straight to terminal
# and to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies if needed (e.g., for database drivers)
# RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# FIX: Added the '-r' flag which was missing in your draft
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY manage.py .
COPY base/ ./base/
COPY news/ ./news/

RUN mkdir -p /app/staticfiles

# AUTOMATION STEP: Collect static files using dummy build-time vars
RUN DJANGO_SECRET_KEY=build-placeholder \
    VAULT_ADDR=http://127.0.0.1:8200 \
    DEBUG=True \
    python manage.py collectstatic --noinput

# Copy the Root CA that signed Vault's certificate
COPY root-ca.crt /usr/local/share/ca-certificates/root-ca.crt

# Update the OS trust store
RUN update-ca-certificates

# Expose the port Gunicorn will run on
EXPOSE 8000

# FIX: Use 'python -m gunicorn' to ensure it's found in the PATH 
# regardless of where pip installed it.
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "news.wsgi:application"]