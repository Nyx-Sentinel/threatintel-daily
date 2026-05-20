FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY threatintel_daily/ ./threatintel_daily/
COPY config.yml ./config.yml

# Create data directory
RUN mkdir -p /app/data /app/logs

# Set environment
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "-m", "threatintel_daily.main"]
