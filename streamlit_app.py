"""
🌊 OceanChat - Streamlit Cloud Deployment Entry Point
Main application file for Streamlit Cloud deployment
"""

import sys
import os

# Add frontend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Import and run the main app
from frontend.app import main

if __name__ == "__main__":
    main()