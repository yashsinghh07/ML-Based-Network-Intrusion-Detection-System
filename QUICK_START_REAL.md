# ⚡ Quick Start - Real Working NIDS

## 🎯 For Local Development (Real Packet Capture)

### Option A: Two Terminal Windows (Recommended)

**Terminal 1 - Backend:**
```bash
cd /Users/yashsingh/NIDS_Projectt
sudo python live_nids.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/yashsingh/NIDS_Projectt
streamlit run dashboard.py
```

Then open: **http://localhost:8501**

---

### Option B: Single Script

```bash
cd /Users/yashsingh/NIDS_Projectt
sudo ./start_local.sh
```

---

## ☁️ For Render Deployment (Real Data)

### Step 1: Process PCAP Files

**On your local machine, capture traffic:**
```bash
# Capture network traffic
sudo tcpdump -i any -w capture.pcap

# Or use Wireshark and save as .pcap
```

### Step 2: Upload PCAP Files

```bash
cd /Users/yashsingh/NIDS_Projectt
mkdir -p pcap_files
# Copy your .pcap files to pcap_files/
git add pcap_files/*.pcap
git commit -m "Add PCAP files for real data processing"
git push
```

### Step 3: Update Render Start Command

**In Render Dashboard → Settings → Start Command:**
```bash
python -c "import threading, subprocess, os, time, sys; t=threading.Thread(target=lambda: subprocess.run([sys.executable, 'process_pcap.py', 'pcap_files/capture.pcap', '0.1']), daemon=True); t.start(); time.sleep(5); os.system(f'streamlit run dashboard.py --server.port={os.environ.get(\"PORT\", \"8501\")} --server.address=0.0.0.0')"
```

**Or create `start_real.py`:**
```python
import threading, subprocess, os, time, sys

def process_pcap():
    subprocess.run([sys.executable, 'process_pcap.py', 'pcap_files/capture.pcap', '0.1'])

t = threading.Thread(target=process_pcap, daemon=True)
t.start()
time.sleep(5)

port = os.environ.get('PORT', '8501')
os.system(f'streamlit run dashboard.py --server.port={port} --server.address=0.0.0.0')
```

**Then use:** `python start_real.py`

---

## ✅ Verification

**Local:**
- Backend terminal shows: "Listening for traffic..."
- Dashboard shows real-time packet counts and alerts
- Data updates automatically

**Render:**
- Check logs to see PCAP processing
- Dashboard displays analysis results from PCAP files
- Statistics and alerts are generated

---

## 📝 Important Notes

1. **Local setup requires sudo/root** for packet capture
2. **Render cannot do live capture** - use PCAP files instead
3. **Model files must be present** (`nids_model.pkl`, `le_proto.pkl`)
4. **Both processes need same directory** to share `alerts.log` and `nids_stats.txt`

---

**See [REAL_WORKING_SETUP.md](./REAL_WORKING_SETUP.md) for detailed instructions.**

