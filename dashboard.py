"""
NIDS Real-Time Dashboard
Streamlit-based dashboard for monitoring network intrusion detection system.
Reads from alerts.log and nids_stats.txt for real-time visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import re
from collections import Counter

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
                # Skip header if exists
                start_idx = 0
                if lines and '=== NIDS Alert Log' in lines[0]:
                    start_idx = 2
                
                for line in lines[start_idx:]:
                    line = line.strip()
                    if line and '[ALERT]' in line:
                        try:
                            # Parse: [timestamp] [ALERT] Malicious Traffic Detected! Src: IP:port -> Dst: IP:port Protocol: PROTO Size: size bytes
                            timestamp_match = re.search(r'\[([^\]]+)\]', line)
                            timestamp = timestamp_match.group(1) if timestamp_match else 'N/A'
                            
                            src_match = re.search(r'Src:\s+([^\s:]+):(\d+)', line)
                            src_ip = src_match.group(1) if src_match else 'N/A'
                            src_port = src_match.group(2) if src_match else 'N/A'
                            
                            dst_match = re.search(r'Dst:\s+([^\s:]+):(\d+)', line)
                            dst_ip = dst_match.group(1) if dst_match else 'N/A'
                            dst_port = dst_match.group(2) if dst_match else 'N/A'
                            
                            proto_match = re.search(r'Protocol:\s+(\w+)', line)
                            protocol = proto_match.group(1) if proto_match else 'N/A'
                            
                            size_match = re.search(r'Size:\s+(\d+)', line)
                            size = size_match.group(1) if size_match else 'N/A'
                            
                            alerts.append({
                                'timestamp': timestamp,
                                'src_ip': src_ip,
                                'src_port': src_port,
                                'dst_ip': dst_ip,
                                'dst_port': dst_port,
                                'protocol': protocol,
                                'size': int(size) if size != 'N/A' else 0
                            })
                        except Exception as e:
                            continue
            
            # Return most recent alerts first
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
    
    # Convert timestamp to datetime
    alerts_df['datetime'] = pd.to_datetime(alerts_df['timestamp'], errors='coerce')
    alerts_df = alerts_df.dropna(subset=['datetime'])
    
    if alerts_df.empty:
        return None
    
    # Group by time intervals (e.g., every minute)
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

# Main dashboard
def main():
    st.title("🛡️ Network Intrusion Detection System Dashboard")
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
    with col2:
        refresh_interval = st.selectbox("Interval", [5, 10, 30], index=0)
    
    # Statistics section
    stats = parse_stats()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Packets", f"{stats['total_packets']:,}")
    with col2:
        st.metric("Normal Traffic", f"{stats['normal_traffic']:,}", 
                 f"{stats['normal_percentage']:.2f}%")
    with col3:
        st.metric("Attacks Detected", f"{stats['attacks_detected']:,}", 
                 f"{stats['attack_percentage']:.2f}%", delta_color="inverse")
    with col4:
        st.metric("Last Updated", stats['last_updated'])
    
    st.divider()
    
    # Parse alerts
    alerts = parse_alerts(limit=500)
    alerts_df = pd.DataFrame(alerts)
    
    if not alerts_df.empty:
        # Filters sidebar
        with st.sidebar:
            st.header("🔍 Filters")
            
            # Protocol filter
            protocols = ['All'] + sorted(alerts_df['protocol'].unique().tolist())
            selected_protocol = st.selectbox("Protocol", protocols)
            
            # Time range filter
            time_range = None
            if 'timestamp' in alerts_df.columns and not alerts_df.empty:
                alerts_df['datetime'] = pd.to_datetime(alerts_df['timestamp'], errors='coerce')
                alerts_df = alerts_df.dropna(subset=['datetime'])
                
                if not alerts_df.empty:
                    min_time = alerts_df['datetime'].min()
                    max_time = alerts_df['datetime'].max()
                    
                    if pd.notna(min_time) and pd.notna(max_time):
                        try:
                            time_range = st.slider(
                                "Time Range",
                                min_value=min_time,
                                max_value=max_time,
                                value=(min_time, max_time),
                                format="YYYY-MM-DD HH:mm"
                            )
                        except Exception:
                            # Fallback if slider fails
                            time_range = (min_time, max_time)
        
        # Apply filters
        filtered_df = alerts_df.copy()
        if selected_protocol != 'All':
            filtered_df = filtered_df[filtered_df['protocol'] == selected_protocol]
        
        if time_range is not None and 'datetime' in filtered_df.columns:
            try:
                if pd.notna(time_range[0]) and pd.notna(time_range[1]):
                    filtered_df = filtered_df[
                        (filtered_df['datetime'] >= time_range[0]) & 
                        (filtered_df['datetime'] <= time_range[1])
                    ]
            except Exception:
                pass  # Skip time filtering if it fails
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            protocol_chart = create_protocol_chart(filtered_df)
            if protocol_chart:
                st.plotly_chart(protocol_chart, use_container_width=True)
        
        with col2:
            time_chart = create_time_series_chart(filtered_df)
            if time_chart:
                st.plotly_chart(time_chart, use_container_width=True)
        
        # Top IPs table
        st.subheader("🔴 Top Source IPs by Attack Count")
        top_ips = get_top_ips(filtered_df, top_n=10)
        if not top_ips.empty:
            st.dataframe(top_ips, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Alerts table
        st.subheader("📋 Recent Alerts")
        
        # Display options
        display_cols = st.multiselect(
            "Select columns to display",
            options=['timestamp', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol', 'size'],
            default=['timestamp', 'src_ip', 'dst_ip', 'protocol', 'size']
        )
        
        if display_cols:
            display_df = filtered_df[display_cols].copy()
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
    else:
        st.info("No alerts detected yet. The system is monitoring network traffic...")
        st.info("Start the NIDS backend with: `python live_nids.py`")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()

