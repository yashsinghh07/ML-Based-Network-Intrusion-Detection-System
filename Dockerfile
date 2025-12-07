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

# Copy model files - ensure these files exist in your repository
# If model files don't exist, comment out the next 2 lines
# Note: COPY with wildcards will fail if no files match
# Make sure nids_model.pkl and le_proto.pkl are in your repo
COPY nids_model.pkl .
COPY le_proto.pkl .

# Copy dataset (optional - comment out if not needed)
# COPY KDDTrain+.txt .

# Create directories for logs
RUN mkdir -p /app/logs

# Expose ports
# 8501 for Streamlit dashboard
EXPOSE 8501

# Default command (can be overridden in docker-compose)
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
