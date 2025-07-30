from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.time_entry import time_entry as crud_time_entry
from app.crud.task import task as crud_task
from app.schemas.time_entry import TimerStart, TimerStop, TimerUpdate


class TimerService:
    def __init__(self):
        pass

    def start_timer(self, db: Session, user_id: int, timer_data: TimerStart):
        """Start a new timer for a task."""
        # Verify task exists and belongs to user
        task = crud_task.get(db, timer_data.task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to track time for this task"
            )

        # Stop any running timer first
        running_entry = crud_time_entry.get_running_entry(db, user_id)
        if running_entry:
            self.stop_timer(db, user_id, TimerStop())

        # Start new timer
        entry = crud_time_entry.start_timer(
            db,
            task_id=timer_data.task_id,
            user_id=user_id,
            description=timer_data.description
        )

        # Update task status to in_progress if it's not already
        if task.status == "todo":
            task.status = "in_progress"
            db.add(task)
            db.commit()

        return entry

    def stop_timer(self, db: Session, user_id: int, timer_data: TimerStop):
        """Stop the currently running timer."""
        running_entry = crud_time_entry.get_running_entry(db, user_id)
        if not running_entry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No running timer found"
            )

        stopped_entry = crud_time_entry.stop_timer(
            db,
            running_entry.id,
            user_id,
            description=timer_data.description,
            notes=timer_data.notes
        )

        return stopped_entry

    def pause_timer(self, db: Session, user_id: int):
        """Pause the currently running timer."""
        return self.stop_timer(db, user_id, TimerStop())

    def get_timer_status(self, db: Session, user_id: int):
        """Get current timer status."""
        running_entry = crud_time_entry.get_running_entry(db, user_id)

        if running_entry:
            elapsed_time = int(
                (datetime.utcnow() - running_entry.start_time).total_seconds())
            return {
                "is_running": True,
                "current_entry": running_entry,
                "elapsed_time": elapsed_time
            }
        else:
            return {
                "is_running": False,
                "current_entry": None,
                "elapsed_time": 0
            }

    def update_running_timer(self, db: Session, user_id: int, timer_data: TimerUpdate):
        """Update the description of the currently running timer."""
        running_entry = crud_time_entry.get_running_entry(db, user_id)
        if not running_entry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No running timer found"
            )

        if timer_data.description is not None:
            running_entry.description = timer_data.description
            db.add(running_entry)
            db.commit()
            db.refresh(running_entry)

        return running_entry

    def switch_task(self, db: Session, user_id: int, new_task_id: int, description: str = None):
        """Switch timer to a different task."""
        # Stop current timer
        running_entry = crud_time_entry.get_running_entry(db, user_id)
        if running_entry:
            self.stop_timer(db, user_id, TimerStop())

        # Start timer for new task
        timer_start = TimerStart(task_id=new_task_id, description=description)
        return self.start_timer(db, user_id, timer_start)

    def get_elapsed_time(self, db: Session, user_id: int) -> int:
        """Get elapsed time for currently running timer in seconds."""
        running_entry = crud_time_entry.get_running_entry(db, user_id)
        if running_entry:
            return int((datetime.utcnow() - running_entry.start_time).total_seconds())
        return 0

    def validate_timer_entry(self, db: Session, entry_id: int, user_id: int):
        """Validate a timer entry (for supervisor approval)."""
        entry = crud_time_entry.get(db, entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found"
            )

        # For now, only the entry owner can validate
        # In future, add supervisor validation logic
        if entry.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to validate this entry"
            )

        entry.is_validated = True
        entry.validated_by = user_id
        entry.validated_at = datetime.utcnow()

        db.add(entry)
        db.commit()
        db.refresh(entry)

        return entry

    def get_timer_stats(self, db: Session, user_id: int):
        """Get timer statistics for today."""
        from datetime import date

        today = date.today()
        total_today = crud_time_entry.get_daily_total(db, user_id, today)

        return {
            "today_total": total_today,
            "today_hours": round(total_today / 3600, 2),
            "is_running": crud_time_entry.get_running_entry(db, user_id) is not None
        }


timer_service = TimerService()
