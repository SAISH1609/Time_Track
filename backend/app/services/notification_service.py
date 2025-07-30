from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.report_service import report_service
from app.crud.user import user as crud_user


class NotificationService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.teams_webhook = settings.TEAMS_WEBHOOK_URL

    def send_daily_summary(self, db: Session, user_id: int, supervisor_email: str) -> Dict[str, Any]:
        """Send daily work summary to supervisor."""
        try:
            user = crud_user.get(db, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get today's data
            today = date.today()
            summary_data = self._generate_daily_summary(db, user_id, today)

            # Generate email content
            subject = f"Daily Work Summary - {user.full_name or user.username} - {today}"
            html_content = self._generate_daily_email_template(
                summary_data, user)

            # Send email
            result = self._send_email(
                to_email=supervisor_email,
                subject=subject,
                html_content=html_content
            )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_weekly_summary(self, db: Session, user_id: int, supervisor_email: str) -> Dict[str, Any]:
        """Send weekly work summary to supervisor."""
        try:
            user = crud_user.get(db, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get this week's data
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            summary_data = self._generate_weekly_summary(
                db, user_id, start_of_week, end_of_week)

            # Generate email content
            subject = f"Weekly Work Summary - {user.full_name or user.username} - Week of {start_of_week}"
            html_content = self._generate_weekly_email_template(
                summary_data, user, start_of_week, end_of_week)

            # Send email
            result = self._send_email(
                to_email=supervisor_email,
                subject=subject,
                html_content=html_content
            )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_teams_summary(self, db: Session, user_id: int, summary_type: str = "daily") -> Dict[str, Any]:
        """Send work summary to Microsoft Teams channel."""
        try:
            user = crud_user.get(db, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            if summary_type == "daily":
                today = date.today()
                summary_data = self._generate_daily_summary(db, user_id, today)
                message = self._generate_teams_daily_message(
                    summary_data, user, today)
            else:  # weekly
                today = date.today()
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                summary_data = self._generate_weekly_summary(
                    db, user_id, start_of_week, end_of_week)
                message = self._generate_teams_weekly_message(
                    summary_data, user, start_of_week, end_of_week)

            # Send to Teams
            result = self._send_teams_message(message)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_daily_summary(self, db: Session, user_id: int, target_date: date) -> Dict[str, Any]:
        """Generate daily summary data."""
        from app.crud.time_entry import time_entry as crud_time_entry
        from app.crud.task import task as crud_task

        # Get time entries for the day
        entries = crud_time_entry.get_by_date_range(
            db, user_id, target_date, target_date)

        total_time = sum(entry.duration or 0 for entry in entries)
        billable_time = sum(
            entry.duration or 0 for entry in entries if entry.is_billable)

        # Group by project/task
        project_breakdown = {}
        task_breakdown = {}

        for entry in entries:
            project_name = entry.project.name if entry.project else "No Project"
            task_name = entry.task.title if entry.task else "Unknown Task"

            project_breakdown[project_name] = project_breakdown.get(
                project_name, 0) + (entry.duration or 0)
            task_breakdown[task_name] = task_breakdown.get(
                task_name, 0) + (entry.duration or 0)

        return {
            "date": target_date,
            "total_hours": round(total_time / 3600, 2),
            "billable_hours": round(billable_time / 3600, 2),
            "entries_count": len(entries),
            "projects": {k: round(v / 3600, 2) for k, v in project_breakdown.items()},
            "tasks": {k: round(v / 3600, 2) for k, v in task_breakdown.items()}
        }

    def _generate_weekly_summary(self, db: Session, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate weekly summary data."""
        from app.schemas.report import ReportRequest, ReportType

        report_request = ReportRequest(
            start_date=start_date,
            end_date=end_date,
            report_type=ReportType.WEEKLY
        )

        report_data = report_service.generate_time_report(
            db, user_id, report_request)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "summary": report_data["summary"],
            "projects": report_data["projects"][:5],  # Top 5 projects
            "daily_breakdown": report_data["daily_breakdown"]
        }

    def _generate_daily_email_template(self, summary_data: Dict[str, Any], user) -> str:
        """Generate HTML email template for daily summary."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Daily Work Summary</h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Employee: {user.full_name or user.username}</h3>
                    <h3>Date: {summary_data['date']}</h3>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Time Summary</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>Total Hours:</strong> {summary_data['total_hours']}</li>
                        <li><strong>Billable Hours:</strong> {summary_data['billable_hours']}</li>
                        <li><strong>Time Entries:</strong> {summary_data['entries_count']}</li>
                    </ul>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>Project Breakdown</h3>
                    <ul>
                        {"".join([f"<li><strong>{project}:</strong> {hours} hours</li>" for project, hours in summary_data['projects'].items()])}
                    </ul>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>Top Tasks</h3>
                    <ul>
                        {"".join([f"<li><strong>{task}:</strong> {hours} hours</li>" for task, hours in list(summary_data['tasks'].items())[:5]])}
                    </ul>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                    <p>This summary was automatically generated by TimeTrack on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_weekly_email_template(self, summary_data: Dict[str, Any], user, start_date: date, end_date: date) -> str:
        """Generate HTML email template for weekly summary."""
        summary = summary_data["summary"]

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Weekly Work Summary</h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Employee: {user.full_name or user.username}</h3>
                    <h3>Week: {start_date} to {end_date}</h3>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Weekly Summary</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>Total Hours:</strong> {round(summary['total_time'] / 3600, 2)}</li>
                        <li><strong>Billable Hours:</strong> {round(summary['billable_time'] / 3600, 2)}</li>
                        <li><strong>Projects Worked:</strong> {summary['unique_projects']}</li>
                        <li><strong>Tasks Completed:</strong> {summary['unique_tasks']}</li>
                        <li><strong>Avg Daily Hours:</strong> {round(summary['average_daily_time'] / 3600, 2)}</li>
                    </ul>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>Top Projects</h3>
                    <ul>
                        {"".join([f"<li><strong>{project['project_name']}:</strong> {round(project['total_time'] / 3600, 2)} hours</li>" for project in summary_data['projects']])}
                    </ul>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                    <p>This summary was automatically generated by TimeTrack on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_teams_daily_message(self, summary_data: Dict[str, Any], user, target_date: date) -> Dict[str, Any]:
        """Generate Teams message for daily summary."""
        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": f"Daily Work Summary - {user.full_name or user.username}",
            "sections": [{
                "activityTitle": f"Daily Work Summary - {user.full_name or user.username}",
                "activitySubtitle": f"Date: {target_date}",
                "facts": [
                    {"name": "Total Hours", "value": str(
                        summary_data['total_hours'])},
                    {"name": "Billable Hours", "value": str(
                        summary_data['billable_hours'])},
                    {"name": "Time Entries", "value": str(
                        summary_data['entries_count'])},
                    {"name": "Projects", "value": str(
                        len(summary_data['projects']))}
                ],
                "markdown": True
            }]
        }

    def _generate_teams_weekly_message(self, summary_data: Dict[str, Any], user, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate Teams message for weekly summary."""
        summary = summary_data["summary"]

        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": f"Weekly Work Summary - {user.full_name or user.username}",
            "sections": [{
                "activityTitle": f"Weekly Work Summary - {user.full_name or user.username}",
                "activitySubtitle": f"Week: {start_date} to {end_date}",
                "facts": [
                    {"name": "Total Hours", "value": str(
                        round(summary['total_time'] / 3600, 2))},
                    {"name": "Billable Hours", "value": str(
                        round(summary['billable_time'] / 3600, 2))},
                    {"name": "Projects", "value": str(
                        summary['unique_projects'])},
                    {"name": "Tasks", "value": str(summary['unique_tasks'])},
                    {"name": "Avg Daily Hours", "value": str(
                        round(summary['average_daily_time'] / 3600, 2))}
                ],
                "markdown": True
            }]
        }

    def _send_email(self, to_email: str, subject: str, html_content: str) -> Dict[str, Any]:
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return {"success": True, "message": f"Email sent to {to_email}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_teams_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Microsoft Teams webhook."""
        try:
            response = requests.post(
                self.teams_webhook,
                headers={'Content-Type': 'application/json'},
                json=message,
                timeout=30
            )
            response.raise_for_status()

            return {"success": True, "message": "Message sent to Teams"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def schedule_automated_summaries(self, db: Session, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure scheduled automated summaries."""
        # This would integrate with a task scheduler like Celery
        # For now, we'll just store the settings

        valid_settings = {
            "daily_enabled": settings.get("daily_enabled", False),
            "weekly_enabled": settings.get("weekly_enabled", False),
            "supervisor_email": settings.get("supervisor_email", ""),
            "teams_enabled": settings.get("teams_enabled", False),
            "daily_time": settings.get("daily_time", "18:00"),
            "weekly_day": settings.get("weekly_day", "friday"),
            "weekly_time": settings.get("weekly_time", "17:00")
        }

        # Store in user settings (would be implemented with user model)

        return {
            "success": True,
            "message": "Automated summary settings updated",
            "settings": valid_settings
        }


notification_service = NotificationService()
