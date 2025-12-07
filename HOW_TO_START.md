# 🚀 How to Start the NIDS Dashboard on Render

## ⚠️ Important Note

**Live packet capture (`live_nids.py`) cannot run on Render** because:
- Render doesn't allow root/privileged access
- Network interfaces aren't accessible in containerized environments
- Packet capture requires system-level permissions

## ✅ Solution: Demo Data Generator

I've created a **demo data generator** that simulates network traffic analysis. This allows your dashboard to display data and function properly on Render.

---

## 📋 Quick Start Steps

### Option 1: Automatic (Recommended)

The dashboard is already configured to start with demo data. Just **redeploy on Render**:

1. **Commit and push the new files:**
   ```bash
   git add generate_demo_data.py start_with_data.py render.yaml
   git commit -m "Add demo data generator for Render deployment"
   git push
   ```

2. **Render will automatically redeploy** (if auto-deploy is enabled)

3. **Or manually trigger redeploy:**
   - Go to Render Dashboard
   - Click "Manual Deploy" → "Deploy latest commit"

4. **Wait 5-10 minutes** for deployment

5. **Visit your dashboard** - it should now show data!

---

### Option 2: Update Render Settings Manually

If you prefer to update manually:

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Select your service:** "ML-Based-Network-Intrusion-Detection-System"
3. **Go to Settings**
4. **Update Start Command:**
   ```
   python start_with_data.py
   ```
5. **Click "Save Changes"**
6. **Redeploy** the service

---

## 🔧 How It Works

The new setup includes:

1. **`generate_demo_data.py`** - Generates simulated network traffic data
   - Creates alerts in `alerts.log`
   - Updates statistics in `nids_stats.txt`
   - Runs continuously in the background

2. **`start_with_data.py`** - Main startup script
   - Starts the data generator in a background thread
   - Starts the Streamlit dashboard
   - Both run simultaneously

3. **Updated `render.yaml`** - Configured to use the new startup script

---

## 📊 What You'll See

After deployment, your dashboard will show:
- ✅ **Total Packets** - Increasing count
- ✅ **Normal Traffic** - Percentage of normal packets
- ✅ **Attacks Detected** - Simulated attack alerts
- ✅ **Recent Alerts Table** - List of detected attacks
- ✅ **Charts** - Protocol distribution and time series

---

## 🎯 For Local Development

If you want to test locally with **real packet capture**:

```bash
# Terminal 1: Start live packet capture (requires sudo)
sudo python live_nids.py

# Terminal 2: Start dashboard
streamlit run dashboard.py
```

**Note:** On your local machine, you can use `live_nids.py` for real packet capture (requires admin/root privileges).

---

## 🔄 Switching Between Demo and Live Data

**On Render (Cloud):**
- Uses `generate_demo_data.py` (demo/simulated data)
- Automatically started via `start_with_data.py`

**On Local Machine:**
- Can use `live_nids.py` for real packet capture
- Or use `generate_demo_data.py` for testing without root access

---

## 🆘 Troubleshooting

**Dashboard shows no data:**
- Wait a few seconds after deployment (data generator needs time to start)
- Check Render logs to ensure both processes are running
- Verify `generate_demo_data.py` is in your repository

**Data not updating:**
- Check if data generator thread is running (check Render logs)
- Verify files `alerts.log` and `nids_stats.txt` are being created

**Build fails:**
- Ensure all files are committed to Git
- Check `requirements.txt` has all dependencies
- Verify Python version is 3.10+

---

## 📝 Files Created

- ✅ `generate_demo_data.py` - Demo data generator
- ✅ `start_with_data.py` - Combined startup script
- ✅ `start_dashboard.sh` - Alternative shell script (optional)
- ✅ Updated `render.yaml` - New start command

---

## ✅ Next Steps

1. **Commit and push** the new files
2. **Redeploy on Render**
3. **Visit your dashboard** - it should now be working with data!

---

**Questions?** Check the Render logs if you encounter any issues.

