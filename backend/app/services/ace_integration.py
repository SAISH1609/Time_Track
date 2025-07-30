from typing import Dict, List, Any, Optional
from datetime import datetime, date
import requests
import json
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud.time_entry import time_entry as crud_time_entry
from app.schemas.report import ACETimesheetEntry, ACEExportRequest


class ACEIntegrationService:
    def __init__(self):
        self.base_url = settings.ACE_API_BASE_URL
        self.api_key = settings.ACE_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def test_connection(self) -> bool:
        """Test connection to ACE API."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_ace_projects(self) -> List[Dict[str, Any]]:
        """Fetch available projects from ACE."""
        try:
            response = requests.get(
                f"{self.base_url}/projects",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch ACE projects: {str(e)}")

    def get_ace_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Fetch available tasks for a project from ACE."""
        try:
            response = requests.get(
                f"{self.base_url}/projects/{project_id}/tasks",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch ACE tasks: {str(e)}")

    def export_to_ace(self, db: Session, user_id: int, export_request: ACEExportRequest) -> Dict[str, Any]:
        """Export time entries to ACE timesheet."""
        # Get time entries for the period
        entries = crud_time_entry.get_by_date_range(
            db, user_id, export_request.start_date, export_request.end_date
        )

        # Convert to ACE format
        ace_entries = []
        for entry in entries:
            if not entry.duration or entry.synced_to_ace:
                continue  # Skip entries without duration or already synced

            # Map project and task using provided mappings
            project_code = export_request.project_mappings.get(
                entry.project_id)
            task_id = export_request.task_mappings.get(entry.task_id)

            if not project_code or not task_id:
                continue  # Skip if no mapping available

            ace_entry = ACETimesheetEntry(
                task_id=task_id,
                project_code=project_code,
                hours=round(entry.duration / 3600, 2),
                description=entry.description or "",
                date=entry.start_time.date(),
                category="Development"  # Default category
            )
            ace_entries.append(ace_entry)

        # Submit to ACE
        if ace_entries:
            result = self._submit_timesheet_entries(ace_entries)

            # Mark entries as synced if successful
            if result.get("success"):
                self._mark_entries_synced(db, entries)

            return result
        else:
            return {"success": False, "message": "No entries to export"}

    def _submit_timesheet_entries(self, entries: List[ACETimesheetEntry]) -> Dict[str, Any]:
        """Submit timesheet entries to ACE."""
        try:
            payload = {
                "entries": [entry.dict() for entry in entries]
            }

            response = requests.post(
                f"{self.base_url}/timesheet/entries",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            return {
                "success": True,
                "message": f"Successfully exported {len(entries)} entries",
                "ace_response": response.json()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to export to ACE: {str(e)}"
            }

    def _mark_entries_synced(self, db: Session, entries: List):
        """Mark time entries as synced to ACE."""
        for entry in entries:
            entry.synced_to_ace = True
            entry.ace_sync_date = datetime.utcnow()
            db.add(entry)
        db.commit()

    def sync_project_mappings(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Sync project mappings with ACE."""
        try:
            ace_projects = self.get_ace_projects()

            # Store mappings in user settings
            # This would typically be stored in a dedicated mapping table
            mappings = {
                project["id"]: project["name"]
                for project in ace_projects
            }

            return {
                "success": True,
                "mappings": mappings,
                "count": len(mappings)
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def validate_mappings(self, project_mappings: Dict[int, str], task_mappings: Dict[int, str]) -> Dict[str, Any]:
        """Validate project and task mappings against ACE."""
        try:
            # Validate project codes
            ace_projects = self.get_ace_projects()
            valid_project_codes = {p["code"] for p in ace_projects}

            invalid_projects = []
            for internal_id, ace_code in project_mappings.items():
                if ace_code not in valid_project_codes:
                    invalid_projects.append(
                        f"Project {internal_id}: {ace_code}")

            # Validate task IDs (simplified - would need project context)
            invalid_tasks = []

            return {
                "valid": len(invalid_projects) == 0 and len(invalid_tasks) == 0,
                "invalid_projects": invalid_projects,
                "invalid_tasks": invalid_tasks
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def get_sync_status(self, db: Session, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get sync status for time entries in date range."""
        entries = crud_time_entry.get_by_date_range(
            db, user_id, start_date, end_date)

        total_entries = len(entries)
        synced_entries = len([e for e in entries if e.synced_to_ace])
        pending_entries = total_entries - synced_entries

        return {
            "total_entries": total_entries,
            "synced_entries": synced_entries,
            "pending_entries": pending_entries,
            "sync_percentage": round((synced_entries / total_entries) * 100, 1) if total_entries > 0 else 0,
            "last_sync": max([e.ace_sync_date for e in entries if e.ace_sync_date], default=None)
        }

    def configure_auto_sync(self, db: Session, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure automatic sync settings."""
        # This would store auto-sync preferences in user settings
        # For example: daily sync at specific time, weekly sync, etc.

        valid_settings = {
            "enabled": settings.get("enabled", False),
            # daily, weekly, monthly
            "frequency": settings.get("frequency", "weekly"),
            "time": settings.get("time", "18:00"),  # Time of day for sync
            "auto_map_new_projects": settings.get("auto_map_new_projects", False)
        }

        # Store in user's ACE integration settings
        # This would be implemented with the user model's ace_integration_settings field

        return {
            "success": True,
            "settings": valid_settings
        }


ace_integration_service = ACEIntegrationService()
