"""
Process PCAP files for NIDS
This allows processing captured network traffic files on Render
where live packet capture is not possible
"""
from scapy.all import rdpcap, IP, TCP, UDP
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import time

# Suppress sklearn warnings
warnings.filterwarnings('ignore')

# Load Model and Encoders
try:
    clf = joblib.load('nids_model.pkl')
    le_proto = joblib.load('le_proto.pkl')
except FileNotFoundError as e:
    print(f"Error loading model: {e}")
    print("Make sure nids_model.pkl and le_proto.pkl are in the repository")
    exit(1)

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
    
    print(f"\033[91m{log_entry.strip()}\033[0m")

def update_stats(total, normal, attacks):
    """Update statistics file"""
    with open(stats_file, 'w') as f:
        f.write(f"=== NIDS Statistics ===\n")
        f.write(f"Total Packets Analyzed: {total}\n")
        if total > 0:
            f.write(f"Normal Traffic: {normal} ({(normal/total*100):.2f}%)\n")
            f.write(f"Attacks Detected: {attacks} ({(attacks/total*100):.2f}%)\n")
        else:
            f.write(f"Normal Traffic: {normal} (0.00%)\n")
            f.write(f"Attacks Detected: {attacks} (0.00%)\n")
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

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
    dst_bytes = 0  # Cannot determine in single-packet analysis
    
    return [protocol_name, src_bytes, dst_bytes]

def process_packet(packet):
    """Process each captured packet"""
    features = extract_features(packet)
    if features is None:
        return None, None
    
    protocol_name, src_bytes, dst_bytes = features
    
    # Encode protocol
    try:
        proto_encoded = le_proto.transform([protocol_name])[0]
    except ValueError:
        return None, None
    
    # Create feature vector as DataFrame to match training format
    feature_df = pd.DataFrame([[proto_encoded, src_bytes, dst_bytes]], 
                              columns=['protocol_type', 'src_bytes', 'dst_bytes'])
    
    # Predict
    prediction = clf.predict(feature_df)
    
    return prediction[0], protocol_name

def process_pcap_file(pcap_file, delay=0.1):
    """Process a PCAP file packet by packet"""
    if not os.path.exists(pcap_file):
        print(f"PCAP file not found: {pcap_file}")
        return
    
    print("="*60)
    print("NETWORK INTRUSION DETECTION SYSTEM - PROCESSING PCAP")
    print("="*60)
    print(f"Model: Random Forest with {clf.n_estimators} estimators")
    print(f"Processing: {pcap_file}")
    print(f"Alert Log: {log_file}")
    print(f"Statistics: {stats_file}")
    print("="*60)
    print("\nProcessing packets...\n")
    
    # Initialize log file
    with open(log_file, 'w') as f:
        f.write(f"=== NIDS Alert Log - Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    packet_count = 0
    normal_count = 0
    attack_count = 0
    
    try:
        # Read and process packets
        packets = rdpcap(pcap_file)
        total_packets = len(packets)
        
        for i, packet in enumerate(packets):
            prediction, protocol_name = process_packet(packet)
            
            if prediction is None:
                continue
            
            packet_count += 1
            
            if prediction == 1:
                attack_count += 1
                log_alert(packet, protocol_name, len(packet))
            else:
                normal_count += 1
            
            # Update stats every 10 packets
            if packet_count % 10 == 0:
                update_stats(packet_count, normal_count, attack_count)
                progress = (i + 1) / total_packets * 100
                print(f"[INFO] Processed {packet_count}/{total_packets} packets ({progress:.1f}%) | "
                      f"Normal: {normal_count} | Attacks: {attack_count}")
            
            # Small delay to simulate real-time processing
            if delay > 0:
                time.sleep(delay)
        
        # Final stats update
        update_stats(packet_count, normal_count, attack_count)
        
        print("\n" + "="*60)
        print("Processing Complete")
        print("="*60)
        print(f"Total Packets: {packet_count}")
        if packet_count > 0:
            print(f"Normal: {normal_count} ({(normal_count/packet_count*100):.2f}%)")
            print(f"Attacks: {attack_count} ({(attack_count/packet_count*100):.2f}%)")
        print(f"\nLogs saved to: {log_file}")
        print(f"Statistics saved to: {stats_file}")
        
    except Exception as e:
        print(f"Error processing PCAP file: {e}")
        import traceback
        traceback.print_exc()

def continuous_processing(pcap_dir='pcap_files', delay=0.1):
    """Continuously process PCAP files from a directory"""
    print("="*60)
    print("NIDS - CONTINUOUS PCAP PROCESSING MODE")
    print("="*60)
    print(f"Watching directory: {pcap_dir}")
    print("Processing PCAP files as they appear...")
    print("="*60)
    
    processed_files = set()
    
    while True:
        try:
            if os.path.exists(pcap_dir):
                pcap_files = [f for f in os.listdir(pcap_dir) if f.endswith('.pcap') or f.endswith('.pcapng')]
                
                for pcap_file in pcap_files:
                    file_path = os.path.join(pcap_dir, pcap_file)
                    if file_path not in processed_files:
                        print(f"\nProcessing new file: {pcap_file}")
                        process_pcap_file(file_path, delay=delay)
                        processed_files.add(file_path)
            
            # Check for new files every 30 seconds
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\nStopping...")
            break
        except Exception as e:
            print(f"Error in continuous processing: {e}")
            time.sleep(30)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Process a specific PCAP file
        pcap_file = sys.argv[1]
        delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
        process_pcap_file(pcap_file, delay=delay)
    else:
        # Continuous mode - process files from pcap_files directory
        print("No PCAP file specified. Starting continuous mode...")
        print("Place .pcap or .pcapng files in 'pcap_files' directory")
        continuous_processing()

