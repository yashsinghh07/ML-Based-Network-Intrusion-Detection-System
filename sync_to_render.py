"""
Sync local NIDS data to Render via API
This allows Render dashboard to show real data from your local capture
"""
import requests
import time
import os
import re
from datetime import datetime

# Configuration
RENDER_API_URL = os.environ.get('RENDER_API_URL', 'https://your-app.onrender.com')
LOCAL_ALERTS_LOG = 'alerts.log'
LOCAL_STATS_FILE = 'nids_stats.txt'

def parse_local_stats():
    """Parse statistics from local nids_stats.txt"""
    stats = {
        'total_packets': 0,
        'normal_traffic': 0,
        'attacks_detected': 0,
        'normal_percentage': 0.0,
        'attack_percentage': 0.0,
        'last_updated': 'N/A'
    }
    
    if os.path.exists(LOCAL_STATS_FILE):
        try:
            with open(LOCAL_STATS_FILE, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'Total Packets Analyzed:' in line:
                        stats['total_packets'] = int(re.search(r'\d+', line).group())
                    elif 'Normal Traffic:' in line:
                        match = re.search(r'(\d+)\s+\(([\d.]+)%\)', line)
                        if match:
                            stats['normal_traffic'] = int(match.group(1))
                            stats['normal_percentage'] = float(match.group(2))
                    elif 'Attacks Detected:' in line:
                        match = re.search(r'(\d+)\s+\(([\d.]+)%\)', line)
                        if match:
                            stats['attacks_detected'] = int(match.group(1))
                            stats['attack_percentage'] = float(match.group(2))
                    elif 'Last Updated:' in line:
                        stats['last_updated'] = line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"Error reading stats: {e}")
    
    return stats

def sync_to_render():
    """Sync local data to Render"""
    try:
        # This would require an API endpoint on Render to receive data
        # For now, this is a placeholder
        stats = parse_local_stats()
        print(f"Syncing stats: {stats['total_packets']} packets, {stats['attacks_detected']} attacks")
        # API call would go here
    except Exception as e:
        print(f"Sync error: {e}")

if __name__ == "__main__":
    print("Data sync to Render (placeholder)")
    print("For real-time sync, you'd need to set up an API endpoint on Render")

