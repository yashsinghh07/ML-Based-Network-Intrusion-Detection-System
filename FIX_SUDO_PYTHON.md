# 🔧 Fix: Sudo Python Module Not Found

## Problem

When you run `sudo python live_nids.py`, it uses the **system Python** instead of your **conda/venv Python**, so it can't find installed packages like `scapy`.

## ✅ Solution

### Option 1: Use Full Python Path (Recommended)

Instead of:
```bash
sudo python live_nids.py
```

Use:
```bash
sudo /opt/anaconda3/bin/python live_nids.py
```

Or use the script:
```bash
./start_backend.sh
```

### Option 2: Find Your Python Path

```bash
# Find your Python path
which python

# Then use it with sudo
sudo $(which python) live_nids.py
```

### Option 3: Install in System Python (Not Recommended)

```bash
sudo pip install scapy
```

But this is not recommended as it mixes environments.

---

## 🚀 Quick Start (Fixed)

**Terminal 1 - Backend:**
```bash
cd /Users/yashsingh/NIDS_Projectt
sudo /opt/anaconda3/bin/python live_nids.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/yashsingh/NIDS_Projectt
streamlit run dashboard.py
```

---

## 📝 Why This Happens

- `python` → Uses your conda environment (has packages)
- `sudo python` → Uses system Python (no packages)
- `sudo /opt/anaconda3/bin/python` → Uses conda Python with sudo privileges

---

## ✅ Verification

Test if it works:
```bash
sudo /opt/anaconda3/bin/python -c "import scapy; print('OK')"
```

If it prints "OK", you're good to go!

