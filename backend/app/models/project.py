from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Project properties
    color = Column(String, default="#3B82F6")  # Hex color for UI
    is_active = Column(Boolean, default=True)
    is_billable = Column(Boolean, default=True)

    # Project metadata
    client_name = Column(String, nullable=True)
    project_code = Column(String, nullable=True, index=True)
    hourly_rate = Column(Integer, nullable=True)  # Rate in cents
    budget_hours = Column(Integer, nullable=True)  # Budget in minutes

    # Associations
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # ACE Integration
    ace_project_id = Column(String, nullable=True)  # External ACE project ID
    ace_project_code = Column(String, nullable=True)

    # Project settings
    # JSON string for project-specific settings
    settings = Column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    time_entries = relationship("TimeEntry", back_populates="project")
