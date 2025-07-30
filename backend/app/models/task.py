from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Task hierarchy
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    # Task properties
    # todo, in_progress, completed, archived
    status = Column(String, default="todo")
    priority = Column(String, default="medium")  # low, medium, high, urgent
    # Estimated time in minutes
    estimated_hours = Column(Integer, nullable=True)

    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Metadata
    tags = Column(Text, nullable=True)  # JSON array of tags
    color = Column(String, default="#3B82F6")  # Hex color for UI

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)

    # ACE Integration
    ace_task_id = Column(String, nullable=True)  # External ACE task ID
    ace_category = Column(String, nullable=True)  # ACE category mapping

    # Active tracking
    is_active = Column(Boolean, default=True)
    is_billable = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    time_entries = relationship("TimeEntry", back_populates="task")

    # Self-referential relationship for sub-tasks
    parent_task = relationship("Task", remote_side=[id], backref="sub_tasks")
