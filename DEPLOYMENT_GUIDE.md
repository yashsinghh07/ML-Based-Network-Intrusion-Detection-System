# NIDS Project Deployment Guide
## Step-by-Step Deployment for Render (Backend) and Vercel (Frontend)

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment on Render](#backend-deployment-on-render)
3. [Frontend Deployment on Vercel](#frontend-deployment-on-vercel)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ GitHub account
- ✅ Render account (sign up at https://render.com)
- ✅ Vercel account (sign up at https://vercel.com)

### Required Files
- ✅ Your project pushed to a GitHub repository
- ✅ `requirements.txt` (already exists)
- ✅ Model files (`nids_model.pkl`, `le_proto.pkl`)

---

## Backend Deployment on Render

### Step 1: Prepare Your Repository

1. **Ensure your project is on GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Create a `render.yaml` file** (optional but recommended):
   ```yaml
   services:
     - type: web
       name: nids-dashboard
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
       envVars:
         - key: PYTHON_VERSION
           value: 3.10.0
   ```

3. **Create a `.streamlit/config.toml` file** (for Streamlit configuration):
   ```toml
   [server]
   port = 8501
   address = "0.0.0.0"
   enableCORS = false
   enableXsrfProtection = false
   
   [browser]
   gatherUsageStats = false
   ```

### Step 2: Deploy on Render

1. **Log in to Render:**
   - Go to https://dashboard.render.com
   - Sign up or log in with your GitHub account

2. **Create a New Web Service:**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub account if not already connected
   - Select your repository

3. **Configure the Service:**
   - **Name:** `nids-dashboard` (or your preferred name)
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** Leave empty (or specify if your app is in a subdirectory)
   - **Build Command:** 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
     ```
   - **Instance Type:** Free tier is fine for testing (upgrade for production)

4. **Environment Variables (if needed):**
   - Click "Advanced" → "Add Environment Variable"
   - Add any required variables:
     - `PYTHON_VERSION=3.10.0`
     - Any API keys or secrets

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for the build to complete (usually 5-10 minutes)

6. **Access Your Application:**
   - Once deployed, you'll get a URL like: `https://nids-dashboard.onrender.com`
   - Your Streamlit dashboard will be accessible at this URL

### Step 3: Handle Model Files

**Important:** Model files (`.pkl` files) need to be in your repository or uploaded separately.

**Option A: Include in Git (for small files < 100MB)**
```bash
git add *.pkl
git commit -m "Add model files"
git push
```

**Option B: Use Render Disk (for larger files)**
- In Render dashboard, go to your service
- Add a "Disk" resource
- Mount it and update your code to read from the disk path

**Option C: Use Cloud Storage (Recommended for production)**
- Upload models to AWS S3, Google Cloud Storage, or similar
- Update your code to download models on startup

---

## Frontend Deployment on Vercel

### Option 1: Deploy Streamlit Dashboard (Recommended)

Since your project uses Streamlit (which combines frontend and backend), the **Streamlit app on Render IS your frontend**. You don't need a separate Vercel deployment unless you want a custom frontend.

### Option 2: Create a Separate Frontend (If Needed)

If you want a custom React/Next.js frontend that calls your backend API:

#### Step 1: Create a Frontend Project

1. **Create a Next.js project:**
   ```bash
   npx create-next-app@latest nids-frontend
   cd nids-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install axios
   ```

3. **Create API integration:**
   - Create API routes to communicate with your Render backend
   - Build UI components for the dashboard

#### Step 2: Deploy on Vercel

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Frontend for NIDS"
   git remote add origin https://github.com/YOUR_USERNAME/nids-frontend.git
   git push -u origin main
   ```

2. **Deploy on Vercel:**
   - Go to https://vercel.com
   - Click "Add New Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset:** Next.js (auto-detected)
     - **Root Directory:** `./`
     - **Build Command:** `npm run build` (default)
     - **Output Directory:** `.next` (default)
   - Add Environment Variables:
     - `NEXT_PUBLIC_API_URL`: Your Render backend URL
   - Click "Deploy"

3. **Access Your Frontend:**
   - Vercel will provide a URL like: `https://nids-frontend.vercel.app`

---

## Post-Deployment Configuration

### 1. Update CORS Settings (if using separate frontend)

If you created a separate frontend, update your Render backend to allow CORS:

**Create `app.py` (Flask API wrapper):**
```python
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/stats')
def get_stats():
    # Read and return stats from nids_stats.txt
    pass

@app.route('/api/alerts')
def get_alerts():
    # Read and return alerts from alerts.log
    pass
```

### 2. Set Up Environment Variables

**On Render:**
- Go to your service → Environment
- Add any required variables:
  - `PYTHON_VERSION=3.10.0`
  - `STREAMLIT_SERVER_PORT=8501`

**On Vercel (if using separate frontend):**
- Go to your project → Settings → Environment Variables
- Add:
  - `NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com`

### 3. Configure Custom Domains (Optional)

**Render:**
- Go to your service → Settings → Custom Domains
- Add your domain and configure DNS

**Vercel:**
- Go to your project → Settings → Domains
- Add your domain

---

## Troubleshooting

### Common Issues

#### 1. Build Fails on Render
- **Issue:** Dependencies not installing
- **Solution:** 
  - Check `requirements.txt` syntax
  - Ensure Python version is compatible
  - Check build logs for specific errors

#### 2. Application Crashes on Startup
- **Issue:** Missing model files
- **Solution:**
  - Ensure `.pkl` files are in repository or accessible
  - Check file paths in code (use absolute paths or environment variables)

#### 3. Port Issues
- **Issue:** Application not accessible
- **Solution:**
  - Render uses `$PORT` environment variable
  - Update start command: `streamlit run dashboard.py --server.port=$PORT`

#### 4. Timeout Issues
- **Issue:** Free tier services sleep after inactivity
- **Solution:**
  - Upgrade to paid plan for always-on service
  - Or use a service like UptimeRobot to ping your app

#### 5. File System Issues
- **Issue:** Logs/stats files not persisting
- **Solution:**
  - Use Render Disk for persistent storage
  - Or use cloud storage (S3, etc.) for logs

### Useful Commands

**Check Render logs:**
- Go to your service → Logs tab

**Check Vercel logs:**
- Go to your project → Deployments → Click deployment → View Function Logs

**Local testing:**
```bash
# Test Streamlit locally
streamlit run dashboard.py

# Test with production port
PORT=8501 streamlit run dashboard.py --server.port=$PORT
```

---

## Quick Reference

### Render Deployment Checklist
- [ ] Repository pushed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] Model files included or accessible
- [ ] Start command configured correctly
- [ ] Environment variables set
- [ ] Service deployed and accessible

### Vercel Deployment Checklist (if using separate frontend)
- [ ] Frontend project created
- [ ] API integration configured
- [ ] Environment variables set
- [ ] Project deployed
- [ ] CORS configured on backend

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Streamlit Docs:** https://docs.streamlit.io
- **Render Status:** https://status.render.com
- **Vercel Status:** https://www.vercel-status.com

---

## Notes

1. **Free Tier Limitations:**
   - Render free tier services sleep after 15 minutes of inactivity
   - First request after sleep takes ~30 seconds
   - Consider upgrading for production use

2. **Model Files:**
   - Large model files (>100MB) should use cloud storage
   - Update code to download models on startup if using cloud storage

3. **Security:**
   - Never commit API keys or secrets to Git
   - Use environment variables for sensitive data
   - Enable HTTPS (automatic on both platforms)

4. **Monitoring:**
   - Set up health checks
   - Monitor logs regularly
   - Set up alerts for errors

---

**Last Updated:** 2025-01-27


