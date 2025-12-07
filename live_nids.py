import time
import random

print("Simulated NIDS backend started...")

while True:
    # Simulated metrics
    total = random.randint(25000, 40000)
    normal = int(total * random.uniform(0.93, 0.98))
    attacks = total - normal

    # Write stats file (for dashboard)
    with open("nids_stats.txt", "w") as f:
        f.write("=== NIDS Statistics ===\n")
        f.write(f"Total Packets Analyzed: {total}\n")
        f.write(f"Normal Traffic: {normal} ({(normal/total)*100:.2f}%)\n")
        f.write(f"Attacks Detected: {attacks} ({(attacks/total)*100:.2f}%)\n")
        f.write(f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Append simulated alert
    with open("alerts.log", "a") as log:
        log.write(f"[{time.strftime('%H:%M:%S')}] ALERT: {attacks} suspicious packets detected\n")

    print(f"Updated stats: {attacks} attacks detected ({time.strftime('%H:%M:%S')})")

    # Update every 5 seconds
    time.sleep(5)
