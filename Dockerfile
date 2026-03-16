FROM python:3.11-slim AS base

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY voip_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY voip_backend/ ./voip_backend/
COPY sql/ ./sql/

# Create dirs
RUN mkdir -p logs uploads

# Env defaults
ENV FLASK_APP=voip_backend/run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "voip_backend.run:app"]
