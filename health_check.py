# 🔧 OceanChat System Health Check
# Run this before your SIH demo to ensure everything is working perfectly

import requests
import time
import sys
from datetime import datetime

def print_status(message, status):
    """Print formatted status message"""
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_database():
    """Check database connectivity"""
    try:
        response = requests.get("http://localhost:8000/api/chat", 
                              json={"query": "system status"}, timeout=10)
        return response.status_code == 200
    except:
        return False

def check_frontend():
    """Check if frontend is accessible"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Run comprehensive system health check"""
    print("🌊 OceanChat System Health Check")
    print("=" * 50)
    print(f"🕒 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check backend
    print("🔍 Checking Backend Service...")
    backend_ok = check_backend()
    print_status("Backend API (Port 8000)", backend_ok)
    
    if not backend_ok:
        print("💡 Start backend: cd backend && python main.py")
        print()
    
    # Check database
    print("\n🔍 Checking Database Connection...")
    db_ok = check_database()
    print_status("Database Query Response", db_ok)
    
    # Check frontend
    print("\n🔍 Checking Frontend Service...")
    frontend_ok = check_frontend()
    print_status("Streamlit Frontend (Port 8501)", frontend_ok)
    
    if not frontend_ok:
        print("💡 Start frontend: cd frontend && streamlit run app.py")
        print()
    
    # Overall status
    print("\n" + "=" * 50)
    all_good = backend_ok and db_ok and frontend_ok
    
    if all_good:
        print("🏆 SYSTEM READY FOR SIH DEMO!")
        print("🚀 All services running perfectly")
        print("🌊 Demo URLs:")
        print("   • Frontend: http://localhost:8501")
        print("   • Backend API: http://localhost:8000")
        print("   • Health Check: http://localhost:8000/health")
    else:
        print("⚠️  SYSTEM NEEDS ATTENTION")
        print("🔧 Fix the issues above before demo")
    
    print("\n🎯 Quick Demo Test:")
    print("1. Open http://localhost:8501")
    print("2. Click 'Indian Ocean Salinity' button")
    print("3. Verify data loads and charts appear")
    print("4. Check system status in sidebar shows green")
    
    return all_good

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Health check cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)