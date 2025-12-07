#!/bin/bash
# Start script for local real-time NIDS
# This starts both the backend (live_nids.py) and frontend (dashboard.py)

echo "============================================================"
echo "Starting NIDS - Real-Time Network Intrusion Detection"
echo "============================================================"
echo ""
echo "This will start:"
echo "  1. Backend: Live packet capture (requires sudo)"
echo "  2. Frontend: Streamlit dashboard"
echo ""
echo "Press Ctrl+C to stop both services"
echo "============================================================"
echo ""

# Check if running as root (for packet capture)
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  WARNING: Not running as root"
    echo "   Packet capture requires sudo privileges"
    echo "   Run with: sudo ./start_local.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start backend in background
echo "🚀 Starting backend (live packet capture)..."
python live_nids.py &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start frontend
echo "🚀 Starting frontend (dashboard)..."
echo ""
echo "✅ Dashboard will open at: http://localhost:8501"
echo ""

streamlit run dashboard.py

# Cleanup: kill backend when frontend stops
kill $BACKEND_PID 2>/dev/null
echo ""
echo "✅ Stopped all services"

