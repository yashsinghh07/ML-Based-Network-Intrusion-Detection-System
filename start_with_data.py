"""
Combined startup script that runs data generator and dashboard
This is the main entry point for Render deployment
"""
import subprocess
import sys
import os
import time
import threading

def run_data_generator():
    """Run demo data generator in background thread"""
    try:
        from generate_demo_data import run_demo_generator
        run_demo_generator()
    except Exception as e:
        print(f"Data generator error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("Starting NIDS Dashboard with Demo Data Generator")
    print("="*60)
    
    # Start data generator in background thread
    data_thread = threading.Thread(target=run_data_generator, daemon=True)
    data_thread.start()
    print("✓ Demo data generator started in background")
    
    # Wait a moment for initial data
    print("Waiting for initial data generation...")
    time.sleep(3)
    print("✓ Initial data generated")
    
    # Get port from environment (Render sets this)
    port = os.environ.get('PORT', '8501')
    print(f"✓ Starting Streamlit dashboard on port {port}")
    print("="*60)
    
    # Run Streamlit dashboard using subprocess
    # This will block until Streamlit stops
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\nShutting down...")
