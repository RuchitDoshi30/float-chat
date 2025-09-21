"""
Ocean Chat Backend 2.0 - Ocean Data Models

SQLAlchemy models for oceanographic data storage.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
# from geoalchemy2 import Geometry  # Uncomment for PostGIS support
import uuid
from datetime import datetime

from app.core.database import Base


class OceanMeasurement(Base):
    """Model for storing oceanographic measurements from NetCDF files."""
    
    __tablename__ = "ocean_measurements"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Spatial coordinates
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    depth = Column(Float, nullable=False, index=True)
    
    # Measurements
    temperature = Column(Float)  # Celsius
    salinity = Column(Float)     # PSU (Practical Salinity Units)
    pressure = Column(Float)     # Decibars
    
    # Temporal information
    measurement_time = Column(DateTime, nullable=False, index=True)
    
    # Data source and quality
    data_source = Column(String(50), nullable=False, default="nc_file")
    quality_flag = Column(Integer, default=1)  # 1=good, 2=questionable, 3=bad
    
    # Metadata
    platform_id = Column(String(100))  # Argo float ID, satellite name, etc.
    instrument_type = Column(String(100))
    
    # Geospatial column for PostGIS (uncomment when PostGIS is available)
    # geom = Column(Geometry('POINT', srid=4326))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<OceanMeasurement(lat={self.latitude}, lon={self.longitude}, temp={self.temperature})>"


class NCFileMetadata(Base):
    """Model for tracking NetCDF files ingested into the database."""
    
    __tablename__ = "nc_file_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(Text)
    file_size = Column(Integer)  # bytes
    
    # Spatial bounds
    min_latitude = Column(Float)
    max_latitude = Column(Float)
    min_longitude = Column(Float)
    max_longitude = Column(Float)
    
    # Temporal bounds
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Data statistics
    total_measurements = Column(Integer, default=0)
    variables = Column(Text)  # JSON string of available variables
    
    # Processing information
    ingestion_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    ingestion_date = Column(DateTime)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database indexes for performance
Index('idx_ocean_measurements_spatial', OceanMeasurement.latitude, OceanMeasurement.longitude)
Index('idx_ocean_measurements_temporal', OceanMeasurement.measurement_time)
Index('idx_ocean_measurements_depth', OceanMeasurement.depth)
Index('idx_ocean_measurements_source', OceanMeasurement.data_source)

# Spatial index using PostGIS (uncomment when PostGIS is available)
# Index('idx_ocean_measurements_geom', OceanMeasurement.geom, postgresql_using='gist')