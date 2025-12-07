#!/bin/bash
# Start script that runs both dashboard and demo data generator
# This allows the dashboard to display data on Render

# Start demo data generator in background
python generate_demo_data.py &

# Wait a moment for data to be generated
sleep 3

# Start Streamlit dashboard
streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0

