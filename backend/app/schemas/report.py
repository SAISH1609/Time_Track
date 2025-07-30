from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"


class ReportGroupBy(str, Enum):
    TASK = "task"
    PROJECT = "project"
    DATE = "date"
    USER = "user"


# Report request schemas
class ReportRequest(BaseModel):
    start_date: date
    end_date: date
    report_type: ReportType
    group_by: Optional[ReportGroupBy] = ReportGroupBy.TASK
    project_ids: Optional[List[int]] = None
    task_ids: Optional[List[int]] = None
    include_billable_only: Optional[bool] = False


class ExportRequest(ReportRequest):
    format: ExportFormat
    include_details: Optional[bool] = True


# Report response schemas
class TaskTimeReport(BaseModel):
    task_id: int
    task_title: str
    project_name: Optional[str] = None
    total_time: int  # Total time in seconds
    billable_time: int  # Billable time in seconds
    entries_count: int
    average_session: int  # Average session length in seconds

    class Config:
        orm_mode = True


class ProjectTimeReport(BaseModel):
    project_id: Optional[int] = None
    project_name: str
    total_time: int  # Total time in seconds
    billable_time: int  # Billable time in seconds
    tasks_count: int
    entries_count: int
    completion_percentage: Optional[float] = None

    class Config:
        orm_mode = True


class DailyTimeReport(BaseModel):
    date: date
    total_time: int  # Total time in seconds
    billable_time: int  # Billable time in seconds
    entries_count: int
    tasks_worked: int
    projects_worked: int

    class Config:
        orm_mode = True


class TimeReportSummary(BaseModel):
    total_time: int  # Total time in seconds
    billable_time: int  # Billable time in seconds
    total_entries: int
    unique_tasks: int
    unique_projects: int
    average_daily_time: int  # Average daily time in seconds
    most_productive_day: Optional[date] = None
    most_worked_project: Optional[str] = None

    class Config:
        orm_mode = True


class DetailedReport(BaseModel):
    summary: TimeReportSummary
    tasks: List[TaskTimeReport]
    projects: List[ProjectTimeReport]
    daily_breakdown: List[DailyTimeReport]

    class Config:
        orm_mode = True


# Performance review schemas
class PerformanceReviewData(BaseModel):
    period_start: date
    period_end: date
    summary: TimeReportSummary
    top_projects: List[ProjectTimeReport]
    achievements: List[str]
    recommendations: List[str]
    productivity_trends: Dict[str, Any]

    class Config:
        orm_mode = True


# ACE integration schemas
class ACETimesheetEntry(BaseModel):
    task_id: str
    project_code: str
    hours: float
    description: str
    date: date
    category: Optional[str] = None


class ACEExportRequest(BaseModel):
    start_date: date
    end_date: date
    project_mappings: Dict[int, str]  # Internal project_id -> ACE project_code
    task_mappings: Dict[int, str]  # Internal task_id -> ACE task_id


# Supervisor summary schemas
class SupervisorSummary(BaseModel):
    employee_name: str
    period: str
    total_hours: float
    projects_summary: List[ProjectTimeReport]
    highlights: List[str]
    concerns: List[str]
    generated_at: datetime

    class Config:
        orm_mode = True
