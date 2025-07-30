from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)

    # Time tracking
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds

    # Description and notes
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Entry metadata
    is_billable = Column(Boolean, default=True)
    # True if timer is currently running
    is_running = Column(Boolean, default=False)

    # Manual vs automatic
    is_manual = Column(Boolean, default=False)  # True if manually entered

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ACE Integration
    ace_entry_id = Column(String, nullable=True)  # External ACE entry ID
    synced_to_ace = Column(Boolean, default=False)
    ace_sync_date = Column(DateTime(timezone=True), nullable=True)

    # Entry validation
    is_validated = Column(Boolean, default=False)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship(
        "User", back_populates="time_entries", foreign_keys=[user_id])
    task = relationship("Task", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    validator = relationship(
        "User", back_populates="validated_entries", foreign_keys=[validated_by])
