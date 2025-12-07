"""
NIDS Real-Time Dashboard
Streamlit-based dashboard for monitoring network intrusion detection system.
Reads from alerts.log and nids_stats.txt for real-time visualization.
Automatically starts backend (live_nids.py) when deployed on Render.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import re
import threading
import subprocess
from collections import Counter

# ---------------------------
# AUTO START BACKEND SIMULATION
# ---------------------------
def start_backend():
    """Start backend simulation in background if not already running."""
    if not os.path.exists("backend_running.flag"):
        open("backend_running.flag", "w").close()
        try:
            subprocess.Popen(["python", "live_nids.py"])
            print("✅ Backend simulation started automatically on Render")
        except Exception as e:
            print(f"⚠️ Failed to start backend: {e}")

# Start backend in a background thread
threading.Thread(target=start_backend, daemon=True).start()

# ---------------------------
# STREAMLIT DASHBOARD
# ---------------------------

# Page configuration
st.set_page_config(
    page_title="NIDS Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 5px;
    }
    .stAlert {
        background-color: #1e1e1e;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# File paths
ALERTS_LOG = 'alerts.log'
STATS_FILE = 'nids_stats.txt'

def parse_stats():
    """Parse statistics from nids_stats.txt"""
    stats = {
        'total_packets': 0,
        'normal_traffic': 0,
        'attacks_detected': 0,
        'normal_percentage': 0.0,
        'attack_percentage': 0.0,
        'last_updated': 'N/A'
    }
    
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'Total Packets Analyzed:' in line:
                        stats['total_packets'] = int(re.search(r'\d+', line).group())
                    elif 'Normal Traffic:' in line:
                        match = re.search(r'(\d+)\s+\(([\d.]+)%\)', line)
                        if match:
                            stats['normal_traffic'] = int(match.group(1))
                            stats['normal_percentage'] = float(match.group(2))
                    elif 'Attacks Detected:' in line:
                        match = re.search(r'(\d+)\s+\(([\d.]+)%\)', line)
                        if match:
                            stats['attacks_detected'] = int(match.group(1))
                            stats['attack_percentage'] = float(match.group(2))
                    elif 'Last Updated:' in line:
                        stats['last_updated'] = line.split(':', 1)[1].strip()
        except Exception as e:
            st.error(f"Error reading stats: {e}")
    
    return stats

def parse_alerts(limit=100):
    """Parse alerts from alerts.log"""
    alerts = []
    
    if os.path.exists(ALERTS_LOG):
        try:
            with open(ALERTS_LOG, 'r') as f:
                lines = f.readlines()
                start_idx = 0
                if lines and '=== NIDS Alert Log' in lines[0]:
                    start_idx = 2
                
                for line in lines[start_idx:]:
                    line = line.strip()
                    if line and 'ALERT' in line:
                        try:
                            timestamp_match = re.search(r'\[([^\]]+)\]', line)
                            timestamp = timestamp_match.group(1) if timestamp_match else 'N/A'
                            
                            size_match = re.search(r'(\d+)\s+suspicious', line)
                            size = size_match.group(1) if size_match else 'N/A'
                            
                            alerts.append({
                                'timestamp': timestamp,
                                'src_ip': 'Simulated',
                                'dst_ip': 'Simulated',
                                'protocol': 'TCP',
                                'size': int(size) if size != 'N/A' else 0
                            })
                        except Exception:
                            continue
            
            alerts.reverse()
            return alerts[:limit]
        except Exception as e:
            st.error(f"Error reading alerts: {e}")
    
    return alerts

def create_protocol_chart(alerts_df):
    """Create protocol distribution chart"""
    if alerts_df.empty:
        return None
    
    protocol_counts = alerts_df['protocol'].value_counts()
    
    fig = px.pie(
        values=protocol_counts.values,
        names=protocol_counts.index,
        title="Attack Distribution by Protocol",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='white'
    )
    return fig

def create_time_series_chart(alerts_df):
    """Create time series chart of attacks over time"""
    if alerts_df.empty:
        return None
    
    alerts_df['datetime'] = pd.to_datetime(alerts_df['timestamp'], errors='coerce')
    alerts_df = alerts_df.dropna(subset=['datetime'])
    
    if alerts_df.empty:
        return None
    
    alerts_df['time_bucket'] = alerts_df['datetime'].dt.floor('1min')
    time_counts = alerts_df.groupby('time_bucket').size().reset_index(name='count')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_counts['time_bucket'],
        y=time_counts['count'],
        mode='lines+markers',
        name='Attacks',
        line=dict(color='#ff4444', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 68, 68, 0.2)'
    ))
    
    fig.update_layout(
        title="Attacks Detected Over Time",
        xaxis_title="Time",
        yaxis_title="Number of Attacks",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='white'
    )
    
    return fig

def get_top_ips(alerts_df, top_n=10):
    """Get top source IPs by attack count"""
    if alerts_df.empty:
        return pd.DataFrame()
    
    ip_counts = alerts_df['src_ip'].value_counts().head(top_n)
    return pd.DataFrame({
        'Source IP': ip_counts.index,
        'Attack Count': ip_counts.values
    })

# ---------------------------
# MAIN DASHBOARD FUNCTION
# ---------------------------

def main():
    st.title("🛡️ Network Intrusion Detection System Dashboard")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
    with col2:
        refresh_interval = st.selectbox("Interval", [5, 10, 30], index=0)
    
    stats = parse_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Packets", f"{stats['total_packets']:,}")
    with col2:
        st.metric("Normal Traffic", f"{stats['normal_traffic']:,}", f"{stats['normal_percentage']:.2f}%")
    with col3:
        st.metric("Attacks Detected", f"{stats['attacks_detected']:,}", f"{stats['attack_percentage']:.2f}%", delta_color="inverse")
    with col4:
        st.metric("Last Updated", stats['last_updated'])
    
    st.divider()
    
    alerts = parse_alerts(limit=500)
    alerts_df = pd.DataFrame(alerts)
    
    if not alerts_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            protocol_chart = create_protocol_chart(alerts_df)
            if protocol_chart:
                st.plotly_chart(protocol_chart, use_container_width=True)
        
        with col2:
            time_chart = create_time_series_chart(alerts_df)
            if time_chart:
                st.plotly_chart(time_chart, use_container_width=True)
        
        st.subheader("🔴 Top Source IPs by Attack Count")
        top_ips = get_top_ips(alerts_df, top_n=10)
        if not top_ips.empty:
            st.dataframe(top_ips, use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.subheader("📋 Recent Alerts")
        st.dataframe(alerts_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("No alerts detected yet. The system is monitoring network traffic...")
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
