from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Profile information
    avatar_url = Column(String, nullable=True)
    timezone = Column(String, default="UTC")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Settings
    default_project_id = Column(Integer, nullable=True)
    notification_preferences = Column(Text, nullable=True)  # JSON string
    ace_integration_settings = Column(Text, nullable=True)  # JSON string

    # Relationships
    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="user")
    time_entries = relationship(
        "TimeEntry", back_populates="user", foreign_keys="TimeEntry.user_id")
    validated_entries = relationship(
        "TimeEntry", foreign_keys="TimeEntry.validated_by")
