# 📍 Where to Set Render Start Command

## 🎯 Location in Render Dashboard

### Step-by-Step Instructions:

1. **Go to Render Dashboard**
   - URL: https://dashboard.render.com
   - Login if needed

2. **Find Your Service**
   - Look for: **"ML-Based-Network-Intrusion-Detection-System"** (or your service name)
   - Click on it

3. **Go to Settings Tab**
   - In the left sidebar, click **"Settings"**
   - (It's usually the 3rd or 4th option in the sidebar)

4. **Find "Start Command" Section**
   - Scroll down in the Settings page
   - Look for a section labeled **"Start Command"** or **"Command"**
   - It's usually under "Build & Deploy" section

5. **Edit the Start Command**
   - You'll see a text input field
   - Current value might be: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
   - **Change it to:**
     ```
     python start_with_data.py
     ```

6. **Save Changes**
   - Click **"Save Changes"** button (usually at the bottom of the page)
   - Render will automatically redeploy with the new command

---

## 📸 Visual Guide

**Navigation Path:**
```
Render Dashboard
  └── Your Service (ML-Based-Network-Intrusion-Detection-System)
      └── Settings (Left Sidebar)
          └── Scroll Down
              └── Start Command (Text Input Field)
                  └── Enter: python start_with_data.py
                      └── Save Changes
```

---

## 🔍 Alternative: Using render.yaml

You can also set it in `render.yaml` file (which you already have):

**File: `render.yaml`**
```yaml
services:
  - type: web
    name: nids-dashboard
    env: python
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python start_with_data.py  # ← This line
    ...
```

**If using render.yaml:**
- Make sure it's committed and pushed
- Render will use the command from `render.yaml` automatically
- You don't need to set it in the dashboard (but you can verify it)

---

## ✅ Verification

### Check 1: In Render Dashboard
1. Go to Settings
2. Look at "Start Command" field
3. Should show: `python start_with_data.py`

### Check 2: In render.yaml
1. Open `render.yaml` file
2. Look for `startCommand:` line
3. Should show: `python start_with_data.py`

### Check 3: After Deployment
1. Go to "Logs" tab
2. Look for: `Starting NIDS Dashboard with Demo Data Generator`
3. This confirms the correct command is running

---

## 🆘 If You Can't Find It

### Option 1: Check Service Type
- Make sure it's a **"Web Service"** (not Static Site or Background Worker)
- Start Command is only available for Web Services

### Option 2: Check Permissions
- Make sure you're the owner/admin of the service
- You need edit permissions

### Option 3: Use render.yaml Instead
- If you can't find it in dashboard, use `render.yaml`
- Commit and push the file
- Render will use it automatically

---

## 📝 Quick Reference

**Location:**
```
Render Dashboard → Your Service → Settings → Start Command
```

**Command to Enter:**
```
python start_with_data.py
```

**File Alternative:**
```
render.yaml → startCommand: python start_with_data.py
```

---

## 🎯 Summary

**Two Ways to Set It:**

1. **Render Dashboard (Manual):**
   - Dashboard → Service → Settings → Start Command
   - Enter: `python start_with_data.py`
   - Save Changes

2. **render.yaml (Automatic):**
   - File already has: `startCommand: python start_with_data.py`
   - Commit and push
   - Render uses it automatically

**Both methods work!** Use whichever is easier for you.

