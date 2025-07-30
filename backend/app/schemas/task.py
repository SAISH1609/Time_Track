from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# Shared properties
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"
    estimated_hours: Optional[int] = None
    project_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = "#3B82F6"
    due_date: Optional[datetime] = None
    is_billable: Optional[bool] = True


# Properties to receive via API on creation
class TaskCreate(TaskBase):
    title: str


# Properties to receive via API on update
class TaskUpdate(TaskBase):
    title: Optional[str] = None
    completed_at: Optional[datetime] = None


# Properties to return via API
class Task(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    ace_task_id: Optional[str] = None
    ace_category: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True


# Task with sub-tasks
class TaskWithSubTasks(Task):
    sub_tasks: List[Task] = []

    class Config:
        orm_mode = True


# Task summary for dashboard
class TaskSummary(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    color: str
    project_name: Optional[str] = None
    total_time: int = 0  # Total time in seconds
    is_running: bool = False

    class Config:
        orm_mode = True


# Quick task creation
class QuickTaskCreate(BaseModel):
    title: str
    project_id: Optional[int] = None


# Task status update
class TaskStatusUpdate(BaseModel):
    status: str  # todo, in_progress, completed, archived


# Task time tracking
class TaskTimeInfo(BaseModel):
    task_id: int
    task_title: str
    total_time: int  # Total time in seconds
    entries_count: int
    last_entry: Optional[datetime] = None
    is_running: bool = False

    class Config:
        orm_mode = True
