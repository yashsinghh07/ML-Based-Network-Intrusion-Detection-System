"""
NIDS Backend - Network Intrusion Detection System Backend
Runs in terminal, processes network traffic, and generates logs for the dashboard.
Supports both live packet capture and simulated traffic modes.
"""

import os
import sys
import time
import random
import warnings
from datetime import datetime, timezone
from collections import defaultdict
import re

# Suppress warnings
warnings.filterwarnings('ignore')

# Try to import required libraries
try:
    import joblib
    import pandas as pd
    import numpy as np
    HAS_ML_LIBS = True
except ImportError as e:
    print(f"[WARNING] ML libraries not available: {e}")
    print("[INFO] Running in simulation mode only")
    HAS_ML_LIBS = False

# Try to fix Scapy cache directory permission issue
# Set cache to a writable location in the current directory
try:
    # Create a local cache directory for Scapy
    local_cache = os.path.join(os.getcwd(), '.scapy_cache')
    if not os.path.exists(local_cache):
        os.makedirs(local_cache, mode=0o755, exist_ok=True)
    # Set environment variable before importing Scapy
    os.environ['SCAPY_CACHE'] = local_cache
    
    # Also try to fix the default cache directory
    cache_dir = os.path.expanduser('~/.cache/scapy')
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir, mode=0o755, exist_ok=True)
        except (PermissionError, OSError):
            pass  # Can't create default cache, will use local one
    else:
        # Try to fix permissions on existing cache
        try:
            services_file = os.path.join(cache_dir, 'services')
            if os.path.exists(services_file):
                os.chmod(services_file, 0o644)
        except (PermissionError, OSError):
            pass  # Can't fix permissions, will use local cache
except Exception:
    pass  # Ignore cache setup errors, will try to import anyway

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    HAS_SCAPY = True
except (ImportError, PermissionError, OSError, Exception) as e:
    print(f"[WARNING] Scapy not available: {e}")
    print("[INFO] Live packet capture disabled. Running in simulation mode.")
    HAS_SCAPY = False

# File paths
ALERTS_LOG = 'alerts.log'
STATS_FILE = 'nids_stats.txt'

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    DIM = '\033[2m'

# Global variables
model = None
le_proto = None
packet_count = 0
normal_count = 0
attack_count = 0
protocol_stats = defaultdict(int)
ip_stats = defaultdict(int)

def load_model():
    """Load NIDS model and encoder if available"""
    global model, le_proto
    
    if not HAS_ML_LIBS:
        return False
    
    try:
        if os.path.exists('nids_model.pkl') and os.path.exists('le_proto.pkl'):
            print(f"{Colors.CYAN}[INFO]{Colors.RESET} Loading NIDS model...")
            model = joblib.load('nids_model.pkl')
            le_proto = joblib.load('le_proto.pkl')
            print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} Model loaded successfully!")
            print(f"{Colors.DIM}  - Model type: {type(model).__name__}{Colors.RESET}")
            if hasattr(model, 'n_estimators'):
                print(f"{Colors.DIM}  - Estimators: {model.n_estimators}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Model files not found. Running in simulation mode.")
            return False
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to load model: {e}")
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Running in simulation mode.")
        return False

def initialize_files():
    """Initialize log and stats files"""
    if not os.path.exists(ALERTS_LOG):
        with open(ALERTS_LOG, 'w') as f:
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            f.write(f"=== NIDS Alert Log - Started {timestamp} ===\n\n")
        print(f"{Colors.GREEN}[INFO]{Colors.RESET} Created alerts log: {ALERTS_LOG}")
    
    if not os.path.exists(STATS_FILE):
        update_stats(0, 0, 0)
        print(f"{Colors.GREEN}[INFO]{Colors.RESET} Created stats file: {STATS_FILE}")

