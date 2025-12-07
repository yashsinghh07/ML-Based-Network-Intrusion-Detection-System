"""
Flask API wrapper for NIDS Dashboard
Use this if you want to create a separate frontend that calls this API
"""
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File paths
ALERTS_LOG = 'alerts.log'
STATS_FILE = 'nids_stats.txt'

def parse_stats():
    """Parse statistics from nids_stats.txt"""
    stats = {
        'total_packets': 0,
        'normal_traffic': 0,
        'attacks_detected': 0,
        'normal_percentage': 0.0,
        'attack_percentage': 0.0,
        'last_updated': 'N/A'
    }
    
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
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
            return {'error': str(e)}
    
    return stats

def parse_alerts(limit=100):
    """Parse alerts from alerts.log"""
    alerts = []
    
    if os.path.exists(ALERTS_LOG):
        try:
            with open(ALERTS_LOG, 'r') as f:
                lines = f.readlines()
                start_idx = 0
                if lines and '=== NIDS Alert Log' in lines[0]:
                    start_idx = 2
                
                for line in lines[start_idx:]:
                    line = line.strip()
                    if line and '[ALERT]' in line:
                        try:
                            timestamp_match = re.search(r'\[([^\]]+)\]', line)
                            timestamp = timestamp_match.group(1) if timestamp_match else 'N/A'
                            
                            src_match = re.search(r'Src:\s+([^\s:]+):(\d+)', line)
                            src_ip = src_match.group(1) if src_match else 'N/A'
                            src_port = src_match.group(2) if src_match else 'N/A'
                            
                            dst_match = re.search(r'Dst:\s+([^\s:]+):(\d+)', line)
                            dst_ip = dst_match.group(1) if dst_match else 'N/A'
                            dst_port = dst_match.group(2) if dst_match else 'N/A'
                            
                            proto_match = re.search(r'Protocol:\s+(\w+)', line)
                            protocol = proto_match.group(1) if proto_match else 'N/A'
                            
                            size_match = re.search(r'Size:\s+(\d+)', line)
                            size = size_match.group(1) if size_match else 'N/A'
                            
                            alerts.append({
                                'timestamp': timestamp,
                                'src_ip': src_ip,
                                'src_port': src_port,
                                'dst_ip': dst_ip,
                                'dst_port': dst_port,
                                'protocol': protocol,
                                'size': int(size) if size != 'N/A' else 0
                            })
                        except Exception:
                            continue
            
            alerts.reverse()
            return alerts[:limit]
        except Exception as e:
            return {'error': str(e)}
    
    return alerts

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NIDS API',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get NIDS statistics"""
    stats = parse_stats()
    return jsonify(stats)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts with optional limit"""
    limit = int(os.environ.get('ALERTS_LIMIT', 100))
    alerts = parse_alerts(limit=limit)
    return jsonify({
        'alerts': alerts,
        'count': len(alerts)
    })

@app.route('/api/alerts/<int:limit>', methods=['GET'])
def get_alerts_with_limit(limit):
    """Get alerts with specified limit"""
    alerts = parse_alerts(limit=limit)
    return jsonify({
        'alerts': alerts,
        'count': len(alerts)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


