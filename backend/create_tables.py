#!/usr/bin/env python3
"""
Create database tables for Ocean Chat Backend 2.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models.ocean_data import OceanMeasurement, NCFileMetadata
from app.core.config import settings

def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("\nCreated tables:")
        print("- ocean_measurements")
        print("- nc_file_metadata")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print(f"Connecting to database: {settings.DATABASE_NAME}")
    
    if create_tables():
        print("\n🎉 Database setup completed!")
    else:
        print("\n💥 Database setup failed!")
        sys.exit(1)