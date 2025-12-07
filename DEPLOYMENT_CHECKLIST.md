# ✅ Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## Pre-Deployment Checklist

### Repository Setup
- [ ] Project is pushed to GitHub
- [ ] All necessary files are committed
- [ ] `.gitignore` is configured (excludes venv, logs, etc.)
- [ ] Model files (`.pkl`) are included or accessible

### Files Verification
- [ ] `requirements.txt` exists and is up to date
- [ ] `dashboard.py` is the main application file
- [ ] `.streamlit/config.toml` exists (created automatically)
- [ ] `render.yaml` exists (optional, for Render)
- [ ] Model files (`nids_model.pkl`, `le_proto.pkl`) are in repo or cloud storage

### Code Verification
- [ ] Application runs locally: `streamlit run dashboard.py`
- [ ] No hardcoded paths (use relative paths or env vars)
- [ ] Port configuration uses `$PORT` environment variable
- [ ] All dependencies are in `requirements.txt`

---

## Render Deployment Checklist

### Step 1: Account Setup
- [ ] Render account created (https://render.com)
- [ ] GitHub account connected to Render
- [ ] Repository is accessible from Render

### Step 2: Service Configuration
- [ ] Service name: `nids-dashboard` (or your choice)
- [ ] Environment: `Python 3`
- [ ] Region selected
- [ ] Branch: `main` (or your default branch)

### Step 3: Build Settings
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
- [ ] Root Directory: (leave empty if root, or specify subdirectory)

### Step 4: Environment Variables
- [ ] `PYTHON_VERSION=3.10.0` (optional, Render auto-detects)
- [ ] Any API keys or secrets added (if needed)

### Step 5: Deploy
- [ ] Clicked "Create Web Service"
- [ ] Build completed successfully (check logs)
- [ ] Service is running (green status)
- [ ] URL is accessible: `https://your-app.onrender.com`

### Step 6: Post-Deployment
- [ ] Tested the dashboard URL
- [ ] Verified all features work
- [ ] Checked logs for errors
- [ ] Set up custom domain (optional)

---

## Vercel Deployment Checklist (Optional - Only if separate frontend needed)

### Step 1: Frontend Project
- [ ] Frontend project created (React/Next.js)
- [ ] API integration code written
- [ ] Environment variables configured
- [ ] Project pushed to GitHub

### Step 2: Vercel Setup
- [ ] Vercel account created (https://vercel.com)
- [ ] GitHub connected to Vercel
- [ ] Project imported from GitHub

### Step 3: Configuration
- [ ] Framework preset: Next.js (or your framework)
- [ ] Build command: `npm run build` (or appropriate)
- [ ] Output directory: `.next` (or appropriate)
- [ ] Environment variable: `NEXT_PUBLIC_API_URL` set to Render URL

### Step 4: Deploy
- [ ] Clicked "Deploy"
- [ ] Build completed successfully
- [ ] Frontend URL is accessible
- [ ] API calls to Render backend work

---

## Testing Checklist

### Local Testing
- [ ] `streamlit run dashboard.py` works locally
- [ ] Dashboard displays correctly
- [ ] All features functional
- [ ] No console errors

### Render Testing
- [ ] Dashboard loads on Render URL
- [ ] Statistics display correctly
- [ ] Alerts table shows data
- [ ] Charts render properly
- [ ] Auto-refresh works (if enabled)

### Integration Testing (if using separate frontend)
- [ ] Frontend loads on Vercel URL
- [ ] API calls to Render backend succeed
- [ ] Data displays correctly in frontend
- [ ] CORS is configured properly

---

## Production Readiness

### Security
- [ ] No secrets in code (use environment variables)
- [ ] HTTPS enabled (automatic on Render/Vercel)
- [ ] CORS configured (if using separate frontend)
- [ ] Input validation in place

### Performance
- [ ] Large files (>100MB) use cloud storage
- [ ] Images optimized
- [ ] Caching configured (if applicable)

### Monitoring
- [ ] Logs accessible
- [ ] Error tracking set up (optional)
- [ ] Health checks configured
- [ ] Alerts configured (optional)

### Documentation
- [ ] README updated with deployment info
- [ ] Environment variables documented
- [ ] API endpoints documented (if applicable)

---

## Troubleshooting Checklist

If deployment fails:

- [ ] Check build logs in Render/Vercel dashboard
- [ ] Verify all dependencies in `requirements.txt`
- [ ] Ensure Python version compatibility
- [ ] Check file paths (use relative paths)
- [ ] Verify model files are accessible
- [ ] Check environment variables are set
- [ ] Review error messages in logs
- [ ] Test locally first

---

## Quick Reference

### Render Service URL Format
```
https://[service-name].onrender.com
```

### Vercel Project URL Format
```
https://[project-name].vercel.app
```

### Important Commands
```bash
# Local testing
streamlit run dashboard.py

# Check dependencies
pip list

# Test API (if using Flask)
python api.py
```

---

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete

**Last Updated:** 2025-01-27


