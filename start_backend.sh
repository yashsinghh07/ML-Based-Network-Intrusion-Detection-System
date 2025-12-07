#!/bin/bash
# Start backend with correct Python environment
# This ensures sudo uses the Python with all dependencies installed

cd /Users/yashsingh/NIDS_Projectt

# Get the Python executable from current environment
PYTHON_PATH=$(which python)

echo "Using Python: $PYTHON_PATH"
echo "Starting NIDS Backend..."
echo ""

# Use sudo with the full path to your Python
sudo $PYTHON_PATH live_nids.py

