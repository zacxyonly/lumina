FROM python:3.11-slim

LABEL maintainer="Mundai"
LABEL description="Lumina - Lightweight AI Agent Framework"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY lumina/ ./lumina/
COPY setup.py .
COPY README.md .
COPY LICENSE .

# Install Lumina
RUN pip install -e .

# Create directories
RUN mkdir -p /app/logs /app/memory /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LUMINA_LOG_DIR=/app/logs
ENV LUMINA_MEMORY_DIR=/app/memory

# Default command (interactive mode)
CMD ["python", "-m", "lumina.cli"]
