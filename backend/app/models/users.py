"""
Ocean Chat Backend 2.0 - User Models

SQLAlchemy models for user management and authentication.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base


class User(Base):
    """Model for user accounts."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Profile information
    institution = Column(String(255))
    research_area = Column(String(255))
    bio = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


class QueryHistory(Base):
    """Model for storing user query history."""
    
    __tablename__ = "query_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User reference (optional for anonymous queries)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Query information
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # spatial, temporal, parameter, etc.
    
    # Results metadata
    data_source_used = Column(String(20))  # "api" or "database"
    result_count = Column(Integer)
    response_time_ms = Column(Integer)
    
    # Status
    status = Column(String(20), default="completed")  # completed, failed, timeout
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QueryHistory(user_id={self.user_id}, query={self.query_text[:50]}...)>"