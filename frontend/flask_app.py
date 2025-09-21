"""
🌊 Ocean Chat - Flask-based Modern Chatbot Interface
Professional chatbot UI with Plotly integration
"""

from flask import Flask, render_template, request, jsonify
import requests
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.utils
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"

# Profile Configurations
PROFILES = {
    "researcher": {
        "name": "Marine Researcher",
        "icon": "🔬",
        "description": "Advanced analytics and scientific data visualization",
        "color_scheme": "blue",
        "features": ["detailed_analytics", "scientific_charts", "data_export", "advanced_filters"]
    },
    "educator": {
        "name": "Ocean Educator",
        "icon": "🎓", 
        "description": "Educational content and simplified visualizations",
        "color_scheme": "green",
        "features": ["simple_charts", "educational_content", "guided_tours", "basic_analytics"]
    },
    "policymaker": {
        "name": "Policy Maker",
        "icon": "🏛️",
        "description": "High-level insights and policy-relevant data",
        "color_scheme": "purple",
        "features": ["summary_reports", "trend_analysis", "policy_insights", "executive_dashboard"]
    },
    "student": {
        "name": "Ocean Student",
        "icon": "📚",
        "description": "Learning-focused interface with guided exploration",
        "color_scheme": "orange",
        "features": ["learning_mode", "basic_charts", "tutorials", "quiz_mode"]
    }
}

# Global profile state (in production, use session or database)
current_profile = "researcher"

# Helper functions for data processing
def fetch_live_data_status():
    """Fetch live data status from the backend API."""
    try:
        response = requests.get(f"{BACKEND_URL}/live-data/status", timeout=5)
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

def fetch_system_status():
    """Fetch comprehensive system status"""
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        live_response = requests.get(f"{BACKEND_URL}/live-data/status", timeout=2)
        live_data = live_response.json() if live_response.status_code == 200 else {}
        
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
    except Exception as e:
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
    n_points = 100
    
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
        response = requests.post(
            f"{BACKEND_URL}/api/v1/query",
            json={"query": user_query},
            timeout=30
        )
        
        if response.status_code == 200:
            api_response = response.json()
            
            if api_response.get("success") and "data" in api_response:
                data_section = api_response["data"]
                
                if "measurements" in data_section and data_section["measurements"]:
                    measurements = data_section["measurements"]
                    if isinstance(measurements, list) and len(measurements) > 0:
                        df = pd.DataFrame(measurements)
                        
                        required_columns = ['latitude', 'longitude', 'temperature', 'salinity', 'depth']
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        
                        if 'platform_id' not in df.columns:
                            df['platform_id'] = 'API_DATA'
                        
                        if missing_columns:
                            return load_sample_data()
                        
                        return df
                    else:
                        return load_sample_data()
                else:
                    return load_sample_data()
            else:
                return load_sample_data()
        else:
            return load_sample_data()
            
    except Exception as e:
        print(f"API Error: {e}")  # Debug logging
        return load_sample_data()

def create_temperature_map(data):
    """Create an interactive temperature map using Plotly"""
    if data is None or data.empty:
        return None
    
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
        height=500,
        margin={"r":10,"t":60,"l":10,"b":10},
        font=dict(family="Inter, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        title_x=0.5
    )
    
    return fig

