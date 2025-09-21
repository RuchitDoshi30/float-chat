# 🌊 OceanChat - AI-Powered Oceanographic Analysis Platform

[![SIH 2025](https://img.shields.io/badge/SIH-2025-blue.svg)](https://sih.gov.in/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)

> **Smart India Hackathon 2025** - Revolutionizing oceanographic research through AI-powered natural language queries and real-time data integration.

## 🎯 Problem Statement

Traditional oceanographic research faces critical challenges:
- **Data Fragmentation**: Ocean data scattered across multiple sources
- **Complex Analysis**: Requires specialized technical knowledge  
- **Real-time Access**: Difficulty accessing live ocean measurements
- **Visualization Barriers**: Complex tools for data interpretation

## 🚀 Our Solution

**OceanChat** bridges this gap with an AI-powered platform that transforms complex oceanographic data into accessible insights through natural language queries.

### ✨ Key Features

- 🤖 **AI-Powered Queries**: Natural language to oceanographic insights
- 📡 **Real-time Data**: Live Argo network integration (320K+ measurements)
- 📊 **Advanced Visualizations**: Research-grade depth profiles and statistical analysis
- 🗺️ **Interactive Maps**: Real-time ocean data visualization
- ⚡ **High Performance**: Sub-500ms response times
- 🎯 **Demo-Ready**: 11 quick actions for presentations

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **PostgreSQL + PostGIS**: Geospatial database
- **OpenAI GPT**: Natural language processing
- **Python**: Data processing and analysis

### Frontend
- **Streamlit**: Modern web application framework
- **Plotly**: Interactive scientific visualizations
- **Folium**: Interactive mapping

### Data Sources
- **Argo Network**: Real-time ocean floats data
- **NetCDF Processing**: Scientific data format handling
- **Live API Integration**: Continuous data updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL with PostGIS
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RuchitDoshi30/float-chat.git
   cd float-chat
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your database credentials and OpenAI API key
   
   # Initialize database
   python create_tables.py
   
   # Start backend server
   python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   pip install -r requirements.txt
   
   # Start frontend
   streamlit run app.py
   ```

4. **Access the Application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Health Check
```bash
python health_check.py
```

## 🎮 Demo Guide

### Quick Demo Actions
1. **🧂 Indian Ocean Salinity** - Regional analysis showcase
2. **📊 Temperature Profiles** - Depth analysis demonstration  
3. **🌊 Real-time Ocean Data** - Live data capabilities
4. **🗺️ Global Ocean Map** - Interactive mapping
5. **📈 Complete Ocean Analysis** - Full feature showcase

### Sample Queries
- "What's the salinity in the Indian Ocean?"
- "Show temperature trends in the Pacific"
- "Create a depth profile for recent measurements"
- "Map all ocean data from this week"

## 📊 System Capabilities

- **📈 320,094+ Ocean Measurements** in database
- **⚡ Sub-500ms Response Times** for queries
- **🌐 24/7 Live Data Integration** from Argo network
- **🔬 Research-Grade Visualizations** with statistical analysis
- **📊 4-Panel Statistical Analysis** with depth profiles
- **💻 Real-time System Monitoring** dashboard

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │     FastAPI     │    │   PostgreSQL    │
│   Frontend      │───▶│    Backend      │───▶│   + PostGIS     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   OpenAI GPT    │              │
         │              │   NLP Service   │              │
         │              └─────────────────┘              │
         │                                               │
         ▼                                               ▼
┌─────────────────┐                           ┌─────────────────┐
│ Real-time Argo  │                           │  NetCDF Data    │
│ Network APIs    │                           │  Processing     │
└─────────────────┘                           └─────────────────┘
```

## 🎯 SIH 2025 Demo

For **Smart India Hackathon 2025** presentations:

1. **Demo Script**: See `SIH_DEMO_SCRIPT.md` for 5-7 minute presentation
2. **Health Check**: Run `python health_check.py` before demo
3. **Backup Plan**: Video guide available in `SIH_VIDEO_GUIDE.md`
4. **Setup**: Use `demo_setup.ps1` for automated startup

## 📈 Impact & Applications

### Target Users
- **🔬 Marine Researchers**: Instant data access and analysis
- **🌡️ Climate Scientists**: Real-time ocean monitoring
- **🎓 Educational Institutions**: Interactive learning platform
- **🏛️ Policy Makers**: Data-driven ocean conservation decisions

### Use Cases
- Climate change research and monitoring
- Marine ecosystem analysis
- Educational oceanography tools
- Environmental policy support
- Real-time ocean condition monitoring

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed for **Smart India Hackathon 2025**. See the [LICENSE](LICENSE) file for details.

## 👥 Team

**Team Members**: [Add your team member names here]

**Institution**: [Add your college/institution name]

**SIH 2025**: Problem Statement - Oceanographic Data Analysis

## 🙏 Acknowledgments

- **Argo Network** for real-time ocean data
- **Smart India Hackathon 2025** for the opportunity
- **OpenAI** for GPT integration
- **Streamlit** and **FastAPI** communities

## 📞 Contact

For questions about this SIH 2025 project:
- GitHub: [@RuchitDoshi30](https://github.com/RuchitDoshi30)
- Repository: [float-chat](https://github.com/RuchitDoshi30/float-chat)

---

<div align="center">
<strong>🏆 Built for Smart India Hackathon 2025 🌊</strong><br>
<em>Democratizing Ocean Science Through AI</em>
</div>