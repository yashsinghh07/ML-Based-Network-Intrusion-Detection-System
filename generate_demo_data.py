"""
Demo Data Generator for NIDS Dashboard
Generates sample data for testing the dashboard on Render
(since live packet capture is not possible in cloud environments)
"""
import random
import time
from datetime import datetime, timedelta
import os

# File paths
ALERTS_LOG = 'alerts.log'
STATS_FILE = 'nids_stats.txt'

# Sample data
PROTOCOLS = ['TCP', 'UDP', 'ICMP']
SAMPLE_IPS = ['192.168.1.10', '10.0.0.5', '172.16.0.20', '203.0.113.45', '198.51.100.12']
SAMPLE_PORTS = [80, 443, 22, 53, 3389, 8080, 3000, 5000]

def generate_alert():
    """Generate a random alert entry"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    src_ip = random.choice(SAMPLE_IPS)
    dst_ip = random.choice(SAMPLE_IPS)
    src_port = random.choice(SAMPLE_PORTS)
    dst_port = random.choice(SAMPLE_PORTS)
    protocol = random.choice(PROTOCOLS)
    size = random.randint(100, 5000)
    
    return f"[{timestamp}] [ALERT] Malicious Traffic Detected! " \
           f"Src: {src_ip}:{src_port} -> " \
           f"Dst: {dst_ip}:{dst_port} " \
           f"Protocol: {protocol} Size: {size} bytes\n"

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
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def initialize_files():
    """Initialize log and stats files"""
    if not os.path.exists(ALERTS_LOG):
        with open(ALERTS_LOG, 'w') as f:
            f.write(f"=== NIDS Alert Log - Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    if not os.path.exists(STATS_FILE):
        update_stats(0, 0, 0)

def run_demo_generator():
    """Run the demo data generator"""
    print("="*60)
    print("NIDS DEMO DATA GENERATOR - ACTIVE")
    print("="*60)
    print("Generating demo data for dashboard visualization...")
    print("This simulates network traffic analysis.")
    print("="*60)
    print("\nRunning in background... (Press Ctrl+C to stop)\n")
    
    initialize_files()
    
    packet_count = 0
    normal_count = 0
    attack_count = 0
    
    try:
        while True:
            # Simulate packet processing
            # 20% chance of attack, 80% normal traffic
            is_attack = random.random() < 0.2
            
            packet_count += 1
            
            if is_attack:
                attack_count += 1
                # Log the alert
                alert = generate_alert()
                with open(ALERTS_LOG, 'a') as f:
                    f.write(alert)
                print(f"[ALERT] Attack detected! ({attack_count} total)")
            else:
                normal_count += 1
            
            # Update stats every 5 seconds
            if packet_count % 10 == 0:
                update_stats(packet_count, normal_count, attack_count)
                print(f"[INFO] Processed {packet_count} packets | Normal: {normal_count} | Attacks: {attack_count}")
            
            # Wait before next packet (simulate real-time processing)
            time.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("Demo Generator Stopped")
        print("="*60)
        update_stats(packet_count, normal_count, attack_count)
        print(f"\nFinal Statistics:")
        print(f"  Total Packets: {packet_count}")
        if packet_count > 0:
            print(f"  Normal: {normal_count} ({(normal_count/packet_count*100):.2f}%)")
            print(f"  Attacks: {attack_count} ({(attack_count/packet_count*100):.2f}%)")
        print(f"\nLogs saved to: {ALERTS_LOG}")
        print(f"Statistics saved to: {STATS_FILE}")

if __name__ == "__main__":
    run_demo_generator()