def log_alert(packet_info, protocol_name, size, is_real_detection=False):
    """Log alerts to file with timestamp and print to terminal"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    src_ip = packet_info.get('src_ip', 'N/A')
    src_port = packet_info.get('src_port', 'N/A')
    dst_ip = packet_info.get('dst_ip', 'N/A')
    dst_port = packet_info.get('dst_port', 'N/A')
    
    # Format log entry
    log_entry = f"[{timestamp}] [ALERT] Malicious Traffic Detected! " \
                f"Src: {src_ip}:{src_port} -> " \
                f"Dst: {dst_ip}:{dst_port} " \
                f"Protocol: {protocol_name.upper()} Size: {size} bytes\n"
    
    # Write to file
    with open(ALERTS_LOG, 'a') as f:
        f.write(log_entry)
    
    # Print to terminal with colors
    detection_type = "MODEL" if is_real_detection else "SIM"
    print(f"\n{Colors.RED}{Colors.BOLD}[ALERT - {detection_type}]{Colors.RESET}")
    print(f"  {Colors.RED}⚠️  Attack Detected!{Colors.RESET}")
    print(f"  {Colors.DIM}Time: {timestamp}{Colors.RESET}")
    print(f"  {Colors.WHITE}Source: {src_ip}:{src_port}{Colors.RESET}")
    print(f"  {Colors.WHITE}Destination: {dst_ip}:{dst_port}{Colors.RESET}")
    print(f"  {Colors.WHITE}Protocol: {protocol_name.upper()}{Colors.RESET}")
    print(f"  {Colors.WHITE}Size: {size} bytes{Colors.RESET}")
    print(f"  {Colors.DIM}Total Attacks: {attack_count}{Colors.RESET}\n")

def update_stats(total, normal, attacks):
    """Update statistics file"""
    with open(STATS_FILE, 'w') as f:
        f.write(f"=== NIDS Statistics ===\n")
        f.write(f"Total Packets Analyzed: {total}\n")
        if total > 0:
            f.write(f"Normal Traffic: {normal} ({(normal/total*100):.2f}%)\n")
            f.write(f"Attacks Detected: {attacks} ({(attacks/total*100):.2f}%)\n")
        else:
            f.write(f"Normal Traffic: {normal} (0.00%)\n")
            f.write(f"Attacks Detected: {attacks} (0.00%)\n")
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        f.write(f"Last Updated: {timestamp}\n")

def extract_features_from_packet(packet):
    """Extract features from a Scapy packet"""
    if not packet.haslayer(IP):
        return None
    
    # Protocol mapping
    proto_map = {1: 'icmp', 6: 'tcp', 17: 'udp'}
    protocol_num = packet[IP].proto
    protocol_name = proto_map.get(protocol_num, 'other')
    
    # Get ports
    sport = 'N/A'
    dport = 'N/A'
    if packet.haslayer(TCP):
        sport = packet[TCP].sport
        dport = packet[TCP].dport
    elif packet.haslayer(UDP):
        sport = packet[UDP].sport
        dport = packet[UDP].dport
    
    # Extract bytes
    src_bytes = len(packet)
    dst_bytes = 0  # Cannot determine in single-packet analysis
    
    return {
        'protocol_name': protocol_name,
        'src_ip': packet[IP].src,
        'dst_ip': packet[IP].dst,
        'src_port': sport,
        'dst_port': dport,
        'src_bytes': src_bytes,
        'dst_bytes': dst_bytes
    }

def predict_with_model(features):
    """Use the loaded model to predict if packet is an attack"""
    if model is None or le_proto is None:
        return None, None
    
    protocol_name = features['protocol_name']
    
    # Check if protocol is in encoder
    if protocol_name not in le_proto.classes_:
        return None, None
    
    try:
        # Encode protocol
        proto_encoded = le_proto.transform([protocol_name])[0]
        
        # Create feature vector
        feature_df = pd.DataFrame([[proto_encoded, features['src_bytes'], features['dst_bytes']]], 
                                  columns=['protocol_type', 'src_bytes', 'dst_bytes'])
        
        # Predict
        prediction = model.predict(feature_df)
        
        return prediction[0], protocol_name
    except Exception as e:
        print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Prediction error: {e}")
        return None, None

def process_packet(packet=None, packet_info=None):
    """Process a single packet"""
    global packet_count, normal_count, attack_count
    
    is_real_detection = False
    
    # If we have a real packet, extract features
    if packet is not None and HAS_SCAPY:
        features = extract_features_from_packet(packet)
        if features is None:
            return
        
        packet_info = {
            'src_ip': features['src_ip'],
            'src_port': features['src_port'],
            'dst_ip': features['dst_ip'],
            'dst_port': features['dst_port']
        }
        
        # Try to predict with model
        if model is not None:
            prediction, protocol_name = predict_with_model(features)
            if prediction is not None:
                is_real_detection = True
                packet_count += 1
                
                if prediction == 1:
                    attack_count += 1
                    protocol_stats[protocol_name.upper()] += 1
                    ip_stats[packet_info['src_ip']] += 1
                    log_alert(packet_info, protocol_name, features['src_bytes'], is_real_detection=True)
                else:
                    normal_count += 1
                
                # Update stats periodically
                if packet_count % 10 == 0:
                    update_stats(packet_count, normal_count, attack_count)
                    print_stats_summary()
                
                return
    
    # Fallback to simulation if no model or packet
    if packet_info is None:
        # Generate simulated packet info
        sample_ips = ['192.168.1.10', '10.0.0.5', '172.16.0.20', '203.0.113.45', '198.51.100.12']
        sample_ports = [80, 443, 22, 53, 3389, 8080, 3000, 5000]
        protocols = ['TCP', 'UDP', 'ICMP']
        
        packet_info = {
            'src_ip': random.choice(sample_ips),
            'src_port': random.choice(sample_ports),
            'dst_ip': random.choice(sample_ips),
            'dst_port': random.choice(sample_ports)
        }
        protocol_name = random.choice(protocols).lower()
        size = random.randint(100, 5000)
    else:
        protocol_name = packet_info.get('protocol', 'tcp').lower()
        size = packet_info.get('size', random.randint(100, 5000))
    
    # Simulate detection (20% chance of attack)
    is_attack = random.random() < 0.2
    
    packet_count += 1
    
    if is_attack:
        attack_count += 1
        protocol_stats[protocol_name.upper()] += 1
        ip_stats[packet_info['src_ip']] += 1
        log_alert(packet_info, protocol_name, size, is_real_detection=False)
    else:
        normal_count += 1
    
    # Update stats periodically
    if packet_count % 10 == 0:
        update_stats(packet_count, normal_count, attack_count)
        print_stats_summary()

def print_stats_summary():
    """Print statistics summary to terminal"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}📊 NIDS Statistics Summary{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"  {Colors.WHITE}Total Packets: {Colors.GREEN}{packet_count:,}{Colors.RESET}")
    print(f"  {Colors.WHITE}Normal Traffic: {Colors.GREEN}{normal_count:,}{Colors.RESET} "
          f"({Colors.GREEN}{(normal_count/packet_count*100):.2f}%{Colors.RESET})" if packet_count > 0 else "")
    print(f"  {Colors.WHITE}Attacks Detected: {Colors.RED}{attack_count:,}{Colors.RESET} "
          f"({Colors.RED}{(attack_count/packet_count*100):.2f}%{Colors.RESET})" if packet_count > 0 else "")
    
    if protocol_stats:
        print(f"\n  {Colors.BOLD}Top Protocols:{Colors.RESET}")
        for proto, count in sorted(protocol_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {Colors.DIM}{proto}: {count}{Colors.RESET}")
    
    if ip_stats:
        print(f"\n  {Colors.BOLD}Top Source IPs:{Colors.RESET}")
        for ip, count in sorted(ip_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {Colors.DIM}{ip}: {count}{Colors.RESET}")
    
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def packet_handler(packet):
    """Handler for live packet capture"""
    try:
        process_packet(packet=packet)
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Error processing packet: {e}")

def run_live_capture(interface=None, count=0):
    """Run live packet capture"""
    if not HAS_SCAPY:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Scapy not available. Cannot capture live packets.")
        return False
    
    print(f"{Colors.CYAN}[INFO]{Colors.RESET} Starting live packet capture...")
    if interface:
        print(f"{Colors.CYAN}[INFO]{Colors.RESET} Interface: {interface}")
    else:
        print(f"{Colors.CYAN}[INFO]{Colors.RESET} Using default interface")
    
    try:
        if count > 0:
            sniff(iface=interface, prn=packet_handler, count=count, store=False)
        else:
            sniff(iface=interface, prn=packet_handler, store=False)
    except PermissionError:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Permission denied. Try running with sudo.")
        return False
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Capture error: {e}")
        return False
    
    return True

def run_simulation_mode(interval=1.0):
    """Run in simulation mode (generate fake traffic)"""
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Running in simulation mode...")
    print(f"{Colors.DIM}Generating simulated network traffic...{Colors.RESET}\n")
    
    try:
        while True:
            process_packet()
            time.sleep(random.uniform(interval * 0.5, interval * 1.5))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[INFO]{Colors.RESET} Simulation stopped by user")

def print_banner():
    """Print startup banner"""
    banner = f"""
{Colors.CYAN}{'='*70}{Colors.RESET}
{Colors.BOLD}{Colors.CYAN}🛡️  NETWORK INTRUSION DETECTION SYSTEM (NIDS) - BACKEND{Colors.RESET}
{Colors.CYAN}{'='*70}{Colors.RESET}
{Colors.DIM}Real-time network traffic monitoring and threat detection{Colors.RESET}
{Colors.CYAN}{'='*70}{Colors.RESET}
"""
    print(banner)

def main():
    """Main function"""
    print_banner()
    
    # Initialize files
    initialize_files()
    
    # Try to load model
    model_loaded = load_model()
    
    # Parse command line arguments
    mode = 'simulation'  # default mode
    interface = None
    count = 0
    interval = 1.0
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'live':
            mode = 'live'
            if len(sys.argv) > 2:
                interface = sys.argv[2]
            if len(sys.argv) > 3:
                count = int(sys.argv[3])
        elif sys.argv[1] == 'simulation' or sys.argv[1] == 'sim':
            mode = 'simulation'
            if len(sys.argv) > 2:
                interval = float(sys.argv[2])
    
    print(f"\n{Colors.BOLD}Configuration:{Colors.RESET}")
    print(f"  {Colors.WHITE}Mode: {Colors.CYAN}{mode.upper()}{Colors.RESET}")
    print(f"  {Colors.WHITE}Model: {Colors.GREEN if model_loaded else Colors.YELLOW}{'Loaded' if model_loaded else 'Simulation Only'}{Colors.RESET}")
    print(f"  {Colors.WHITE}Alerts Log: {Colors.DIM}{ALERTS_LOG}{Colors.RESET}")
    print(f"  {Colors.WHITE}Stats File: {Colors.DIM}{STATS_FILE}{Colors.RESET}")
    print(f"\n{Colors.DIM}Press Ctrl+C to stop{Colors.RESET}\n")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    try:
        if mode == 'live' and HAS_SCAPY:
            if not run_live_capture(interface, count):
                print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Falling back to simulation mode...")
                run_simulation_mode(interval)
        else:
            if mode == 'live':
                print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Live capture requested but Scapy not available.")
                print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Switching to simulation mode...")
            run_simulation_mode(interval)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[INFO]{Colors.RESET} Shutting down...")
        update_stats(packet_count, normal_count, attack_count)
        print_stats_summary()
        print(f"\n{Colors.GREEN}[SUCCESS]{Colors.RESET} Backend stopped gracefully.")
        print(f"{Colors.DIM}Logs saved to: {ALERTS_LOG}{Colors.RESET}")
        print(f"{Colors.DIM}Statistics saved to: {STATS_FILE}{Colors.RESET}\n")

if __name__ == "__main__":
    main()

