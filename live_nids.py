from scapy.all import sniff, IP, TCP, UDP, ICMP
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

# Suppress sklearn warnings
warnings.filterwarnings('ignore')

# Load Model and Encoders
clf = joblib.load('nids_model.pkl')
le_proto = joblib.load('le_proto.pkl')

# Setup logging
log_file = 'alerts.log'
stats_file = 'nids_stats.txt'

def log_alert(packet, protocol_name, size):
    """Log alerts to file with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get ports if available
    sport = packet[TCP].sport if packet.haslayer(TCP) else (packet[UDP].sport if packet.haslayer(UDP) else 'N/A')
    dport = packet[TCP].dport if packet.haslayer(TCP) else (packet[UDP].dport if packet.haslayer(UDP) else 'N/A')
    
    log_entry = f"[{timestamp}] [ALERT] Malicious Traffic Detected! " \
                f"Src: {packet[IP].src}:{sport} -> " \
                f"Dst: {packet[IP].dst}:{dport} " \
                f"Protocol: {protocol_name.upper()} Size: {size} bytes\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)
    
    # Print to console with color (red)
    print(f"\033[91m{log_entry.strip()}\033[0m")

def update_stats(total, normal, attacks):
    """Update statistics file"""
    with open(stats_file, 'w') as f:
        f.write(f"=== NIDS Statistics ===\n")
        f.write(f"Total Packets Analyzed: {total}\n")
        f.write(f"Normal Traffic: {normal} ({(normal/total*100):.2f}%)\n")
        f.write(f"Attacks Detected: {attacks} ({(attacks/total*100):.2f}%)\n")
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Packet counters
packet_count = 0
normal_count = 0
attack_count = 0

print("="*60)
print("NETWORK INTRUSION DETECTION SYSTEM - ACTIVE")
print("="*60)
print(f"Model: Random Forest with {clf.n_estimators} estimators")
print(f"Monitoring: All IP traffic")
print(f"Alert Log: {log_file}")
print(f"Statistics: {stats_file}")
print("="*60)
print("\nListening for traffic... (Press Ctrl+C to stop)\n")

def extract_features(packet):
    """Extract features from packet"""
    if not packet.haslayer(IP):
        return None
    
    # Protocol mapping
    proto_map = {1: 'icmp', 6: 'tcp', 17: 'udp'}
    protocol_num = packet[IP].proto
    protocol_name = proto_map.get(protocol_num, 'other')
    
    # Skip if protocol not in training encoder
    if protocol_name not in le_proto.classes_:
        return None
    
    # Extract bytes
    src_bytes = len(packet)
    dst_bytes = 0  # Cannot determine in single-packet sniffing
    
    return [protocol_name, src_bytes, dst_bytes]

def process_packet(packet):
    """Process each captured packet"""
    global packet_count, normal_count, attack_count
    
    features = extract_features(packet)
    if features is None:
        return
    
    protocol_name, src_bytes, dst_bytes = features
    
    # Encode protocol
    try:
        proto_encoded = le_proto.transform([protocol_name])[0]
    except ValueError:
        return
    
    # Create feature vector as DataFrame to match training format
    # This eliminates the warning about feature names
    feature_df = pd.DataFrame([[proto_encoded, src_bytes, dst_bytes]], 
                              columns=['protocol_type', 'src_bytes', 'dst_bytes'])
    
    # Predict
    prediction = clf.predict(feature_df)
    
    # Update counters
    packet_count += 1
    
    if prediction[0] == 1:
        attack_count += 1
        log_alert(packet, protocol_name, src_bytes)
    else:
        normal_count += 1
    
    # Update stats every 10 packets
    if packet_count % 10 == 0:
        update_stats(packet_count, normal_count, attack_count)
        print(f"[INFO] Processed {packet_count} packets | Normal: {normal_count} | Attacks: {attack_count}")

# Initialize log file
with open(log_file, 'w') as f:
    f.write(f"=== NIDS Alert Log - Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")

try:
    # Start Sniffing
    sniff(filter="ip", prn=process_packet, store=0)
except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("NIDS Stopped by User")
    print("="*60)
    update_stats(packet_count, normal_count, attack_count)
    print(f"\nFinal Statistics:")
    print(f"  Total Packets: {packet_count}")
    print(f"  Normal: {normal_count} ({(normal_count/packet_count*100):.2f}%)")
    print(f"  Attacks: {attack_count} ({(attack_count/packet_count*100):.2f}%)")
    print(f"\nLogs saved to: {log_file}")
    print(f"Statistics saved to: {stats_file}")