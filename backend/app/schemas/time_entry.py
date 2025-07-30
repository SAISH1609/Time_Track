from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# Shared properties
class TimeEntryBase(BaseModel):
    description: Optional[str] = None
    notes: Optional[str] = None
    task_id: int
    project_id: Optional[int] = None
    is_billable: Optional[bool] = True


# Properties to receive via API on creation
class TimeEntryCreate(TimeEntryBase):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in seconds
    is_manual: Optional[bool] = False


# Properties to receive via API on update
class TimeEntryUpdate(TimeEntryBase):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None


# Properties to return via API
class TimeEntry(TimeEntryBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    is_running: bool
    is_manual: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    ace_entry_id: Optional[str] = None
    synced_to_ace: bool
    is_validated: bool

    class Config:
        orm_mode = True


# Timer control schemas
class TimerStart(BaseModel):
    task_id: int
    description: Optional[str] = None


class TimerStop(BaseModel):
    description: Optional[str] = None
    notes: Optional[str] = None


class TimerUpdate(BaseModel):
    description: Optional[str] = None


# Time entry with task details
class TimeEntryWithTask(TimeEntry):
    task_title: str
    task_color: str
    project_name: Optional[str] = None

    class Config:
        orm_mode = True


# Manual time entry
class ManualTimeEntry(BaseModel):
    task_id: int
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    notes: Optional[str] = None
    is_billable: Optional[bool] = True


# Current timer status
class TimerStatus(BaseModel):
    is_running: bool
    current_entry: Optional[TimeEntry] = None
    elapsed_time: int = 0  # Elapsed time in seconds

    class Config:
        orm_mode = True


# Time entry summary
class TimeEntrySummary(BaseModel):
    date: datetime
    total_time: int  # Total time in seconds
    entries_count: int
    billable_time: int  # Billable time in seconds

    class Config:
        orm_mode = True
