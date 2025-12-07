# 🚀 Quick Steps: Deploy Frontend on Vercel

## ⚠️ Important Note

**Your Streamlit dashboard on Render IS your frontend!** It's already deployed and working.

You only need Vercel if you want a **custom React/Next.js frontend** instead of Streamlit.

---

## 📋 Option 1: Keep Using Streamlit (Easiest) ✅

**You're done!** Your frontend is already deployed on Render:
- URL: `https://your-app-name.onrender.com`
- No additional steps needed

---

## 📋 Option 2: Create Custom Frontend on Vercel

### Prerequisites
- ✅ Backend deployed on Render (already done)
- ✅ Flask API (`api.py`) - needs to be deployed separately OR use Streamlit

### Step 1: Deploy Flask API on Render (If Needed)

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure:**
   - **Name:** `nids-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python api.py`
   - **Port:** Leave default (Render sets `$PORT` automatically)
5. **Add Environment Variable:**
   - Key: `PORT`
   - Value: (Leave empty - Render auto-sets this)
6. **Click "Create Web Service"**
7. **Wait for deployment** (~5 minutes)
8. **Copy your API URL:** `https://nids-api.onrender.com`

### Step 2: Create Next.js Frontend

**Open terminal and run:**

```bash
# Create Next.js project
npx create-next-app@latest nids-frontend

# Navigate to project
cd nids-frontend

# Install dependencies
npm install axios recharts
```

### Step 3: Create Frontend Files

**Create `pages/index.js`:**
```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://nids-api.onrender.com';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, alertsRes] = await Promise.all([
        axios.get(`${API_URL}/api/stats`),
        axios.get(`${API_URL}/api/alerts`)
      ]);
      setStats(statsRes.data);
      setAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div style={{ padding: '20px', background: '#0e1117', color: '#fff', minHeight: '100vh' }}>
      <h1>🛡️ NIDS Dashboard</h1>
      
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', margin: '20px 0' }}>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
            <h3>Total Packets</h3>
            <p style={{ fontSize: '24px' }}>{stats.total_packets?.toLocaleString() || 0}</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
            <h3>Normal Traffic</h3>
            <p style={{ fontSize: '24px' }}>{stats.normal_traffic?.toLocaleString() || 0}</p>
            <p>{stats.normal_percentage?.toFixed(2)}%</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
            <h3>Attacks</h3>
            <p style={{ fontSize: '24px', color: '#ff4444' }}>{stats.attacks_detected?.toLocaleString() || 0}</p>
            <p>{stats.attack_percentage?.toFixed(2)}%</p>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
            <h3>Last Updated</h3>
            <p>{stats.last_updated || 'N/A'}</p>
          </div>
        </div>
      )}

      <div style={{ marginTop: '30px' }}>
        <h2>Recent Alerts</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1e1e1e', borderRadius: '8px' }}>
          <thead>
            <tr style={{ background: '#2a2a2a' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>Timestamp</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Source IP</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Destination IP</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Protocol</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Size</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length > 0 ? alerts.map((alert, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #333' }}>
                <td style={{ padding: '12px' }}>{alert.timestamp}</td>
                <td style={{ padding: '12px' }}>{alert.src_ip}:{alert.src_port}</td>
                <td style={{ padding: '12px' }}>{alert.dst_ip}:{alert.dst_port}</td>
                <td style={{ padding: '12px' }}>{alert.protocol}</td>
                <td style={{ padding: '12px' }}>{alert.size} bytes</td>
              </tr>
            )) : (
              <tr>
                <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
                  No alerts detected yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Update `package.json` to ensure it has:**
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "next": "latest",
    "react": "latest",
    "react-dom": "latest"
  }
}
```

### Step 4: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "NIDS Frontend"

# Add remote (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nids-frontend.git

# Push
git branch -M main
git push -u origin main
```

### Step 5: Deploy on Vercel

1. **Go to Vercel:** https://vercel.com
2. **Sign up/Login** (use GitHub for easy connection)
3. **Click "Add New Project"**
4. **Import your `nids-frontend` repository**
5. **Configure Project:**
   - **Framework Preset:** `Next.js` (auto-detected)
   - **Root Directory:** `./` (leave default)
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
6. **Environment Variables:**
   - Click "Add" → Add variable:
     - **Key:** `NEXT_PUBLIC_API_URL`
     - **Value:** `https://nids-api.onrender.com` (your Render API URL)
7. **Click "Deploy"**
8. **Wait 2-3 minutes** for deployment
9. **✅ Done!** Your frontend is live at: `https://nids-frontend.vercel.app`

---

## ✅ Verification

1. **Visit your Vercel URL:** `https://nids-frontend.vercel.app`
2. **Check if data loads** from your Render API
3. **Verify auto-refresh** (updates every 5 seconds)

---

## 🔧 Troubleshooting

**"Failed to fetch" or CORS errors:**
- Make sure `flask-cors` is in `requirements.txt`
- Verify `CORS(app)` is in your `api.py`
- Check API URL is correct in Vercel environment variables

**No data showing:**
- Check Render API is running: Visit `https://nids-api.onrender.com/api/stats`
- Check browser console for errors
- Verify environment variable `NEXT_PUBLIC_API_URL` is set in Vercel

**Build fails:**
- Check `package.json` has all dependencies
- Verify no syntax errors in `pages/index.js`
- Check Vercel build logs

---

## 📝 Summary

**Quick Checklist:**
- [ ] Deploy Flask API on Render (separate service)
- [ ] Create Next.js project
- [ ] Create `pages/index.js` with dashboard code
- [ ] Push to GitHub
- [ ] Deploy on Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` environment variable
- [ ] Test your frontend

**Or simply use your Streamlit dashboard on Render - it's already your frontend!** 🎉

---

**Need help?** See [FRONTEND_DEPLOYMENT.md](./FRONTEND_DEPLOYMENT.md) for detailed guide.

