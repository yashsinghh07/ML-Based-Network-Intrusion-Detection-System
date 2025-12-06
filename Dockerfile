# Dockerfile for NIDS Project
# Multi-stage build for optimized image size

FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY train_model.py .
COPY live_nids.py .
COPY dashboard.py .
COPY train_deep_nids.py .

# Copy model files (if they exist)
COPY *.pkl . 2>/dev/null || true
COPY *.h5 . 2>/dev/null || true

# Copy dataset (optional, for training)
COPY KDDTrain+.txt . 2>/dev/null || true

# Create directories for logs
RUN mkdir -p /app/logs

# Expose ports
# 8501 for Streamlit dashboard
EXPOSE 8501

# Default command (can be overridden in docker-compose)
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

