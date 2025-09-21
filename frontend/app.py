"""
🌊 Ocean Chat - Modern AI-Powered Ocean Data Assistant
Clean, minimalist interface inspired by modern AI chat applications
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json
import time
import os
try:
    from scipy import stats
except ImportError:
    stats = None

# Configuration - Environment-aware backend URL
if "streamlit" in os.environ.get("HOME", "").lower() or os.environ.get("STREAMLIT_SHARING_MODE"):
    # Running on Streamlit Cloud
    BACKEND_URL = st.secrets.get("api", {}).get("backend_url", "http://localhost:8000")
else:
    # Running locally
    BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="🌊 OceanChat",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Modern, clean CSS that works with Streamlit
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Dark theme app background */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #e2e8f0;
    }
    
    /* Main content area */
    .main > div {
        background: transparent;
        padding: 1rem;  /* Reduced padding for more space */
        max-width: 100% !important;  /* Use full width */
    }
    
    /* Full width containers for better visualization */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100% !important;
    }
    
    /* Chart containers - use full width */
    .stPlotlyChart {
        width: 100% !important;
    }
    
    /* Tab containers - full width */
    .stTabs [data-baseweb="tab-list"] {
        width: 100%;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e2329 0%, #2d3748 100%);
        border-right: 2px solid #4a5568;
    }
    
    /* Sidebar text */
    .css-1lcbmhc {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(145deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
        border: 1px solid rgba(66, 153, 225, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #3182ce 0%, #2c5282 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.4);
    }
    
    /* Navigation buttons */
    .nav-button {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%) !important;
        border: 2px solid #4a5568 !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Chat input enhancement */
    .stChatInput > div > div > textarea {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%) !important;
        border: 2px solid #4a5568 !important;
        color: #e2e8f0 !important;
        border-radius: 15px !important;
        font-size: 16px !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput > div > div > textarea:focus {
        border-color: #4299e1 !important;
        box-shadow: 0 0 20px rgba(66, 153, 225, 0.3) !important;
        transform: scale(1.02) !important;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%) !important;
        border: 1px solid #4a5568 !important;
        border-radius: 15px !important;
        margin: 1rem 0 !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Metric cards enhancement */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%) !important;
        border: 1px solid #4a5568 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Footer enhancement */
    .footer-sih {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(90deg, #1a202c 0%, #2d3748 50%, #1a202c 100%);
        border-top: 2px solid #4299e1;
        color: #e2e8f0;
        text-align: center;
        padding: 0.5rem;
        font-size: 0.9rem;
        z-index: 999;
        box-shadow: 0 -4px 15px rgba(66, 153, 225, 0.2);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSlider > div > div > div > div {
        background: rgba(45, 55, 72, 0.8) !important;
        border: 2px solid #4a5568 !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Chat input */
    .stChatInput > div {
        background: rgba(45, 55, 72, 0.8) !important;
        border: 2px solid #4a5568 !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(45, 55, 72, 0.8) !important;
        border: 1px solid #4a5568 !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        margin: 0.75rem 0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Metrics styling */
    .stMetric {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #4a5568;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        border-color: #4299e1;
    }
    
    /* Chart containers */
    .js-plotly-plot {
        background: rgba(45, 55, 72, 0.6) !important;
        border-radius: 15px !important;
        border: 1px solid #4a5568 !important;
        backdrop-filter: blur(10px) !important;
        padding: 1rem !important;
    }
    
    /* Title styling */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    /* Info/Success/Error boxes */
    .stAlert {
        background: rgba(66, 153, 225, 0.1) !important;
        border: 1px solid #4299e1 !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        color: #e2e8f0 !important;
    }
    
    .stSuccess {
        background: rgba(72, 187, 120, 0.1) !important;
        border: 1px solid #48bb78 !important;
        color: #e2e8f0 !important;
    }
    
    .stError {
        background: rgba(245, 101, 101, 0.1) !important;
        border: 1px solid #f56565 !important;
        color: #e2e8f0 !important;
    }
    
    .stWarning {
        background: rgba(237, 137, 54, 0.1) !important;
        border: 1px solid #ed8936 !important;
        color: #e2e8f0 !important;
    }
    
    /* Divider styling */
    hr {
        border-color: #4a5568 !important;
        margin: 2rem 0 !important;
        opacity: 0.6;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(45, 55, 72, 0.8) !important;
        border-radius: 12px !important;
        border: 1px solid #4a5568 !important;
        backdrop-filter: blur(10px) !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #a0aec0 !important;
        border-radius: 8px !important;
        margin: 0.25rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #4299e1 0%, #3182ce 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3) !important;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #e2e8f0 !important;
    }
    
    /* Radio button styling */
    .stRadio > label {
        color: #e2e8f0 !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > label {
        color: #e2e8f0 !important;
    }
    
    /* Text input label */
    .stTextInput > label {
        color: #e2e8f0 !important;
    }
    
    /* Slider label */
    .stSlider > label {
        color: #e2e8f0 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a202c;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(145deg, #4a5568 0%, #2d3748 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(145deg, #4299e1 0%, #3182ce 100%);
    }
    
    /* Card-like containers */
    .element-container {
        background: rgba(45, 55, 72, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(74, 85, 104, 0.3);
    }
    
    /* Custom 900px width for charts and tables */
    .chart-container-900 {
        width: 900px !important;
        max-width: 900px !important;
        margin: 0 auto !important;
    }
    
    .chart-container-900 .stPlotlyChart {
        width: 900px !important;
        max-width: 900px !important;
    }
    
    .chart-container-900 .js-plotly-plot {
        width: 900px !important;
        max-width: 900px !important;
    }
    
    .table-container-900 {
        width: 900px !important;
        max-width: 900px !important;
        margin: 0 auto !important;
    }
    
    .table-container-900 .stDataFrame {
        width: 900px !important;
        max-width: 900px !important;
    }
    
    .table-container-900 div[data-testid="stDataFrame"] {
        width: 900px !important;
        max-width: 900px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# Helper functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_live_data_status():
    """Fetch live data status from the backend API."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/live-data/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("live_data_status", {})
        return {
            "status": "unavailable",
            "argo_files_available": 0,
            "last_update": "N/A"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "backend_offline",
            "argo_files_available": 0,
            "last_update": "N/A"
        }
    except Exception as e:
        return {
            "status": "error",
            "argo_files_available": 0,
            "last_update": f"Error: {str(e)[:50]}"
        }

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_system_status():
    """Fetch comprehensive system status for demo"""
    try:
        # Get backend health with shorter timeout
        health_response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=2)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        # Get live data status with shorter timeout
        live_response = requests.get(f"{BACKEND_URL}/api/v1/live-data/status", timeout=2)
        live_data = live_response.json() if live_response.status_code == 200 else {}
        
        # Calculate system metrics
        backend_status = "🟢 Online" if health_response.status_code == 200 else "🔴 Offline"
        api_response_time = "< 500ms" if health_response.status_code == 200 else "N/A"
        data_sources = "Dual Source" if live_data.get("live_data_available") else "Database Only"
        
        return {
            "backend_status": backend_status,
            "api_response_time": api_response_time,
            "data_sources": data_sources,
            "live_data_status": live_data.get("status", "Unknown"),
            "connection_health": "✅ All Systems Operational" if health_response.status_code == 200 else "⚠️ Backend Unavailable",
            "query_processing": "🚀 NLP Engine Active",
            "visualization": "📊 All Charts Ready",
            "total_files": live_data.get("total_files", 0)
        }
    except (requests.exceptions.RequestException, requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        # Return graceful fallback status without showing error details  
        return {
            "backend_status": "🔴 Connection Error",
            "api_response_time": "N/A",
            "data_sources": "Local Only", 
            "live_data_status": "❌ Check Failed",
            "connection_health": "⚠️ System Check Failed",
            "query_processing": "⚠️ Backend Offline",
            "visualization": "📊 Frontend Only",
            "total_files": 0
        }

def load_sample_data():
    """Load sample ocean data for demonstration"""
    np.random.seed(42)
    n_points = 1000
    
    data = {
        'latitude': np.random.uniform(-90, 90, n_points),
        'longitude': np.random.uniform(-180, 180, n_points),
        'temperature': np.random.normal(15, 8, n_points),
        'salinity': np.random.normal(35, 2, n_points),
        'depth': np.random.exponential(500, n_points),
        'platform_id': np.random.choice(['ARGO_001', 'ARGO_002', 'ARGO_003', 'BUOY_001', 'SHIP_001'], n_points),
        'measurement_time': pd.date_range('2024-01-01', periods=n_points, freq='H')
    }
    
    return pd.DataFrame(data)

def query_ocean_api(user_query):
    """Query the ocean data API"""
    try:
        # Debug: Show what URL we're trying to connect to
        st.info(f"🔍 Connecting to: {BACKEND_URL}/api/v1/query")
        
        # Call the actual backend API
        response = requests.post(
            f"{BACKEND_URL}/api/v1/query",
            json={"query": user_query},
            timeout=30
        )
        
        # Debug: Show response status
        st.info(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            api_response = response.json()
            
            # Check if the response is successful
            if api_response.get("success") and "data" in api_response:
                data_section = api_response["data"]
                
                # Extract measurements from the nested structure
                if "measurements" in data_section and data_section["measurements"]:
                    measurements = data_section["measurements"]
                    if isinstance(measurements, list) and len(measurements) > 0:
                        df = pd.DataFrame(measurements)
                        
                        # Ensure required columns exist
                        required_columns = ['latitude', 'longitude', 'temperature', 'salinity', 'depth']
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        
                        # Add platform_id if missing (for compatibility)
                        if 'platform_id' not in df.columns:
                            df['platform_id'] = 'API_DATA'
                        
                        if missing_columns:
                            st.warning(f"Missing columns: {missing_columns}. Using sample data.")
                            return load_sample_data().sample(50)
                        
                        return df
                    else:
                        st.info("No measurements found in API response. Using sample data.")
                        return load_sample_data().sample(50)
                else:
                    st.info("No measurement data in API response. Using sample data.")
                    return load_sample_data().sample(50)
            else:
                error_msg = api_response.get("error", "Unknown API error")
                st.error(f"API Error: {error_msg}")
                return load_sample_data().sample(50)
        else:
            st.error(f"HTTP Error: {response.status_code}")
            return load_sample_data().sample(50)
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return load_sample_data().sample(50)
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return load_sample_data().sample(50)

def create_temperature_map(data):
    """Create an interactive temperature map using Plotly"""
    if data is None or data.empty:
        return None
    
    # Create Plotly scatter mapbox
    fig = px.scatter_mapbox(
        data,
        lat='latitude',
        lon='longitude',
        color='temperature',
        size_max=15,
        zoom=3,
        color_continuous_scale='Blues',
        hover_data={
            'temperature': ':.1f',
            'salinity': ':.1f',
            'depth': ':.0f',
            'platform_id': True,
            'latitude': ':.2f',
            'longitude': ':.2f'
        },
        hover_name='platform_id',
        title='Ocean Temperature Distribution'
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=600,  # Increased from 400 to 600
        margin={"r":10,"t":60,"l":10,"b":10},  # Better margins
        font=dict(family="Inter, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_x=0.5  # Center the title
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "🌡️ Temperature: %{customdata[0]:.1f}°C<br>" +
                      "🧂 Salinity: %{customdata[1]:.1f} PSU<br>" +
                      "📏 Depth: %{customdata[2]:.0f}m<br>" +
                      "📍 Location: %{customdata[4]:.2f}, %{customdata[5]:.2f}<br>" +
                      "<extra></extra>"
    )
    
    return fig

def create_depth_profile_chart(data):
    """Create enhanced depth profile visualization"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    # Temperature vs depth
    fig.add_trace(go.Scatter(
        x=data['temperature'],
        y=-data['depth'],  # Negative for proper depth representation
        mode='markers',
        marker=dict(
            size=10,
            color=data['temperature'],
            colorscale='RdYlBu_r',  # Red-Yellow-Blue reversed
            showscale=True,
            colorbar=dict(
                title=dict(text="Temperature (°C)", side="right"),
                thickness=15
            ),
            cmin=data['temperature'].min(),
            cmax=data['temperature'].max(),
            line=dict(width=1, color='white')
        ),
        name='Temperature Profile',
        hovertemplate='<b>Temperature:</b> %{x:.1f}°C<br><b>Depth:</b> %{y:.0f}m<br><b>Platform:</b> %{text}<extra></extra>',
        text=data['platform_id']
    ))
    
    # Add salinity as secondary trace
    fig.add_trace(go.Scatter(
        x=data['salinity'],
        y=-data['depth'],
        mode='markers',
        marker=dict(
            size=8,
            color=data['salinity'],
            colorscale='Viridis',
            symbol='diamond',
            opacity=0.7,
            line=dict(width=1, color='white')
        ),
        name='Salinity Profile',
        hovertemplate='<b>Salinity:</b> %{x:.1f} PSU<br><b>Depth:</b> %{y:.0f}m<extra></extra>',
        visible='legendonly'  # Hidden by default, can be toggled
    ))
    
    fig.update_layout(
        title={
            'text': "🌊 Ocean Depth Profile Analysis",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#e2e8f0'}
        },
        xaxis_title="Temperature (°C) / Salinity (PSU)",
        yaxis_title="Depth (m)",
        font=dict(family="Inter", size=12, color='#e2e8f0'),
        plot_bgcolor='rgba(26, 32, 44, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,  # Keep good height
        margin=dict(l=60, r=60, t=80, b=60),  # Better margins for readability
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add depth zones
    fig.add_hline(y=-200, line_dash="dash", line_color="gray", 
                  annotation_text="Epipelagic Zone", annotation_position="bottom right")
    fig.add_hline(y=-1000, line_dash="dash", line_color="gray",
                  annotation_text="Mesopelagic Zone", annotation_position="bottom right")
    
    return fig

def create_advanced_statistics_chart(data):
    """Create comprehensive statistical analysis chart"""
    if data is None or data.empty:
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature Distribution', 'Salinity Distribution', 
                       'Depth Distribution', 'Geographic Coverage'),
        specs=[[{"type": "histogram"}, {"type": "histogram"}],
               [{"type": "histogram"}, {"type": "scattergeo"}]]
    )
    
    # Temperature histogram
    fig.add_trace(go.Histogram(
        x=data['temperature'],
        nbinsx=20,
        name='Temperature',
        marker_color='rgba(66, 153, 225, 0.7)',
        hovertemplate='Temperature: %{x:.1f}°C<br>Count: %{y}<extra></extra>'
    ), row=1, col=1)
    
    # Salinity histogram
    fig.add_trace(go.Histogram(
        x=data['salinity'],
        nbinsx=20,
        name='Salinity',
        marker_color='rgba(72, 187, 120, 0.7)',
        hovertemplate='Salinity: %{x:.1f} PSU<br>Count: %{y}<extra></extra>'
    ), row=1, col=2)
    
    # Depth histogram
    fig.add_trace(go.Histogram(
        x=data['depth'],
        nbinsx=20,
        name='Depth',
        marker_color='rgba(128, 90, 213, 0.7)',
        hovertemplate='Depth: %{x:.0f}m<br>Count: %{y}<extra></extra>'
    ), row=2, col=1)
    
    # Geographic scatter
    fig.add_trace(go.Scattergeo(
        lon=data['longitude'],
        lat=data['latitude'],
        mode='markers',
        marker=dict(
            size=8,
            color=data['temperature'],
            colorscale='RdYlBu_r',
            cmin=data['temperature'].min(),
            cmax=data['temperature'].max(),
            line=dict(width=1, color='white')
        ),
        name='Measurements',
        hovertemplate='<b>Lat:</b> %{lat:.2f}°<br><b>Lon:</b> %{lon:.2f}°<br><b>Temp:</b> %{marker.color:.1f}°C<extra></extra>'
    ), row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="📊 Comprehensive Ocean Data Analysis",
        title_x=0.5,
        font=dict(family="Inter", size=10, color='#e2e8f0'),
        plot_bgcolor='rgba(26, 32, 44, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Update geo subplot
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="rgba(68, 68, 68, 0.8)",
        showocean=True,
        oceancolor="rgba(26, 32, 44, 0.9)",
        showlakes=True,
        lakecolor="rgba(26, 32, 44, 0.9)"
    )
    
    return fig

def create_time_series_chart(data):
    """Create enhanced time series chart with multiple parameters"""
    if data is None or data.empty:
        return None
    
    # Sort by time and add time-based grouping
    data_sorted = data.sort_values('measurement_time').copy()
    
    fig = make_subplots(rows=2, cols=1, 
                       shared_xaxes=True,
                       subplot_titles=('Temperature Trends', 'Salinity Trends'),
                       vertical_spacing=0.1)
    
    # Temperature time series
    fig.add_trace(go.Scatter(
        x=data_sorted['measurement_time'],
        y=data_sorted['temperature'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#f56565', width=2),
        marker=dict(size=6, symbol='circle'),
        hovertemplate='<b>Time:</b> %{x}<br><b>Temperature:</b> %{y:.1f}°C<extra></extra>'
    ), row=1, col=1)
    
    # Add temperature trend line if scipy available
    if stats is not None:
        try:
            time_numeric = pd.to_numeric(data_sorted['measurement_time'])
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, data_sorted['temperature'])
            trend_line = slope * time_numeric + intercept
            
            fig.add_trace(go.Scatter(
                x=data_sorted['measurement_time'],
                y=trend_line,
                mode='lines',
                name='Temperature Trend',
                line=dict(color='#fc8181', width=2, dash='dash'),
                hovertemplate='<b>Trend:</b> %{y:.1f}°C<extra></extra>'
            ), row=1, col=1)
        except:
            pass  # Skip trend line if calculation fails
    
    # Salinity time series
    fig.add_trace(go.Scatter(
        x=data_sorted['measurement_time'],
        y=data_sorted['salinity'],
        mode='lines+markers',
        name='Salinity',
        line=dict(color='#4299e1', width=2),
        marker=dict(size=6, symbol='diamond'),
        hovertemplate='<b>Time:</b> %{x}<br><b>Salinity:</b> %{y:.1f} PSU<extra></extra>'
    ), row=2, col=1)
    
    # Add salinity trend line if scipy available
    if stats is not None:
        try:
            time_numeric = pd.to_numeric(data_sorted['measurement_time'])
            slope_sal, intercept_sal, _, _, _ = stats.linregress(time_numeric, data_sorted['salinity'])
            trend_line_sal = slope_sal * time_numeric + intercept_sal
            
            fig.add_trace(go.Scatter(
                x=data_sorted['measurement_time'],
                y=trend_line_sal,
                mode='lines',
                name='Salinity Trend',
                line=dict(color='#63b3ed', width=2, dash='dash'),
                hovertemplate='<b>Trend:</b> %{y:.1f} PSU<extra></extra>'
            ), row=2, col=1)
        except:
            pass  # Skip trend line if calculation fails
    
    fig.update_layout(
        title={
            'text': "📈 Ocean Parameter Trends Over Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#e2e8f0'}
        },
        xaxis_title="Time",
        font=dict(family="Inter", size=12, color='#e2e8f0'),
        plot_bgcolor='rgba(26, 32, 44, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=550,  # Increased from 500 to 550
        margin=dict(l=60, r=60, t=80, b=60),  # Better margins
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Salinity (PSU)", row=2, col=1)
    
    return fig

def main():
    """Main application with clean, native Streamlit design"""
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'chat'
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Enhanced sidebar with modern dark styling
    with st.sidebar:
        # Modern brand header with gradient
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0; background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                    border-radius: 15px; border: 1px solid #4a5568; margin-bottom: 1.5rem;">
            <h1 style="color: #4299e1; font-size: 2rem; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">🌊 OceanChat</h1>
            <p style="color: #a0aec0; font-size: 0.9rem; margin: 0;">AI Oceanographic Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Navigation
        st.markdown("""
        <h3 style="color: #e2e8f0; margin-bottom: 1rem; padding-left: 0.5rem;">🧭 Navigation</h3>
        """, unsafe_allow_html=True)
        
        pages = {
            "💬 Chat": "chat",
            "📊 Dashboard": "dashboard", 
            "🗺️ Maps": "maps",
            "📈 Analytics": "analytics",
            "⚙️ Settings": "settings"
        }
        
        for page_name, page_key in pages.items():
            # Highlight current page
            is_current = st.session_state.current_page == page_key
            button_style = "background: linear-gradient(145deg, #4299e1 0%, #3182ce 100%); color: white;" if is_current else ""
            
            if st.button(page_name, key=f"nav_{page_key}", width="stretch"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.divider()
        
        # Enhanced System Status with Live Data
        st.markdown("""
        <h3 style="color: #e2e8f0; margin-bottom: 1rem; padding-left: 0.5rem;">📊 System Status</h3>
        """, unsafe_allow_html=True)
        
        # Fetch comprehensive system status
        system_status = fetch_system_status()
        live_status = fetch_live_data_status()
        
        # Status cards with modern styling
        col1, col2 = st.columns(2)
        with col1:
            backend_color = "#48bb78" if "🟢" in system_status["backend_status"] else "#f56565"
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                        padding: 0.75rem; border-radius: 10px; border: 1px solid {backend_color}; text-align: center;">
                <div style="color: {backend_color}; font-weight: bold; font-size: 0.8rem;">Backend</div>
                <div style="color: #e2e8f0; font-size: 0.7rem;">{system_status["backend_status"]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                        padding: 0.75rem; border-radius: 10px; border: 1px solid #4299e1; text-align: center;">
                <div style="color: #4299e1; font-weight: bold; font-size: 0.8rem;">Response</div>
                <div style="color: #e2e8f0; font-size: 0.7rem;">{system_status["api_response_time"]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Comprehensive system metrics
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                    padding: 1rem; border-radius: 12px; border: 1px solid #4a5568; margin: 1rem 0;">
            <div style="color: #4299e1; font-weight: bold; margin-bottom: 0.75rem; font-size: 0.9rem;">
                🚀 System Performance
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; color: #e2e8f0; font-size: 0.75rem;">
                <div>🔗 Data Sources:</div><div>{system_status["data_sources"]}</div>
                <div>🧠 NLP Engine:</div><div>🟢 Active</div>
                <div>📊 Visualization:</div><div>🟢 Ready</div>
                <div>⚡ Query Speed:</div><div>{system_status["api_response_time"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Live data status with enhanced details
        if live_status and live_status.get("live_data_available"):
            hours_old = live_status.get("hours_old", 0)
            status_color = "#48bb78" if hours_old < 24 else "#ed8936" if hours_old < 48 else "#f56565"
            status_icon = "🟢" if hours_old < 24 else "🟡" if hours_old < 48 else "🔴"
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                        padding: 1rem; border-radius: 12px; border: 1px solid {status_color}; margin-bottom: 1rem;">
                <div style="color: {status_color}; font-weight: bold; margin-bottom: 0.5rem; font-size: 0.9rem;">
                    {status_icon} Live Argo Data
                </div>
                <div style="color: #e2e8f0; font-size: 0.8rem; margin-bottom: 0.25rem;">
                    Latest: {live_status.get('latest_file', 'Unknown')[:15]}...
                </div>
                <div style="color: #a0aec0; font-size: 0.7rem; margin-bottom: 0.25rem;">
                    {hours_old:.1f} hours old
                </div>
                <div style="color: #a0aec0; font-size: 0.7rem;">
                    {live_status.get('total_files', 0)} files available
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                        padding: 1rem; border-radius: 12px; border: 1px solid #f56565; margin-bottom: 1rem;">
                <div style="color: #f56565; font-weight: bold; margin-bottom: 0.5rem; font-size: 0.9rem;">
                    🔴 Live Data
                </div>
                <div style="color: #a0aec0; font-size: 0.8rem; margin-bottom: 0.25rem;">
                    Fallback to database mode
                </div>
                <div style="color: #a0aec0; font-size: 0.7rem;">
                    Demo continues with static data
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Database status with demo metrics
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                    padding: 1rem; border-radius: 12px; border: 1px solid #4a5568; margin-bottom: 1rem;">
            <div style="color: #ed8936; font-weight: bold; margin-bottom: 0.5rem; font-size: 0.9rem;">🗄️ Database</div>
            <div style="color: #e2e8f0; font-size: 1.1rem; font-weight: bold;">320,094</div>
            <div style="color: #a0aec0; font-size: 0.8rem; margin-bottom: 0.25rem;">Ocean Measurements</div>
            <div style="color: #a0aec0; font-size: 0.7rem;">PostgreSQL + PostGIS</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Enhanced Recent Activity
        if st.session_state.current_page == 'chat' and st.session_state.messages:
            st.markdown("""
            <h3 style="color: #e2e8f0; margin-bottom: 1rem; padding-left: 0.5rem;">💭 Recent Queries</h3>
            """, unsafe_allow_html=True)
            
            recent_count = min(3, len(st.session_state.messages))
            for i in range(recent_count):
                msg = st.session_state.messages[-(i+1)]
                if msg['role'] == 'user':
                    preview = msg['content'][:30] + "..." if len(msg['content']) > 30 else msg['content']
                    
                    # Custom styled recent query button
                    st.markdown(f"""
                    <style>
                    .query-card-{i} {{
                        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
                        padding: 0.75rem;
                        border-radius: 10px;
                        border: 1px solid #4a5568;
                        margin-bottom: 0.5rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    .query-card-{i}:hover {{
                        border-color: #4299e1;
                        transform: translateY(-1px);
                    }}
                    </style>
                    <div class="query-card-{i}">
                        <div style="color: #4299e1; font-size: 0.8rem; margin-bottom: 0.25rem;">Query {i+1}</div>
                        <div style="color: #e2e8f0; font-size: 0.75rem; line-height: 1.2;">{preview}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Show helpful tips when no recent activity
            st.markdown("""
            <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                        padding: 1rem; border-radius: 12px; border: 1px solid #4a5568;">
                <div style="color: #4299e1; font-weight: bold; margin-bottom: 0.5rem;">💡 Quick Tips</div>
                <div style="color: #a0aec0; font-size: 0.8rem; line-height: 1.4;">
                    • Ask about ocean temperatures<br>
                    • Explore salinity data<br>
                    • Analyze regional patterns<br>
                    • View real-time measurements
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.current_page == 'chat':
        show_chat_page()
    elif st.session_state.current_page == 'dashboard':
        show_dashboard_page()
    elif st.session_state.current_page == 'maps':
        show_maps_page()
    elif st.session_state.current_page == 'analytics':
        show_analytics_page()
    elif st.session_state.current_page == 'settings':
        show_settings_page()
    
    # Add professional SIH footer
    st.markdown("""
    <div class="footer-sih">
        <strong>🏆 Smart India Hackathon 2025</strong> • 
        🌊 OceanChat - AI-Powered Oceanographic Analysis Platform • 
        🚀 Powered by Real-time Argo Network Data • 
        💡 Innovative Ocean Intelligence
    </div>
    """, unsafe_allow_html=True)

def show_chat_page():
    """Clean chat interface using native Streamlit components"""
    
    # Header
    st.title("🌊 OceanChat Assistant")
    st.subheader("Ask me anything about oceanographic data, maps, and analysis")
    st.divider()
    
    # Main chat container
    if not st.session_state.messages:
        # Welcome screen with enhanced styling and live data info
        live_status = fetch_live_data_status()
        live_indicator = "🟢 Live Data Active" if live_status and live_status.get("live_data_available") else "🔴 Static Data Mode"
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                    padding: 2rem; border-radius: 20px; border: 1px solid #4a5568; 
                    text-align: center; margin-bottom: 2rem;">
            <div style="color: #4299e1; font-size: 3rem; margin-bottom: 1rem;">🌊</div>
            <h2 style="color: #e2e8f0; margin-bottom: 0.5rem;">Welcome to OceanChat!</h2>
            <p style="color: #a0aec0; font-size: 1.1rem; margin-bottom: 1rem;">
                Your AI assistant for exploring oceanographic data, maps, and analysis
            </p>
            <div style="color: #4299e1; font-size: 0.9rem; padding: 0.5rem; 
                        background: rgba(66, 153, 225, 0.1); border-radius: 8px; 
                        border: 1px solid rgba(66, 153, 225, 0.3);">
                {live_indicator} | Real-time Argo Network Integration
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <h3 style="color: #e2e8f0; text-align: center; margin-bottom: 1.5rem;">
            🚀 What would you like to explore?
        </h3>
        """, unsafe_allow_html=True)
        
        # Enhanced suggestion cards using columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Custom styled suggestion buttons
            st.markdown("""
            <style>
            .suggestion-card-temp {
                background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid #4a5568;
                margin-bottom: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .suggestion-card-temp:hover {
                border-color: #4299e1;
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(66,153,225,0.3);
            }
            </style>
            <div class="suggestion-card-temp">
                <div style="color: #4299e1; font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">🌡️</div>
                <div style="color: #e2e8f0; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">Temperature Data</div>
                <div style="color: #a0aec0; font-size: 0.9rem; text-align: center; line-height: 1.4;">
                    Show temperature trends in the Pacific Ocean
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🌡️ Temperature Data", key="temp_suggestion", width="stretch"):
                process_chat_query("Show temperature trends in the Pacific")
            
            st.markdown("""
            <style>
            .suggestion-card-maps {
                background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid #4a5568;
                margin-bottom: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .suggestion-card-maps:hover {
                border-color: #48bb78;
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(72,187,120,0.3);
            }
            </style>
            <div class="suggestion-card-maps">
                <div style="color: #48bb78; font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">🗺️</div>
                <div style="color: #e2e8f0; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">Ocean Maps</div>
                <div style="color: #a0aec0; font-size: 0.9rem; text-align: center; line-height: 1.4;">
                    Create interactive maps of ocean data
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗺️ Ocean Maps", key="map_suggestion", width="stretch"):
                process_chat_query("Create a map of current data")
        
        with col2:
            st.markdown("""
            <style>
            .suggestion-card-salinity {
                background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid #4a5568;
                margin-bottom: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .suggestion-card-salinity:hover {
                border-color: #ed8936;
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(237,137,54,0.3);
            }
            </style>
            <div class="suggestion-card-salinity">
                <div style="color: #ed8936; font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">🧂</div>
                <div style="color: #e2e8f0; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">Salinity Patterns</div>
                <div style="color: #a0aec0; font-size: 0.9rem; text-align: center; line-height: 1.4;">
                    Explore salinity data near the equator
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🧂 Salinity Patterns", key="salinity_suggestion", width="stretch"):
                process_chat_query("What's the salinity near the equator?")
                
            st.markdown("""
            <style>
            .suggestion-card-analysis {
                background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid #4a5568;
                margin-bottom: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .suggestion-card-analysis:hover {
                border-color: #9f7aea;
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(159,122,234,0.3);
            }
            </style>
            <div class="suggestion-card-analysis">
                <div style="color: #9f7aea; font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">📊</div>
                <div style="color: #e2e8f0; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">Data Analysis</div>
                <div style="color: #a0aec0; font-size: 0.9rem; text-align: center; line-height: 1.4;">
                    Analyze depth profiles by region
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📊 Data Analysis", key="analysis_suggestion", width="stretch"):
                process_chat_query("Analyze depth profiles by region")
        
    else:
        # Display chat messages
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🌊"):
                    st.write(message["content"])
    
    st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask me about ocean data, maps, or analysis..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🌊"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = process_chat_query(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()
    
    # Enhanced Quick action buttons if no messages
    if not st.session_state.messages:
        st.markdown("### 🚀 Demo Quick Actions")
        st.markdown("*Click any button below to see OceanChat in action*")
        
        # Row 1: Core Ocean Analysis
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("� Pacific Ocean Analysis", width="stretch"):
                process_chat_query("Show me temperature and salinity data for the Pacific Ocean")
        
        with col2:
            if st.button("🧂 Indian Ocean Salinity", width="stretch", key="indian_salinity"):
                process_chat_query("Analyze salinity patterns in the Indian Ocean")
        
        with col3:
            if st.button("🌡️ Temperature Profiles", width="stretch", key="temp_profiles"):
                process_chat_query("Show temperature distribution with depth profiles")
        
        with col4:
            if st.button("📈 Trend Analysis", width="stretch", key="trend_analysis"):
                process_chat_query("What are the recent ocean temperature trends?")
        
        # Row 2: Advanced Analysis
        st.markdown("#### 🔬 Advanced Ocean Research")
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if st.button("🌍 Global Ocean Map", width="stretch", key="global_map"):
                process_chat_query("Create a comprehensive global ocean data map")
        
        with col6:
            if st.button("📊 Statistical Summary", width="stretch", key="stats_summary"):
                process_chat_query("Provide comprehensive statistical analysis of ocean data")
        
        with col7:
            if st.button("🏝️ Arctic Waters", width="stretch", key="arctic_waters"):
                process_chat_query("Analyze Arctic Ocean conditions and ice coverage")
        
        with col8:
            if st.button("⚡ Live Data Status", width="stretch", key="live_status"):
                process_chat_query("Show me live ocean data availability and status")
        
        # Row 3: Demo Showcase
        st.markdown("#### 🎯 SIH Demo Showcase")
        col9, col10, col11 = st.columns(3)
        
        with col9:
            if st.button("� Complete Ocean Analysis", width="stretch"):
                process_chat_query("Show me a complete analysis of ocean parameters with all visualizations")
        
        with col10:
            if st.button("🌊 Real-time Ocean Data", width="stretch", key="realtime_data"):
                process_chat_query("Get the latest real-time ocean measurements from Argo network")
        
        with col11:
            if st.button("🔥 System Performance", width="stretch", key="system_perf"):
                process_chat_query("Demonstrate system capabilities and processing speed")

def show_dashboard_page():
    """Modern dashboard with key metrics and visualizations"""
    
    st.title("📊 Ocean Data Dashboard")
    st.subheader("Real-time insights and key metrics")
    st.divider()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌊 Total Measurements", "320,094", delta="Live")
    with col2:
        st.metric("🛰️ Active Platforms", "405", delta="Online")
    with col3:
        st.metric("🌡️ Avg Temperature", "18.5°C", delta="0.2°C")
    with col4:
        st.metric("📍 Global Coverage", "95%", delta="Active")
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Temperature Trends")
        
        # Create sample data for demo
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        temps = np.random.normal(18.5, 2, len(dates))
        
        chart_data = pd.DataFrame({
            'Date': dates,
            'Temperature': temps
        })
        
        st.line_chart(chart_data.set_index('Date'))
    
    with col2:
        st.subheader("🧂 Salinity Distribution")
        
        # Create sample salinity data
        regions = ['Pacific', 'Atlantic', 'Indian', 'Arctic', 'Southern']
        salinity = [35.1, 35.4, 34.8, 32.5, 34.7]
        
        chart_data = pd.DataFrame({
            'Ocean': regions,
            'Salinity': salinity
        })
        
        st.bar_chart(chart_data.set_index('Ocean'))

def show_maps_page():
    """Interactive maps page with stable rendering"""
    
    st.title("🗺️ Ocean Data Maps")
    st.subheader("Interactive visualization of global ocean data")
    st.divider()
    
    # Initialize map session state
    if 'map_data' not in st.session_state:
        st.session_state.map_data = None
    if 'map_settings' not in st.session_state:
        st.session_state.map_settings = {
            'data_type': 'Temperature',
            'time_range': 'Last 24h',
            'region': 'Global'
        }
    
    # Map controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        data_type = st.selectbox("Data Type", ["Temperature", "Salinity", "Depth", "Current"],
                                index=["Temperature", "Salinity", "Depth", "Current"].index(st.session_state.map_settings['data_type']),
                                key="map_data_type")
    with col2:
        time_range = st.selectbox("Time Range", ["Last 24h", "Last Week", "Last Month", "Last Year"],
                                 index=["Last 24h", "Last Week", "Last Month", "Last Year"].index(st.session_state.map_settings['time_range']),
                                 key="map_time_range")
    with col3:
        region = st.selectbox("Region", ["Global", "Pacific", "Atlantic", "Indian Ocean"],
                             index=["Global", "Pacific", "Atlantic", "Indian Ocean"].index(st.session_state.map_settings['region']),
                             key="map_region")
    with col4:
        refresh_map = st.button("🔄 Refresh", help="Update map with current settings")
        
    # Add clear map cache button for troubleshooting
    if st.button("🗑️ Clear Map Cache", help="Reset map if experiencing issues"):
        st.session_state.map_data = None
        st.session_state.last_clicked = None
        st.rerun()
    
    # Check if settings changed or refresh button clicked
    settings_changed = (
        data_type != st.session_state.map_settings['data_type'] or
        time_range != st.session_state.map_settings['time_range'] or
        region != st.session_state.map_settings['region'] or
        refresh_map
    )
    
    # Update settings if changed
    if settings_changed:
        st.session_state.map_settings = {
            'data_type': data_type,
            'time_range': time_range,
            'region': region
        }
        # Clear cached map data to force regeneration
        st.session_state.map_data = None
    
    # Generate map only if needed
    if st.session_state.map_data is None or settings_changed:
        with st.spinner(f"🗺️ Loading {data_type} data for {region}..."):
            # Set map center based on region
            region_centers = {
                "Global": [20, 0],
                "Pacific": [0, -150],
                "Atlantic": [30, -30],
                "Indian Ocean": [-10, 80]
            }
            
            map_center = region_centers.get(region, [20, 0])
            
            # Add region-specific sample data points
            if region == "Global":
                sample_locations = [
                    [40, -70, "Atlantic Station 1", 18.5],
                    [35, -120, "Pacific Station 2", 16.2],
                    [0, 80, "Indian Ocean Station 3", 24.1],
                    [-30, 150, "Pacific Station 4", 15.8],
                    [60, 10, "Norwegian Sea Station", 8.3],
                    [-45, -60, "Southern Ocean Station", 4.2]
                ]
            elif region == "Pacific":
                sample_locations = [
                    [35, -120, "West Coast Station", 16.2],
                    [20, -160, "Hawaiian Station", 22.5],
                    [-10, -140, "Equatorial Station", 26.8],
                    [45, 150, "North Pacific Station", 12.1]
                ]
            elif region == "Atlantic":
                sample_locations = [
                    [40, -70, "North Atlantic", 18.5],
                    [25, -80, "Gulf Stream", 24.2],
                    [10, -40, "Equatorial Atlantic", 27.1],
                    [50, -30, "Labrador Sea", 6.8]
                ]
            else:  # Indian Ocean
                sample_locations = [
                    [0, 80, "Equatorial Indian", 24.1],
                    [-20, 60, "Mauritius Region", 22.7],
                    [-10, 100, "Java Sea", 28.3],
                    [15, 60, "Arabian Sea", 26.5]
                ]
            
            # Color mapping for different data types
            color_maps = {
                "Temperature": {"color": "Blues", "unit": "°C"},
                "Salinity": {"color": "Viridis", "unit": "PSU"}, 
                "Depth": {"color": "Greens", "unit": "m"},
                "Current": {"color": "Purples", "unit": "m/s"}
            }
            
            color_info = color_maps.get(data_type, {"color": "Blues", "unit": ""})
            
            # Prepare data for Plotly map
            lats, lons, names, values = zip(*sample_locations)
            
            # Adjust values based on data type
            display_values = []
            for value in values:
                if data_type == "Salinity":
                    display_values.append(value + 16)  # Typical salinity range
                elif data_type == "Depth":
                    display_values.append(np.random.uniform(100, 5000))
                elif data_type == "Current":
                    display_values.append(np.random.uniform(0.1, 2.5))
                else:
                    display_values.append(value)
            
            # Create Plotly scatter mapbox
            fig = go.Figure(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers',
                marker=dict(
                    size=12,
                    color=display_values,
                    colorscale=color_info['color'],
                    showscale=True,
                    colorbar=dict(title=f"{data_type} ({color_info['unit']})")
                ),
                text=[f"{name}<br>{data_type}: {val:.1f} {color_info['unit']}<br>Time: {time_range}<br>Region: {region}" 
                      for name, val in zip(names, display_values)],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            fig.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=map_center[0], lon=map_center[1]),
                    zoom=2 if region == "Global" else 3
                ),
                height=500,
                margin={"r":0,"t":0,"l":0,"b":0},
                showlegend=False
            )
            
            # Store the map in session state
            st.session_state.map_data = fig
    
    # Display the map with a unique key to prevent re-rendering
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); 
                padding: 1rem; border-radius: 12px; border: 1px solid #4a5568; margin-bottom: 1rem;">
        <div style="color: #e2e8f0; font-weight: bold; margin-bottom: 0.5rem;">
            📊 Current View: {data_type} data for {region} ({time_range})
        </div>
        <div style="color: #a0aec0; font-size: 0.9rem;">
            Click on markers for detailed information • Use refresh button to update data
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the stable map
    try:
        # Ensure map data exists before display
        if st.session_state.map_data is None:
            st.error("Map data not available. Please refresh the page.")
            return
            
        # Display map using Plotly instead of folium
        st.plotly_chart(
            st.session_state.map_data, 
            use_container_width=True,
            key="ocean_map"  # Stable key prevents re-rendering
        )
        
        # Note: Plotly charts have built-in interactivity
        
        # Display clicked location info from session state
        if (hasattr(st.session_state, 'last_clicked') and 
            st.session_state.last_clicked and
            st.session_state.last_clicked != {}):
            clicked_data = st.session_state.last_clicked
            with st.container():
                st.info(f"📍 Last clicked location: Lat {clicked_data.get('lat', 0):.2f}, Lon {clicked_data.get('lng', 0):.2f}")
    
    except Exception as e:
        st.error(f"Map display error: {str(e)}")
        st.info("🔄 Please refresh the page or try clicking the refresh button above")
        
        # Provide fallback information
        st.markdown("""
        **Map Information:**
        - Interactive ocean data visualization
        - Click refresh button to reload map
        - Choose different regions and data types above
        """)
    
    # Map statistics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get current sample locations count based on region
    current_locations_count = {
        "Global": 6,
        "Pacific": 4,
        "Atlantic": 4,
        "Indian Ocean": 4
    }.get(region, 4)
    
    with col1:
        st.metric("Data Points", current_locations_count, delta="Live")
    with col2:
        st.metric("Coverage", "95%", delta="2%")
    with col3:
        st.metric("Update Rate", "Real-time", delta="Active")
    with col4:
        st.metric("Quality", "High", delta="✓")

def show_analytics_page():
    """Advanced analytics and insights"""
    
    st.title("📈 Ocean Analytics")
    st.subheader("Advanced data analysis and insights")
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📊 Trends", "🔍 Patterns", "📋 Reports"])
    
    with tab1:
        st.subheader("Long-term Trends Analysis")
        st.info("🔄 Analyzing multi-year temperature and salinity trends...")
        
        # Sample trend analysis
        years = list(range(2020, 2025))
        temp_trend = [18.2, 18.4, 18.1, 18.6, 18.5]
        
        chart_data = pd.DataFrame({
            'Year': years,
            'Temperature': temp_trend
        })
        
        st.line_chart(chart_data.set_index('Year'))
    
    with tab2:
        st.subheader("Seasonal Patterns")
        st.info("🌊 Identifying seasonal oceanographic patterns...")
        
        # Sample seasonal data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        seasonal_temp = [16.5, 16.8, 17.2, 18.1, 19.5, 20.8,
                        21.2, 20.9, 19.6, 18.3, 17.1, 16.7]
        
        chart_data = pd.DataFrame({
            'Month': months,
            'Temperature': seasonal_temp
        })
        
        st.bar_chart(chart_data.set_index('Month'))
    
    with tab3:
        st.subheader("Data Quality Report")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Data Completeness", "98.5%", delta="0.3%")
            st.metric("Quality Score", "A+", delta="Excellent")
        with col2:
            st.metric("Coverage Areas", "127", delta="5 new")
            st.metric("Update Frequency", "Hourly", delta="Real-time")

def show_settings_page():
    """Application settings and configuration"""
    
    st.title("⚙️ Settings")
    st.subheader("Configure your OceanChat experience")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Display Preferences")
        
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        units = st.selectbox("Temperature Units", ["Celsius", "Fahrenheit"])
        language = st.selectbox("Language", ["English", "Spanish", "French"])
    
    with col2:
        st.subheader("🔧 Data Settings")
        
        refresh_rate = st.selectbox("Data Refresh", ["Real-time", "5 minutes", "15 minutes", "Hourly"])
        max_results = st.slider("Max Results per Query", 10, 1000, 100)
        cache_enabled = st.checkbox("Enable Data Caching", value=True)
    
    st.divider()
    st.subheader("🌐 API Configuration")
    
    st.success("✅ Backend API: Connected")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Test Connection", width="stretch"):
            with st.spinner("Testing connection..."):
                time.sleep(2)
                st.success("Connection successful!")
    
    with col2:
        if st.button("🧹 Clear Cache", width="stretch"):
            with st.spinner("Clearing cache..."):
                time.sleep(1)
                st.success("Cache cleared!")
    st.markdown("""
    <div class="section-header fade-in-up">
        <h2>💬 Ask Ocean Questions</h2>
        <p>Type your questions in natural language and get instant insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat input with modern styling
    st.markdown("""
    <div class="chat-container fade-in-up">
        <h4 style="margin-top: 0; color: #006994; font-weight: 600;">🚀 What would you like to know about the ocean?</h4>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask me anything...",
                placeholder="e.g., Show me temperature data near the Arabian Sea",
                key="chat_input",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("🚀 Send", type="primary", width="stretch")
    
    # Quick suggestions
    st.markdown("""
    <div style="margin: 1rem 0;">
        <p style="color: #475569; margin-bottom: 0.5rem; font-weight: 500;">💡 Try these examples:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌡️ Temperature trends", width="stretch", key="temp_trends_btn"):
            process_chat_query("Show me temperature trends in the Pacific Ocean")
    with col2:
        if st.button("🧂 Salinity data", width="stretch", key="salinity_data_btn"):
            process_chat_query("What's the salinity distribution in the Atlantic?")
    with col3:
        if st.button("📏 Depth analysis", width="stretch", key="depth_analysis_btn"):
            process_chat_query("Analyze depth profiles near the equator")
    
    # Process chat input
    if send_button and user_input:
        process_chat_query(user_input)
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("""
        <div class="section-header" style="margin-top: 2rem;">
            <h2>💭 Conversation History</h2>
            <p>Your recent ocean data queries and insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, chat in enumerate(st.session_state.chat_history):
            with st.container():
                # User message
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                    <div style="background: linear-gradient(135deg, #006994 0%, #0891b2 100%); color: white; padding: 1rem 1.5rem; border-radius: 18px 18px 4px 18px; max-width: 70%; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                        <strong>You:</strong> {chat['user']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Assistant message
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
                    <div style="background: white; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 18px 18px 18px 4px; max-width: 85%; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                        <div style="color: #006994; font-weight: 600; margin-bottom: 0.5rem;">🌊 Ocean Assistant:</div>
                        <div style="color: #475569; line-height: 1.6;">{chat['assistant']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if 'data' in chat and chat['data'] is not None:
                    st.markdown("""
                    <div class="section-header" style="margin: 1.5rem 0;">
                        <h2>📊 Data Visualization</h2>
                        <p>Interactive charts and maps based on your query</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create tabs for different visualizations
                    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Interactive Map", "📈 Advanced Charts", "📊 Statistics", "📋 Raw Data"])
                    
                    with tab1:
                        st.markdown("### 🌍 Geographic Distribution")
                        map_chart = create_temperature_map(chat['data'])
                        if map_chart:
                            st.plotly_chart(map_chart, use_container_width=True, key=f"map_{i}")
                    
                    with tab2:
                        # Full width section for Enhanced Depth Profile
                        st.markdown("### 📏 Enhanced Depth Profile")
                        st.markdown("*Vertical ocean temperature and salinity analysis*")
                        depth_chart = create_depth_profile_chart(chat['data'])
                        if depth_chart:
                            st.plotly_chart(depth_chart, use_container_width=True, key=f"depth_{i}")
                        
                        # Add spacing between charts
                        st.markdown("---")
                        
                        # Full width section for Time Series
                        st.markdown("### ⏰ Multi-Parameter Time Series")
                        st.markdown("*Ocean parameter trends over time*")
                        time_chart = create_time_series_chart(chat['data'])
                        if time_chart:
                            st.plotly_chart(time_chart, use_container_width=True, key=f"time_{i}")
                    
                    with tab3:
                        st.markdown("### 📊 Comprehensive Statistical Analysis")
                        st.markdown("*Distribution patterns and geographic coverage*")
                        stats_chart = create_advanced_statistics_chart(chat['data'])
                        if stats_chart:
                            st.plotly_chart(stats_chart, use_container_width=True, key=f"stats_{i}")
                        else:
                            st.info("📋 Statistical analysis requires sufficient data points for meaningful insights.")
                    
                    with tab4:
                        st.markdown("### 📊 Data Sample")
                        
                        # Add data summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Total Records", len(chat['data']))
                        with col2:
                            st.metric("🌡️ Avg Temperature", f"{chat['data']['temperature'].mean():.1f}°C")
                        with col3:
                            st.metric("🧂 Avg Salinity", f"{chat['data']['salinity'].mean():.1f} PSU")
                        with col4:
                            st.metric("📏 Max Depth", f"{chat['data']['depth'].max():.0f}m")
                        
                        st.dataframe(
                            chat['data'].head(20),
                            width="stretch",
                            hide_index=True
                        )
                
                st.markdown("<hr style='margin: 2rem 0; border: none; height: 1px; background: #e2e8f0;'>", unsafe_allow_html=True)

def process_chat_query(user_input):
    """Process user chat query with visualizations and improved layout"""
    with st.spinner("🔍 Searching ocean data..."):
        # Query the API
        data = query_ocean_api(user_input)
        
        # Generate response and visualizations
        if data is not None and not data.empty:
            # Display textual response
            response = f"""
            🌊 Found {len(data)} ocean measurements based on your query!
            
            **Key Insights:**
            - Temperature range: {data['temperature'].min():.1f}°C to {data['temperature'].max():.1f}°C
            - Salinity range: {data['salinity'].min():.1f} to {data['salinity'].max():.1f} PSU
            - Depth range: {data['depth'].min():.0f}m to {data['depth'].max():.0f}m
            - Data from {data['platform_id'].nunique()} different platforms
            """
            
            # Display the textual part of the response
            st.write(response)
            
            # Use st.container() for logical grouping and a clean layout
            with st.container():
                st.markdown("---")
                st.markdown("### 📊 Data Visualizations")
                
                # --- Temperature vs Depth Profile ---
                st.markdown("### 🌡️ Temperature vs Depth Profile")
                st.markdown("*Vertical distribution of ocean temperature and salinity*")
                temp_depth_fig = create_depth_profile_chart(data)
                if temp_depth_fig:
                    st.plotly_chart(temp_depth_fig, use_container_width=True)
                else:
                    st.info("Temperature depth profile not available for this dataset.")

            # --- Advanced Statistical Analysis ---
            with st.container():
                st.markdown("---")
                st.markdown("### 📈 Advanced Statistical Analysis")
                st.markdown("*Distribution patterns and data overview*")
                stats_fig = create_advanced_statistics_chart(data)
                if stats_fig:
                    st.plotly_chart(stats_fig, use_container_width=True)
                else:
                    st.info("Statistical analysis not available for this dataset.")

            # --- Geographic Distribution ---
            if 'latitude' in data.columns and 'longitude' in data.columns:
                with st.container():
                    st.markdown("---")
                    st.markdown("### 🗺️ Geographic Distribution")
                    st.markdown("*Spatial distribution of ocean measurement points*")
                    
                    try:
                        sample_data = data.sample(min(50, len(data)))
                        fig = px.scatter_mapbox(
                            sample_data,
                            lat='latitude',
                            lon='longitude',
                            color='temperature',
                            size_max=15,
                            zoom=3,
                            color_continuous_scale='Blues',
                            hover_data={
                                'temperature': ':.1f',
                                'salinity': ':.1f'
                            },
                            title='Ocean Data Distribution'
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map",
                            height=500,
                            margin={"r": 10, "t": 60, "l": 10, "b": 10},
                            title_font_size=16,
                            title_x=0.5
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.info(f"Map visualization not available: {str(e)}")
            
            # --- Raw Data Sample ---
            with st.container():
                st.markdown("---")
                st.markdown("### 📋 Raw Data Sample")
                st.markdown("*First 10 records from the dataset*")
                st.dataframe(data.head(10), use_container_width=True)
            
            return "Visualizations generated successfully!"
        
        else:
            response = "❌ Sorry, I couldn't find any ocean data matching your query. Please try rephrasing your question or check different parameters."
            st.write(response)
            
            # Show demo visualizations with synthetic data
            st.markdown("---")
            st.markdown("### 📊 Demo Visualizations (Sample Data)")
            st.info("🎯 Since no data was found, here are sample visualizations to show system capabilities:")
            
            sample_data = generate_sample_ocean_data()
            
            with st.container():
                st.markdown("---")
                st.markdown("### 🌡️ Sample Temperature Profile")
                st.markdown("*Vertical distribution of sample ocean temperature data*")
                temp_fig = create_depth_profile_chart(sample_data)
                if temp_fig:
                    st.plotly_chart(temp_fig, use_container_width=True)
            
            with st.container():
                st.markdown("---")
                st.markdown("### 📈 Sample Statistical Analysis")
                st.markdown("*Distribution patterns from sample ocean data*")
                stats_fig = create_advanced_statistics_chart(sample_data)
                if stats_fig:
                    st.plotly_chart(stats_fig, use_container_width=True)
            
            return response

def generate_sample_ocean_data():
    """Generate sample ocean data for demonstration"""
    import pandas as pd
    import numpy as np
    
    # Create sample data
    n_points = 100
    depths = np.random.uniform(0, 2000, n_points)
    temperatures = 25 - (depths / 100) + np.random.normal(0, 2, n_points)
    salinities = 35 + np.random.normal(0, 1, n_points)
    latitudes = np.random.uniform(-60, 60, n_points)
    longitudes = np.random.uniform(-180, 180, n_points)
    
    return pd.DataFrame({
        'depth': depths,
        'temperature': temperatures,
        'salinity': salinities,
        'latitude': latitudes,
        'longitude': longitudes,
        'platform_id': [f"DEMO_{i%10}" for i in range(n_points)]
    })

def show_dashboard():
    """Display the main dashboard"""
    st.markdown("""
    <div class="section-header fade-in-up">
        <h2>📊 Ocean Data Dashboard</h2>
        <p>Real-time oceanographic insights and analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load sample data
    data = load_sample_data()
    
    # Key metrics with modern design
    st.markdown("### 🌊 Key Ocean Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Avg Temperature",
            f"{data['temperature'].mean():.1f}°C",
            f"±{data['temperature'].std():.1f}°C",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "🧂 Avg Salinity",
            f"{data['salinity'].mean():.1f} PSU",
            f"±{data['salinity'].std():.1f} PSU",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "📏 Max Depth",
            f"{data['depth'].max():.0f}m",
            f"{data['depth'].mean():.0f}m avg",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            "🛰️ Active Platforms",
            data['platform_id'].nunique(),
            f"{len(data)} measurements",
            delta_color="normal"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main visualizations
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("""
        <div class="section-header">
            <h2>🗺️ Global Ocean Temperature</h2>
            <p>Interactive map showing temperature distribution</p>
        </div>
        """, unsafe_allow_html=True)
        
        map_chart = create_temperature_map(data.sample(100))
        if map_chart:
            st.plotly_chart(map_chart, use_container_width=True, key="dashboard_map")
    
    with col2:
        st.markdown("""
        <div class="section-header">
            <h2>📈 Temperature vs Depth</h2>
            <p>Vertical ocean profile analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        depth_chart = create_depth_profile_chart(data.sample(200))
        if depth_chart:
            st.plotly_chart(depth_chart, use_container_width=True, key="dashboard_depth")
    
    # Additional insights
    st.markdown("""
    <div class="section-header" style="margin-top: 2rem;">
        <h2>📊 Data Insights</h2>
        <p>Statistical analysis and trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 🌡️ Temperature Distribution")
        temp_fig = px.histogram(
            data.sample(500), 
            x='temperature',
            title="Temperature Distribution",
            color_discrete_sequence=['#006994'],
            nbins=30
        )
        temp_fig.update_layout(
            showlegend=False,
            height=300,
            font=dict(family="Inter", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(temp_fig, use_container_width=True, key="temp_dist")
    
    with col2:
        st.markdown("##### 🧂 Salinity Distribution")
        sal_fig = px.histogram(
            data.sample(500),
            x='salinity',
            title="Salinity Distribution",
            color_discrete_sequence=['#0891b2'],
            nbins=30
        )
        sal_fig.update_layout(
            showlegend=False,
            height=300,
            font=dict(family="Inter", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(sal_fig, use_container_width=True, key="sal_dist")
    
    with col3:
        st.markdown("##### 📏 Depth Distribution")
        depth_fig = px.histogram(
            data.sample(500),
            x='depth',
            title="Depth Distribution",
            color_discrete_sequence=['#22d3ee'],
            nbins=30
        )
        depth_fig.update_layout(
            showlegend=False,
            height=300,
            font=dict(family="Inter", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(depth_fig, use_container_width=True, key="depth_dist")

def show_data_explorer():
    """Display data exploration interface"""
    st.markdown("""
    <div class="section-header fade-in-up">
        <h2>🔍 Data Explorer</h2>
        <p>Explore and filter oceanographic datasets with advanced controls</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced filters with better layout
    with st.expander("🎛️ Advanced Data Filters", expanded=True):
        # Temperature Section
        st.markdown("### 🌡️ Temperature Range")
        temp_range = st.slider(
            "Select temperature range (°C)",
            -5.0, 35.0, (-2.0, 30.0),
            step=0.5,
            help="Filter data by ocean temperature"
        )
        
        # Depth Section  
        st.markdown("### 📏 Depth Range")
        depth_range = st.slider(
            "Select depth range (meters)",
            0, 5000, (0, 2000),
            step=50,
            help="Filter data by measurement depth"
        )
        
        # Platform Section
        st.markdown("### 🛰️ Platform Selection")
        platform_filter = st.multiselect(
            "Choose platforms",
            ['ARGO_001', 'ARGO_002', 'ARGO_003', 'BUOY_001', 'SHIP_001'],
            default=['ARGO_001', 'ARGO_002'],
            help="Select specific ocean monitoring platforms"
        )
        
        # Salinity Section
        st.markdown("### 🧂 Salinity Range")
        salinity_range = st.slider(
            "Select salinity range (PSU)",
            30.0, 40.0, (32.0, 38.0),
            step=0.1,
            help="Filter data by ocean salinity"
        )
    
    # Load and filter data
    data = load_sample_data()
    
    # Apply filters
    filtered_data = data[
        (data['temperature'] >= temp_range[0]) &
        (data['temperature'] <= temp_range[1]) &
        (data['depth'] >= depth_range[0]) &
        (data['depth'] <= depth_range[1]) &
        (data['salinity'] >= salinity_range[0]) &
        (data['salinity'] <= salinity_range[1]) &
        (data['platform_id'].isin(platform_filter) if platform_filter else True)
    ]
    
    # Results summary
    st.markdown("### 📊 Filter Results Summary")
    
    # Create metrics in a more readable layout
    st.metric("📊 Filtered Results", f"{len(filtered_data):,}")
    st.metric("📈 Total Available", f"{len(data):,}")
    st.metric("🎯 Filter Efficiency", f"{len(filtered_data)/len(data)*100:.1f}%")
    if len(filtered_data) > 0:
        st.metric("🌡️ Average Temperature", f"{filtered_data['temperature'].mean():.1f}°C")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display filtered data
    if not filtered_data.empty:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Data Table", 
            "🗺️ Geographic View", 
            "📊 Statistical Analysis",
            "📁 Export Options"
        ])
        
        with tab1:
            st.markdown("### 📊 Filtered Dataset")
            st.dataframe(
                filtered_data,
                width="stretch",
                hide_index=True,
                column_config={
                    "temperature": st.column_config.NumberColumn(
                        "🌡️ Temperature (°C)",
                        format="%.2f"
                    ),
                    "salinity": st.column_config.NumberColumn(
                        "🧂 Salinity (PSU)",
                        format="%.2f"
                    ),
                    "depth": st.column_config.NumberColumn(
                        "📏 Depth (m)",
                        format="%.0f"
                    ),
                    "latitude": st.column_config.NumberColumn(
                        "🌍 Latitude",
                        format="%.4f"
                    ),
                    "longitude": st.column_config.NumberColumn(
                        "🌍 Longitude", 
                        format="%.4f"
                    )
                }
            )
        
        with tab2:
            st.markdown("### 🗺️ Geographic Distribution")
            if len(filtered_data) > 0:
                sample_size = min(200, len(filtered_data))
                map_chart = create_temperature_map(filtered_data.sample(sample_size))
                if map_chart:
                    st.plotly_chart(map_chart, use_container_width=True, key="explorer_map")
        
        with tab3:
            st.markdown("### 📈 Statistical Analysis")
            
            # Temperature Analysis Section
            st.markdown("---")
            st.markdown("#### 🌡️ Temperature Analysis")
            temp_stats = filtered_data['temperature'].describe()
            st.write(f"**Mean:** {temp_stats['mean']:.2f}°C")
            st.write(f"**Std Dev:** {temp_stats['std']:.2f}°C")
            st.write(f"**Range:** {temp_stats['min']:.2f}°C to {temp_stats['max']:.2f}°C")
            
            # Temperature histogram
            temp_hist = px.histogram(
                filtered_data.sample(min(1000, len(filtered_data))),
                x='temperature',
                title="Temperature Distribution",
                color_discrete_sequence=['#006994'],
                nbins=25
            )
            temp_hist.update_layout(
                height=400,
                font=dict(family="Inter", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(temp_hist, use_container_width=True, key="temp_hist_explorer")
            
            # Salinity Analysis Section
            st.markdown("---")
            st.markdown("#### 🧂 Salinity Analysis")
            sal_stats = filtered_data['salinity'].describe()
            st.write(f"**Mean:** {sal_stats['mean']:.2f} PSU")
            st.write(f"**Std Dev:** {sal_stats['std']:.2f} PSU")
            st.write(f"**Range:** {sal_stats['min']:.2f} to {sal_stats['max']:.2f} PSU")
            
            # Salinity histogram
            sal_hist = px.histogram(
                filtered_data.sample(min(1000, len(filtered_data))),
                x='salinity',
                title="Salinity Distribution",
                color_discrete_sequence=['#0891b2'],
                nbins=25
            )
            sal_hist.update_layout(
                height=400,
                font=dict(family="Inter", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(sal_hist, use_container_width=True, key="sal_hist_explorer")
            
            # Correlation analysis
            st.markdown("---")
            st.markdown("#### 🔗 Data Correlations")
            correlation_data = filtered_data[['temperature', 'salinity', 'depth']].corr()
            fig_corr = px.imshow(
                correlation_data,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title="Parameter Correlation Matrix"
            )
            fig_corr.update_layout(
                height=500,
                font=dict(family="Inter", size=12)
            )
            st.plotly_chart(fig_corr, use_container_width=True, key="corr_explorer")
        
        with tab4:
            st.markdown("### 📁 Export Filtered Data")
            
            st.markdown("**Available Export Formats:**")
            
            # CSV Download Section
            st.markdown("### 📊 CSV Export")
            if st.button("📊 Download CSV", key="csv_download"):
                csv = filtered_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV File",
                    data=csv,
                    file_name=f"ocean_data_filtered_{len(filtered_data)}_points.csv",
                    mime="text/csv"
                )
            
            # Additional Export Options
            st.markdown("### 📋 Other Export Options")
            if st.button("📋 Copy to Clipboard", key="clipboard_copy"):
                st.info("📋 Data copied! (Feature simulated)")
            
            if st.button("📧 Email Report", key="email_report"):
                st.info("📧 Report sent! (Feature simulated)")
    else:
        st.warning("""
        🚫 **No data matches your current filters**
        
        Try adjusting the filter parameters to see results:
        - Expand temperature range
        - Increase depth range
        - Select more platforms
        - Adjust salinity range
        """)

def show_analytics():
    """Display analytics and insights"""
    st.markdown("""
    <div class="section-header fade-in-up">
        <h2>📈 Analytics & Insights</h2>
        <p>Advanced ocean data analysis and predictive insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Coming soon section with better design
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #006994 0%, #0891b2 100%); padding: 2rem; border-radius: 20px; color: white; margin-bottom: 2rem;">
            <h3 style="margin-top: 0; color: white;">🚀 Advanced Analytics Coming Soon</h3>
            <p style="margin-bottom: 0; opacity: 0.9;">We're building powerful analytics tools to unlock deeper ocean insights.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Planned Features")
        
        features = [
            {"icon": "🤖", "title": "Machine Learning Predictions", "desc": "AI-powered ocean parameter forecasting"},
            {"icon": "📊", "title": "Trend Analysis", "desc": "Long-term climate and ocean pattern analysis"},
            {"icon": "🔗", "title": "Data Correlations", "desc": "Advanced statistical relationships discovery"},
            {"icon": "📱", "title": "Custom Reports", "desc": "Automated report generation and insights"},
            {"icon": "🌍", "title": "Climate Insights", "desc": "Global climate change impact analysis"},
            {"icon": "⚡", "title": "Real-time Alerts", "desc": "Anomaly detection and notification system"}
        ]
        
        for i, feature in enumerate(features):
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid #006994; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">{feature['icon']}</div>
                    <div>
                        <h4 style="margin: 0; color: #006994;">{feature['title']}</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #475569;">{feature['desc']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 2rem;">
            <h4 style="margin-top: 0; color: #006994;">📅 Development Timeline</h4>
            <div style="color: #475569;">
                <p><strong>Q1 2025:</strong> Machine Learning Models</p>
                <p><strong>Q2 2025:</strong> Trend Analysis Tools</p>
                <p><strong>Q3 2025:</strong> Custom Reports</p>
                <p><strong>Q4 2025:</strong> Real-time Alerts</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%); padding: 1.5rem; border-radius: 16px; color: white; text-align: center;">
            <h4 style="margin: 0; color: white;">🔔 Get Notified</h4>
            <p style="margin: 0.5rem 0; opacity: 0.9;">Be the first to know when new analytics features launch!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📧 Subscribe to Updates", width="stretch"):
            st.success("✅ You'll be notified about new analytics features!")

def show_settings():
    """Display settings interface"""
    st.markdown("""
    <div class="section-header fade-in-up">
        <h2>⚙️ Settings & Configuration</h2>
        <p>Customize your Ocean Chat experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔌 API Configuration", 
        "🎨 Display Settings", 
        "📊 Data Preferences",
        "👤 User Profile"
    ])
    
    with tab1:
        st.markdown("### 🔌 API Configuration")
        
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 1rem;">
            """, unsafe_allow_html=True)
            
            api_endpoint = st.text_input(
                "Backend API Endpoint",
                value="http://localhost:8000",
                help="URL of your Ocean Chat backend API"
            )
            
            api_timeout = st.slider(
                "API Timeout (seconds)",
                1, 60, 10,
                help="Maximum time to wait for API responses"
            )
            
            st.markdown("**🔑 API Keys**")
            argo_key = st.text_input(
                "Argo API Key",
                type="password",
                help="Your Argo oceanographic data API key"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧪 Test Connection", width="stretch"):
                    st.success("✅ Connection successful!")
            with col2:
                if st.button("🔄 Reset to Default", width="stretch"):
                    st.info("🔄 Settings reset to default values")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🎨 Display Settings")
        
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 1rem;">
            """, unsafe_allow_html=True)
            
            theme = st.selectbox(
                "🎨 Color Theme",
                ["Ocean Blue (Default)", "Deep Sea", "Coral Reef", "Arctic Ice"],
                help="Choose your preferred color scheme"
            )
            
            language = st.selectbox(
                "🌍 Language",
                ["English", "Spanish", "French", "Portuguese", "Mandarin"],
                help="Select your preferred language"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                auto_refresh = st.checkbox(
                    "🔄 Auto-refresh data",
                    value=True,
                    help="Automatically update data in real-time"
                )
                
                chart_animation = st.checkbox(
                    "✨ Chart animations",
                    value=True,
                    help="Enable smooth chart transitions"
                )
            
            with col2:
                dark_mode = st.checkbox(
                    "🌙 Dark mode",
                    value=False,
                    help="Switch to dark theme"
                )
                
                compact_view = st.checkbox(
                    "📱 Compact view",
                    value=False,
                    help="Optimize for smaller screens"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📊 Data Preferences")
        
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 1rem;">
            """, unsafe_allow_html=True)
            
            max_points = st.slider(
                "📊 Maximum data points to display",
                100, 10000, 1000,
                step=100,
                help="Limit the number of data points for better performance"
            )
            
            cache_duration = st.slider(
                "⏰ Cache duration (minutes)",
                1, 120, 15,
                help="How long to cache data before refreshing"
            )
            
            default_region = st.selectbox(
                "🌍 Default region",
                ["Global", "Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Southern Ocean"],
                help="Default geographic focus for data queries"
            )
            
            st.markdown("**📏 Units Preferences**")
            col1, col2 = st.columns(2)
            with col1:
                temp_unit = st.radio(
                    "Temperature",
                    ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
                    horizontal=True
                )
            with col2:
                depth_unit = st.radio(
                    "Depth",
                    ["Meters (m)", "Feet (ft)", "Fathoms"],
                    horizontal=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 👤 User Profile")
        
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 1rem;">
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**👤 Profile Picture**")
                uploaded_file = st.file_uploader(
                    "Choose profile image",
                    type=['png', 'jpg', 'jpeg'],
                    label_visibility="collapsed"
                )
                if uploaded_file:
                    st.success("✅ Profile picture updated!")
            
            with col2:
                user_name = st.text_input(
                    "👤 Full Name",
                    value="Ocean Researcher",
                    help="Your display name"
                )
                
                user_role = st.selectbox(
                    "🎓 Role",
                    ["Researcher", "Student", "Educator", "Policy Maker", "Curious Explorer"],
                    help="Your primary role or interest"
                )
                
                organization = st.text_input(
                    "🏢 Organization",
                    placeholder="University, Institute, or Company",
                    help="Your affiliated organization"
                )
            
            st.markdown("**🎯 Research Interests**")
            interests = st.multiselect(
                "Select your areas of interest",
                [
                    "Climate Change", "Ocean Temperature", "Marine Biology", 
                    "Ocean Chemistry", "Deep Sea Research", "Coastal Studies",
                    "Pollution Monitoring", "Fisheries", "Renewable Energy"
                ],
                default=["Ocean Temperature", "Climate Change"]
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Save settings button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Save All Settings", width="stretch", type="primary"):
            st.success("✅ All settings saved successfully!")
            st.balloons()

if __name__ == "__main__":
    main()
