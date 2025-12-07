# 📦 NIDS Project - Deployment Documentation

This directory contains all deployment-related documentation and configuration files for deploying the NIDS (Network Intrusion Detection System) project.

## 📚 Documentation Files

1. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete step-by-step deployment guide
2. **[DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)** - Quick reference for fast deployment
3. **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Interactive checklist for deployment

## 🎯 Quick Overview

### Architecture
- **Backend:** Python/Streamlit application (`dashboard.py`)
- **Frontend:** Streamlit dashboard (combined with backend)
- **Optional API:** Flask API wrapper (`api.py`) for separate frontend

### Deployment Platforms
- **Render:** Backend/Full-stack deployment (Streamlit dashboard)
- **Vercel:** Frontend deployment (only if you create a separate React/Next.js frontend)

## 🚀 Fastest Deployment Path

### Option 1: Streamlit Only (Recommended)
Deploy the Streamlit dashboard on Render - it serves as both frontend and backend.

**Time:** ~10 minutes
**Steps:**
1. Push code to GitHub
2. Deploy on Render using `render.yaml` or manual setup
3. Done!

### Option 2: Separate Frontend + Backend
- Backend: Render (Streamlit or Flask API)
- Frontend: Vercel (React/Next.js)

**Time:** ~30 minutes
**Steps:**
1. Deploy backend on Render
2. Create frontend project
3. Deploy frontend on Vercel
4. Connect frontend to backend API

## 📁 Configuration Files

### For Render
- `render.yaml` - Render service configuration
- `.streamlit/config.toml` - Streamlit configuration
- `requirements.txt` - Python dependencies

### For Vercel (if using separate frontend)
- `vercel.json` - Vercel configuration
- Frontend project files (React/Next.js)

### General
- `.gitignore` - Git ignore rules
- `api.py` - Optional Flask API wrapper

## 🔧 Key Configuration

### Render Start Command
```bash
streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

### Environment Variables
- `PORT` - Automatically set by Render
- `PYTHON_VERSION` - Python version (optional)

### Model Files
Ensure `nids_model.pkl` and `le_proto.pkl` are:
- In your Git repository (for small files)
- Or in cloud storage (for large files)
- Or on Render Disk (for persistent storage)

## 📖 Getting Started

1. **Read the Quick Start:**
   ```bash
   cat DEPLOYMENT_QUICK_START.md
   ```

2. **Follow the Checklist:**
   ```bash
   cat DEPLOYMENT_CHECKLIST.md
   ```

3. **For Detailed Steps:**
   ```bash
   cat DEPLOYMENT_GUIDE.md
   ```

## 🆘 Need Help?

1. Check the [Troubleshooting](#troubleshooting) section in `DEPLOYMENT_GUIDE.md`
2. Review Render/Vercel documentation
3. Check application logs in respective dashboards

## 📝 Notes

- **Free Tier:** Render free tier services sleep after 15 minutes of inactivity
- **Model Files:** Large files should use cloud storage (S3, etc.)
- **Security:** Never commit secrets - use environment variables
- **HTTPS:** Automatically enabled on both platforms

## 🔗 Useful Links

- [Render Dashboard](https://dashboard.render.com)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Streamlit Docs](https://docs.streamlit.io)
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)

---

**Last Updated:** 2025-01-27


