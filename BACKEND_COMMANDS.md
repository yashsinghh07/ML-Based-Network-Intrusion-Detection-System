# 🔧 Backend Commands Guide

## 📍 Two Scenarios

### 1. Local Development (Your Computer)
### 2. Render Deployment (Cloud)

---

## 🖥️ LOCAL BACKEND (Your Computer)

### Command to Run:

```bash
cd /Users/yashsingh/NIDS_Projectt
sudo /opt/anaconda3/bin/python live_nids.py
```

**OR use the helper script:**
```bash
cd /Users/yashsingh/NIDS_Projectt
./start_backend.sh
```

### What This Does:
- ✅ Captures **real network packets** from your network interface
- ✅ Analyzes packets using your ML model
- ✅ Generates `alerts.log` and `nids_stats.txt`
- ✅ Frontend (dashboard) reads these files and displays data

### Requirements:
- ✅ **sudo/root access** (required for packet capture)
- ✅ Model files present: `nids_model.pkl`, `le_proto.pkl`
- ✅ Dependencies installed: `scapy`, `pandas`, `scikit-learn`, etc.

### Expected Output:
```
============================================================
NETWORK INTRUSION DETECTION SYSTEM - ACTIVE
============================================================
Model: Random Forest with X estimators
Monitoring: All IP traffic
Alert Log: alerts.log
Statistics: nids_stats.txt
============================================================

Listening for traffic... (Press Ctrl+C to stop)

[INFO] Processed 10 packets | Normal: 8 | Attacks: 2
[ALERT] Malicious Traffic Detected! ...
```

---

## ☁️ RENDER BACKEND (Cloud Deployment)

### Command (Already Configured):

**In Render Dashboard → Settings → Start Command:**
```
python start_with_data.py
```

### What This Does:
- ✅ Runs `generate_demo_data.py` in background (simulates network traffic)
- ✅ Generates `alerts.log` and `nids_stats.txt` with demo data
- ✅ Starts Streamlit dashboard
- ✅ Frontend reads these files and displays data

### You Don't Need to Run Anything:
- ✅ Render automatically runs this when service starts
- ✅ No manual command needed
- ✅ Works automatically after deployment

### What Happens:
1. Render builds your code
2. Runs `python start_with_data.py`
3. Data generator starts automatically
4. Dashboard starts automatically
5. Both run together

---

## 📋 Complete Local Setup Commands

### Terminal 1 - Backend:
```bash
cd /Users/yashsingh/NIDS_Projectt
sudo /opt/anaconda3/bin/python live_nids.py
```

### Terminal 2 - Frontend:
```bash
cd /Users/yashsingh/NIDS_Projectt
streamlit run dashboard.py
```

### Then Open Browser:
```
http://localhost:8501
```

---

## 🔍 Verify Backend is Running

### Check 1: Process Running
```bash
ps aux | grep live_nids
```
Should show the Python process.

### Check 2: Files Being Created
```bash
ls -lh alerts.log nids_stats.txt
```
Files should exist and be updating.

### Check 3: File Contents
```bash
tail -f alerts.log
```
Should show new alerts appearing.

### Check 4: Statistics
```bash
cat nids_stats.txt
```
Should show current statistics.

---

## ⚠️ Common Issues

### Issue: "Permission denied"
**Solution:**
```bash
# Use full Python path with sudo
sudo /opt/anaconda3/bin/python live_nids.py

# OR use the script
./start_backend.sh
```

### Issue: "ModuleNotFoundError: No module named 'scapy'"
**Solution:**
```bash
pip install scapy
# Then use full path with sudo
sudo /opt/anaconda3/bin/python live_nids.py
```

### Issue: "No packets captured"
**Solution:**
- Check network interface is active
- Verify you have network traffic
- Try: `sudo tcpdump -i any` to test capture

### Issue: "FileNotFoundError: nids_model.pkl"
**Solution:**
- Ensure model files are in the same directory
- Check: `ls nids_model.pkl le_proto.pkl`

---

## 📝 Quick Reference

### Local Backend Command:
```bash
sudo /opt/anaconda3/bin/python live_nids.py
```

### Render Backend Command (Auto):
```
python start_with_data.py
```
(Configured in Render Settings)

### Stop Backend:
```
Press Ctrl+C in the terminal
```

---

## 🎯 Summary

**For Local:**
- Run: `sudo /opt/anaconda3/bin/python live_nids.py`
- This captures real packets
- Frontend reads the generated files

**For Render:**
- Command: `python start_with_data.py` (already configured)
- Runs automatically
- No manual command needed

---

**Need to start backend?** Use the command above in a terminal!

