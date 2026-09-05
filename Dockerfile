# Multistage Dockerfile for PayGuard AI
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code, models, and datasets
COPY backend /app/backend

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "backend/main.py"]