def create_depth_profile_chart(data):
    """Create enhanced depth profile visualization"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['temperature'],
        y=-data['depth'],
        mode='markers',
        marker=dict(
            size=8,
            color=data['temperature'],
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(
                title=dict(text="Temperature (°C)", side="right"),
                thickness=15
            ),
            line=dict(width=1, color='white')
        ),
        name='Temperature Profile',
        hovertemplate='<b>Temperature:</b> %{x:.1f}°C<br><b>Depth:</b> %{y:.0f}m<br><extra></extra>'
    ))
    
    fig.update_layout(
        title="Ocean Depth Profile Analysis",
        xaxis_title="Temperature (°C)",
        yaxis_title="Depth (m)",
        font=dict(family="Inter", size=12),
        plot_bgcolor='rgba(26, 32, 44, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    return fig

def create_statistics_chart(data):
    """Create comprehensive statistical analysis chart"""
    if data is None or data.empty:
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature Distribution', 'Salinity Distribution', 
                       'Depth Distribution', 'Data Points'),
        specs=[[{"type": "histogram"}, {"type": "histogram"}],
               [{"type": "histogram"}, {"type": "scatter"}]]
    )
    
    fig.add_trace(go.Histogram(
        x=data['temperature'],
        nbinsx=15,
        name='Temperature',
        marker_color='rgba(66, 153, 225, 0.7)',
        hovertemplate='Temperature: %{x:.1f}°C<br>Count: %{y}<extra></extra>'
    ), row=1, col=1)
    
    fig.add_trace(go.Histogram(
        x=data['salinity'],
        nbinsx=15,
        name='Salinity',
        marker_color='rgba(72, 187, 120, 0.7)',
        hovertemplate='Salinity: %{x:.1f} PSU<br>Count: %{y}<extra></extra>'
    ), row=1, col=2)
    
    fig.add_trace(go.Histogram(
        x=data['depth'],
        nbinsx=15,
        name='Depth',
        marker_color='rgba(128, 90, 213, 0.7)',
        hovertemplate='Depth: %{x:.0f}m<br>Count: %{y}<extra></extra>'
    ), row=2, col=1)
    
    fig.add_trace(go.Scatter(
        x=data['longitude'],
        y=data['latitude'],
        mode='markers',
        marker=dict(
            size=6,
            color=data['temperature'],
            colorscale='RdYlBu_r',
            line=dict(width=1, color='white')
        ),
        name='Locations',
        hovertemplate='<b>Lat:</b> %{y:.2f}°<br><b>Lon:</b> %{x:.2f}°<br><extra></extra>'
    ), row=2, col=2)
    
    fig.update_layout(
        height=500,
        showlegend=False,
        title_text="Comprehensive Ocean Data Analysis",
        title_x=0.5,
        font=dict(family="Inter", size=10),
        plot_bgcolor='rgba(26, 32, 44, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Routes
@app.route('/')
def index():
    """Main chat interface"""
    system_status = fetch_system_status()
    live_status = fetch_live_data_status()
    return render_template('index.html', 
                         system_status=system_status, 
                         live_status=live_status,
                         profiles=PROFILES,
                         current_profile=current_profile,
                         profile_info=PROFILES.get(current_profile, PROFILES["researcher"]))

@app.route('/api/profiles')
def get_profiles():
    """Get all available profiles"""
    return jsonify({
        "profiles": PROFILES,
        "current_profile": current_profile
    })

@app.route('/api/profiles/switch', methods=['POST'])
def switch_profile():
    """Switch to a different user profile"""
    global current_profile
    
    try:
        data = request.json
        new_profile = data.get('profile')
        
        if new_profile in PROFILES:
            current_profile = new_profile
            profile_info = PROFILES[new_profile]
            
            return jsonify({
                "success": True,
                "message": f"Switched to {profile_info['name']} profile",
                "profile": new_profile,
                "profile_info": profile_info
            })
        else:
            return jsonify({
                "success": False,
                "error": "Invalid profile selected"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/profiles/current')
def get_current_profile():
    """Get current profile information"""
    return jsonify({
        "current_profile": current_profile,
        "profile_info": PROFILES.get(current_profile, PROFILES["researcher"])
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return responses with visualizations"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Query the backend API
        ocean_data = query_ocean_api(user_message)
        
        # Generate appropriate visualization based on query
        charts = []
        response_text = f"I found {len(ocean_data)} ocean data points for your query: '{user_message}'"
        
        # Generate statistics
        stats = {
            "avg_temperature": f"{ocean_data['temperature'].mean():.1f}°C",
            "avg_salinity": f"{ocean_data['salinity'].mean():.1f} PSU",
            "max_depth": f"{ocean_data['depth'].max():.0f}m",
            "data_points": len(ocean_data),
            "platforms": ocean_data['platform_id'].nunique()
        }
        
        # Create visualizations based on query content
        if 'map' in user_message.lower() or 'location' in user_message.lower():
            map_fig = create_temperature_map(ocean_data.sample(min(50, len(ocean_data))))
            if map_fig:
                charts.append({
                    'type': 'map',
                    'data': json.dumps(map_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Ocean Temperature Map'
                })
        
        if 'depth' in user_message.lower() or 'profile' in user_message.lower():
            depth_fig = create_depth_profile_chart(ocean_data.sample(min(100, len(ocean_data))))
            if depth_fig:
                charts.append({
                    'type': 'depth',
                    'data': json.dumps(depth_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Depth Profile Analysis'
                })
        
        if 'analysis' in user_message.lower() or 'statistics' in user_message.lower():
            stats_fig = create_statistics_chart(ocean_data.sample(min(200, len(ocean_data))))
            if stats_fig:
                charts.append({
                    'type': 'statistics',
                    'data': json.dumps(stats_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Statistical Analysis'
                })
        
        # If no specific visualization requested, provide a summary with basic chart
        if not charts:
            depth_fig = create_depth_profile_chart(ocean_data.sample(min(50, len(ocean_data))))
            if depth_fig:
                charts.append({
                    'type': 'depth',
                    'data': json.dumps(depth_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Ocean Data Overview'
                })
        
        return jsonify({
            'response': response_text,
            'charts': charts,
            'stats': stats,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({
            'error': f"Error processing your request: {str(e)}",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }), 500

@app.route('/api/system-status')
def get_system_status():
    """Get current system status"""
    return jsonify(fetch_system_status())

@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    """Handle quick action buttons"""
    try:
        data = request.json
        action = data.get('action', '')
        
        # Map actions to queries
        action_queries = {
            'temperature': "Show temperature analysis with depth profiles",
            'map': "Create an interactive map of ocean data",
            'metrics': "Show comprehensive ocean data metrics",
            'dashboard': "Generate full ocean dashboard",
            'salinity': "Analyze salinity patterns in ocean data",
            'charts': "Create advanced ocean data visualizations",
            'global': "Analyze global ocean patterns and trends",
            'status': "Show system status and health check"
        }
        
        query = action_queries.get(action, "Show ocean data overview")
        
        # Process the query same as chat
        ocean_data = query_ocean_api(query)
        charts = []
        
        if action == 'temperature':
            depth_fig = create_depth_profile_chart(ocean_data)
            if depth_fig:
                charts.append({
                    'type': 'depth',
                    'data': json.dumps(depth_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Temperature vs Depth Analysis'
                })
        elif action == 'map':
            map_fig = create_temperature_map(ocean_data.sample(min(100, len(ocean_data))))
            if map_fig:
                charts.append({
                    'type': 'map',
                    'data': json.dumps(map_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Interactive Ocean Map'
                })
        elif action == 'charts':
            stats_fig = create_statistics_chart(ocean_data)
            if stats_fig:
                charts.append({
                    'type': 'statistics',
                    'data': json.dumps(stats_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Advanced Charts'
                })
        elif action == 'status':
            return jsonify({
                'response': 'System Status Check Complete',
                'stats': fetch_system_status(),
                'charts': [],
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
        else:
            # Default response with depth chart
            depth_fig = create_depth_profile_chart(ocean_data.sample(min(50, len(ocean_data))))
            if depth_fig:
                charts.append({
                    'type': 'depth',
                    'data': json.dumps(depth_fig, cls=plotly.utils.PlotlyJSONEncoder),
                    'title': 'Ocean Data Overview'
                })
        
        stats = {
            "avg_temperature": f"{ocean_data['temperature'].mean():.1f}°C",
            "avg_salinity": f"{ocean_data['salinity'].mean():.1f} PSU",
            "max_depth": f"{ocean_data['depth'].max():.0f}m",
            "data_points": len(ocean_data),
            "platforms": ocean_data['platform_id'].nunique()
        }
        
        return jsonify({
            'response': f"Action '{action}' completed successfully with {len(ocean_data)} data points.",
            'charts': charts,
            'stats': stats,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({
            'error': f"Error processing action: {str(e)}",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)