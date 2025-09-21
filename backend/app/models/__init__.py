"""
Ocean Chat Backend 2.0 - Models Package

Import all models for easy access and registration.
"""

from app.models.ocean_data import OceanMeasurement, NCFileMetadata
from app.models.users import User, QueryHistory

__all__ = [
    "OceanMeasurement",
    "NCFileMetadata", 
    "User",
    "QueryHistory"
]