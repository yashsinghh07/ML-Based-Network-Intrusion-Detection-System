# 🎨 Frontend Deployment Guide for Vercel

## 📋 Understanding Your Setup

**Current Status:**
- ✅ **Backend:** Deployed on Render (Streamlit dashboard)
- ✅ **Frontend:** Your Streamlit dashboard IS your frontend (already deployed on Render)

**Two Options:**

### Option 1: Use Streamlit Dashboard (Already Deployed) ✅
Your Streamlit dashboard on Render is both frontend and backend. You're done! Just access it at:
```
https://your-app-name.onrender.com
```

### Option 2: Create Separate Frontend on Vercel (Optional)
If you want a custom React/Next.js frontend that calls your backend API, follow the steps below.

---

## 🚀 Option 2: Deploy Custom Frontend on Vercel

### Step 1: Set Up Flask API Backend (If Not Already Done)

Your `api.py` file provides a REST API. You need to deploy it separately or modify your Render service.

**Option A: Deploy API as Separate Service on Render**

1. **Create a new Web Service on Render:**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - **Settings:**
     - Name: `nids-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python api.py`
     - Add Environment Variable: `PORT` (auto-set by Render)
   - Click "Create Web Service"
   - Note your API URL: `https://nids-api.onrender.com`

**Option B: Use Your Existing Streamlit Service**

You can access your Streamlit app, but for a separate frontend, you'll need the Flask API.

---

### Step 2: Create Next.js Frontend Project

1. **Create a new Next.js project:**
   ```bash
   npx create-next-app@latest nids-frontend
   cd nids-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install axios
   npm install recharts  # For charts (alternative to plotly)
   ```

3. **Create the frontend structure:**
   ```
   nids-frontend/
   ├── pages/
   │   ├── index.js          # Main dashboard page
   │   └── api/
   │       └── proxy.js      # API proxy (optional)
   ├── components/
   │   ├── Stats.js          # Statistics component
   │   ├── AlertsTable.js    # Alerts table component
   │   └── Charts.js         # Charts component
   ├── public/
   └── package.json
   ```

---

### Step 3: Build Frontend Components

**Create `pages/index.js`:**
```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';
import Stats from '../components/Stats';
import AlertsTable from '../components/AlertsTable';
import Charts from '../components/Charts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://nids-api.onrender.com';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
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
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>🛡️ Network Intrusion Detection System</h1>
      <Stats data={stats} />
      <Charts alerts={alerts} />
      <AlertsTable alerts={alerts} />
    </div>
  );
}
```

**Create `components/Stats.js`:**
```javascript
export default function Stats({ data }) {
  if (!data) return null;

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <h3>Total Packets</h3>
        <p>{data.total_packets?.toLocaleString() || 0}</p>
      </div>
      <div className="stat-card">
        <h3>Normal Traffic</h3>
        <p>{data.normal_traffic?.toLocaleString() || 0}</p>
        <span>{data.normal_percentage?.toFixed(2)}%</span>
      </div>
      <div className="stat-card">
        <h3>Attacks Detected</h3>
        <p>{data.attacks_detected?.toLocaleString() || 0}</p>
        <span>{data.attack_percentage?.toFixed(2)}%</span>
      </div>
      <div className="stat-card">
        <h3>Last Updated</h3>
        <p>{data.last_updated || 'N/A'}</p>
      </div>
    </div>
  );
}
```

