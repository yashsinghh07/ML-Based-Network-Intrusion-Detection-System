# 🚀 Quick Start Deployment Guide

## TL;DR - Fastest Way to Deploy

### Backend on Render (5 minutes)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect GitHub → Select your repo
   - **Settings:**
     - Name: `nids-dashboard`
     - Build: `pip install -r requirements.txt`
     - Start: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
   - Click "Create Web Service"
   - Wait 5-10 minutes
   - ✅ Done! Your app is live at `https://nids-dashboard.onrender.com`

### Frontend on Vercel (Only if you need a separate frontend)

**Note:** Your Streamlit dashboard IS your frontend. You only need Vercel if you want a custom React/Next.js frontend.

If you need a separate frontend:
1. Create a Next.js project
2. Connect to Vercel
3. Set `NEXT_PUBLIC_API_URL` to your Render URL
4. Deploy

---

## Detailed Steps

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete instructions.

---

## Common Commands

```bash
# Test locally
streamlit run dashboard.py

# Test API locally (if using Flask API)
python api.py

# Check if everything is ready
python -c "import streamlit, pandas, numpy, sklearn; print('✅ All dependencies OK')"
```

---

## Troubleshooting

**Build fails?**
- Check `requirements.txt` is correct
- Ensure Python 3.10+ is used

**App crashes?**
- Check model files (`.pkl`) are in repo
- Check logs in Render dashboard

**Can't access?**
- Free tier sleeps after 15 min inactivity
- First request takes ~30 seconds

---

**Need help?** See full guide: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)


