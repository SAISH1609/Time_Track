from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import pandas as pd
import io
from app.crud.time_entry import time_entry as crud_time_entry
from app.crud.task import task as crud_task
from app.models.time_entry import TimeEntry
from app.models.task import Task
from app.schemas.report import ReportRequest, ExportRequest, ReportType


class ReportService:
    def __init__(self):
        pass

    def generate_time_report(self, db: Session, user_id: int, report_request: ReportRequest):
        """Generate comprehensive time report."""
        start_date = report_request.start_date
        end_date = report_request.end_date

        # Get time entries for the period
        entries = crud_time_entry.get_by_date_range(
            db, user_id, start_date, end_date)

        if not entries:
            return {
                "summary": self._empty_summary(),
                "tasks": [],
                "projects": [],
                "daily_breakdown": []
            }

        # Generate report based on grouping
        if report_request.group_by == "task":
            return self._generate_task_report(db, entries, start_date, end_date)
        elif report_request.group_by == "project":
            return self._generate_project_report(db, entries, start_date, end_date)
        elif report_request.group_by == "date":
            return self._generate_daily_report(db, entries, start_date, end_date)
        else:
            return self._generate_comprehensive_report(db, entries, start_date, end_date)

    def _generate_comprehensive_report(self, db: Session, entries: List[TimeEntry], start_date: date, end_date: date):
        """Generate comprehensive report with all breakdowns."""
        # Calculate summary
        total_time = sum(entry.duration or 0 for entry in entries)
        billable_time = sum(
            entry.duration or 0 for entry in entries if entry.is_billable)

        # Task breakdown
        task_data = {}
        for entry in entries:
            task_id = entry.task_id
            if task_id not in task_data:
                task_data[task_id] = {
                    "task_id": task_id,
                    "task_title": entry.task.title if entry.task else "Unknown",
                    "project_name": entry.project.name if entry.project else None,
                    "total_time": 0,
                    "billable_time": 0,
                    "entries_count": 0
                }

            task_data[task_id]["total_time"] += entry.duration or 0
            if entry.is_billable:
                task_data[task_id]["billable_time"] += entry.duration or 0
            task_data[task_id]["entries_count"] += 1

        # Project breakdown
        project_data = {}
        for entry in entries:
            project_id = entry.project_id or 0
            project_name = entry.project.name if entry.project else "No Project"

            if project_id not in project_data:
                project_data[project_id] = {
                    "project_id": project_id if project_id > 0 else None,
                    "project_name": project_name,
                    "total_time": 0,
                    "billable_time": 0,
                    "tasks_count": set(),
                    "entries_count": 0
                }

            project_data[project_id]["total_time"] += entry.duration or 0
            if entry.is_billable:
                project_data[project_id]["billable_time"] += entry.duration or 0
            project_data[project_id]["tasks_count"].add(entry.task_id)
            project_data[project_id]["entries_count"] += 1

        # Convert sets to counts
        for project in project_data.values():
            project["tasks_count"] = len(project["tasks_count"])

        # Daily breakdown
        daily_data = {}
        for entry in entries:
            entry_date = entry.start_time.date()
            if entry_date not in daily_data:
                daily_data[entry_date] = {
                    "date": entry_date,
                    "total_time": 0,
                    "billable_time": 0,
                    "entries_count": 0,
                    "tasks_worked": set(),
                    "projects_worked": set()
                }

            daily_data[entry_date]["total_time"] += entry.duration or 0
            if entry.is_billable:
                daily_data[entry_date]["billable_time"] += entry.duration or 0
            daily_data[entry_date]["entries_count"] += 1
            daily_data[entry_date]["tasks_worked"].add(entry.task_id)
            if entry.project_id:
                daily_data[entry_date]["projects_worked"].add(entry.project_id)

        # Convert sets to counts
        for daily in daily_data.values():
            daily["tasks_worked"] = len(daily["tasks_worked"])
            daily["projects_worked"] = len(daily["projects_worked"])

        # Calculate summary statistics
        total_days = (end_date - start_date).days + 1
        working_days = len(daily_data)

        summary = {
            "total_time": total_time,
            "billable_time": billable_time,
            "total_entries": len(entries),
            "unique_tasks": len(task_data),
            "unique_projects": len(project_data),
            "average_daily_time": total_time // working_days if working_days > 0 else 0,
            "most_productive_day": max(daily_data.items(), key=lambda x: x[1]["total_time"])[0] if daily_data else None,
            "most_worked_project": max(project_data.values(), key=lambda x: x["total_time"])["project_name"] if project_data else None
        }

        return {
            "summary": summary,
            "tasks": list(task_data.values()),
            "projects": list(project_data.values()),
            "daily_breakdown": list(daily_data.values())
        }

    def _generate_task_report(self, db: Session, entries: List[TimeEntry], start_date: date, end_date: date):
        """Generate task-focused report."""
        # Implementation similar to comprehensive but focused on tasks
        pass

    def _generate_project_report(self, db: Session, entries: List[TimeEntry], start_date: date, end_date: date):
        """Generate project-focused report."""
        # Implementation similar to comprehensive but focused on projects
        pass

    def _generate_daily_report(self, db: Session, entries: List[TimeEntry], start_date: date, end_date: date):
        """Generate daily breakdown report."""
        # Implementation similar to comprehensive but focused on daily stats
        pass

    def _empty_summary(self):
        """Return empty summary for when no data is found."""
        return {
            "total_time": 0,
            "billable_time": 0,
            "total_entries": 0,
            "unique_tasks": 0,
            "unique_projects": 0,
            "average_daily_time": 0,
            "most_productive_day": None,
            "most_worked_project": None
        }

    def export_to_csv(self, db: Session, user_id: int, export_request: ExportRequest):
        """Export time data to CSV format."""
        entries = crud_time_entry.get_by_date_range(
            db, user_id, export_request.start_date, export_request.end_date)

        # Prepare data for CSV
        csv_data = []
        for entry in entries:
            csv_data.append({
                "Date": entry.start_time.date(),
                "Start Time": entry.start_time.strftime("%H:%M:%S"),
                "End Time": entry.end_time.strftime("%H:%M:%S") if entry.end_time else "",
                "Duration (hours)": round((entry.duration or 0) / 3600, 2),
                "Task": entry.task.title if entry.task else "",
                "Project": entry.project.name if entry.project else "",
                "Description": entry.description or "",
                "Notes": entry.notes or "",
                "Billable": "Yes" if entry.is_billable else "No"
            })

        # Create CSV
        df = pd.DataFrame(csv_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        return csv_buffer.getvalue()

    def export_to_excel(self, db: Session, user_id: int, export_request: ExportRequest):
        """Export time data to Excel format."""
        entries = crud_time_entry.get_by_date_range(
            db, user_id, export_request.start_date, export_request.end_date)

        # Prepare data
        excel_data = []
        for entry in entries:
            excel_data.append({
                "Date": entry.start_time.date(),
                "Start Time": entry.start_time.strftime("%H:%M:%S"),
                "End Time": entry.end_time.strftime("%H:%M:%S") if entry.end_time else "",
                "Duration (hours)": round((entry.duration or 0) / 3600, 2),
                "Task": entry.task.title if entry.task else "",
                "Project": entry.project.name if entry.project else "",
                "Description": entry.description or "",
                "Notes": entry.notes or "",
                "Billable": "Yes" if entry.is_billable else "No"
            })

        # Create Excel file
        df = pd.DataFrame(excel_data)
        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Time Entries', index=False)

            # Add summary sheet if requested
            if export_request.include_details:
                report = self.generate_time_report(db, user_id, export_request)
                summary_data = [{
                    "Metric": k.replace("_", " ").title(),
                    "Value": v
                } for k, v in report["summary"].items() if v is not None]

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    def generate_performance_review(self, db: Session, user_id: int, start_date: date, end_date: date):
        """Generate performance review data."""
        report_request = ReportRequest(
            start_date=start_date,
            end_date=end_date,
            report_type=ReportType.CUSTOM,
            group_by="project"
        )

        report_data = self.generate_time_report(db, user_id, report_request)

        # Generate insights and recommendations
        achievements = self._generate_achievements(report_data)
        recommendations = self._generate_recommendations(report_data)
        productivity_trends = self._analyze_productivity_trends(report_data)

        return {
            "period_start": start_date,
            "period_end": end_date,
            "summary": report_data["summary"],
            "top_projects": sorted(report_data["projects"], key=lambda x: x["total_time"], reverse=True)[:5],
            "achievements": achievements,
            "recommendations": recommendations,
            "productivity_trends": productivity_trends
        }

    def _generate_achievements(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate achievements based on report data."""
        achievements = []

        summary = report_data["summary"]
        total_hours = summary["total_time"] / 3600

        if total_hours > 40:
            achievements.append(
                f"Logged {total_hours:.1f} hours of productive work")

        if summary["unique_projects"] > 3:
            achievements.append(
                f"Contributed to {summary['unique_projects']} different projects")

        if summary["billable_time"] / summary["total_time"] > 0.8:
            achievements.append("Maintained high billable time ratio (>80%)")

        return achievements

    def _generate_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on report data."""
        recommendations = []

        # Add logic for generating recommendations based on work patterns
        summary = report_data["summary"]

        if summary["average_daily_time"] < 4 * 3600:  # Less than 4 hours per day
            recommendations.append(
                "Consider tracking more detailed time entries to improve accuracy")

        return recommendations

    def _analyze_productivity_trends(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze productivity trends."""
        return {
            "weekly_pattern": "Analysis of weekly work patterns",
            "peak_hours": "Identification of most productive hours",
            "project_distribution": "Project time distribution analysis"
        }


report_service = ReportService()