**Create `components/AlertsTable.js`:**
```javascript
export default function AlertsTable({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <div className="no-alerts">No alerts detected yet.</div>;
  }

  return (
    <div className="alerts-table">
      <h2>Recent Alerts</h2>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Source IP</th>
            <th>Destination IP</th>
            <th>Protocol</th>
            <th>Size (bytes)</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert, index) => (
            <tr key={index}>
              <td>{alert.timestamp}</td>
              <td>{alert.src_ip}:{alert.src_port}</td>
              <td>{alert.dst_ip}:{alert.dst_port}</td>
              <td>{alert.protocol}</td>
              <td>{alert.size}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Create `components/Charts.js`:**
```javascript
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function Charts({ alerts }) {
  if (!alerts || alerts.length === 0) return null;

  // Process data for charts
  const protocolCounts = alerts.reduce((acc, alert) => {
    acc[alert.protocol] = (acc[alert.protocol] || 0) + 1;
    return acc;
  }, {});

  const protocolData = Object.entries(protocolCounts).map(([name, value]) => ({
    name,
    value
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div className="charts">
      <div className="chart-container">
        <h3>Attack Distribution by Protocol</h3>
        <PieChart width={400} height={300}>
          <Pie
            data={protocolData}
            cx={200}
            cy={150}
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {protocolData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </div>
    </div>
  );
}
```

**Create `styles/globals.css`:**
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #0e1117;
  color: #ffffff;
  padding: 20px;
}

.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 30px;
  color: #ffffff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: #1e1e1e;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #333;
}

.stat-card h3 {
  color: #888;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-card p {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
}

.alerts-table {
  margin-top: 30px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #333;
}

th {
  background-color: #2a2a2a;
  color: #fff;
  font-weight: 600;
}

tr:hover {
  background-color: #2a2a2a;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 18px;
}

.no-alerts {
  text-align: center;
  padding: 30px;
  color: #888;
}
```

---

### Step 4: Configure Environment Variables

**Create `.env.local` (for local development):**
```env
NEXT_PUBLIC_API_URL=https://nids-api.onrender.com
```

**For Vercel:**
- Go to your Vercel project → Settings → Environment Variables
- Add: `NEXT_PUBLIC_API_URL` = `https://nids-api.onrender.com`

---

### Step 5: Deploy on Vercel

1. **Push to GitHub:**
   ```bash
   cd nids-frontend
   git init
   git add .
   git commit -m "NIDS Frontend"
   git remote add origin https://github.com/YOUR_USERNAME/nids-frontend.git
   git push -u origin main
   ```

2. **Deploy on Vercel:**
   - Go to https://vercel.com
   - Click "Add New Project"
   - Import your `nids-frontend` repository
   - **Settings:**
     - Framework Preset: `Next.js` (auto-detected)
     - Root Directory: `./`
     - Build Command: `npm run build` (default)
     - Output Directory: `.next` (default)
   - **Environment Variables:**
     - Add `NEXT_PUBLIC_API_URL` = `https://nids-api.onrender.com`
   - Click "Deploy"

3. **Access Your Frontend:**
   - Vercel will provide: `https://nids-frontend.vercel.app`
   - Your frontend will call your Render API backend

---

## 🔧 Quick Setup Script

**Create `setup-frontend.sh`:**
```bash
#!/bin/bash
echo "Setting up NIDS Frontend..."

# Create Next.js app
npx create-next-app@latest nids-frontend --yes

cd nids-frontend

# Install dependencies
npm install axios recharts

# Create directory structure
mkdir -p components pages/api public styles

echo "✅ Frontend setup complete!"
echo "Next steps:"
echo "1. Copy component files to components/"
echo "2. Copy pages/index.js"
echo "3. Add styles to styles/globals.css"
echo "4. Set NEXT_PUBLIC_API_URL environment variable"
echo "5. Deploy to Vercel"
```

---

## 📝 Summary

**If using Streamlit only (Recommended):**
- ✅ Already deployed on Render
- ✅ Access at: `https://your-app.onrender.com`
- ✅ No additional steps needed

**If using separate frontend:**
1. Deploy Flask API on Render (separate service)
2. Create Next.js frontend
3. Deploy frontend on Vercel
4. Connect frontend to API via environment variable

---

## 🆘 Troubleshooting

**CORS Errors:**
- Ensure `flask-cors` is installed in your API
- Check CORS is enabled: `CORS(app)` in `api.py`

**API Not Responding:**
- Check Render service is running
- Verify API URL is correct
- Check Render logs for errors

**Frontend Build Fails:**
- Ensure all dependencies are in `package.json`
- Check for syntax errors in components
- Verify environment variables are set

---

**Need Help?** Check the main [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for more details.

