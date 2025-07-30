from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, date
from app.models.time_entry import TimeEntry
from app.schemas.time_entry import TimeEntryCreate, TimeEntryUpdate


class CRUDTimeEntry:
    def get(self, db: Session, id: int) -> Optional[TimeEntry]:
        """Get time entry by ID."""
        return db.query(TimeEntry).filter(TimeEntry.id == id).first()

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[TimeEntry]:
        """Get time entries by user ID."""
        return db.query(TimeEntry).filter(
            TimeEntry.user_id == user_id
        ).order_by(desc(TimeEntry.start_time)).offset(skip).limit(limit).all()

    def get_running_entry(self, db: Session, user_id: int) -> Optional[TimeEntry]:
        """Get currently running time entry for user."""
        return db.query(TimeEntry).filter(
            and_(
                TimeEntry.user_id == user_id,
                TimeEntry.is_running == True
            )
        ).first()

    def get_by_task(self, db: Session, task_id: int, user_id: int) -> List[TimeEntry]:
        """Get time entries for a specific task."""
        return db.query(TimeEntry).filter(
            and_(
                TimeEntry.task_id == task_id,
                TimeEntry.user_id == user_id
            )
        ).order_by(desc(TimeEntry.start_time)).all()

    def get_by_date_range(self, db: Session, user_id: int, start_date: date, end_date: date) -> List[TimeEntry]:
        """Get time entries within a date range."""
        return db.query(TimeEntry).filter(
            and_(
                TimeEntry.user_id == user_id,
                func.date(TimeEntry.start_time) >= start_date,
                func.date(TimeEntry.start_time) <= end_date
            )
        ).order_by(desc(TimeEntry.start_time)).all()

    def get_by_project(self, db: Session, project_id: int, user_id: int) -> List[TimeEntry]:
        """Get time entries for a specific project."""
        return db.query(TimeEntry).filter(
            and_(
                TimeEntry.project_id == project_id,
                TimeEntry.user_id == user_id
            )
        ).order_by(desc(TimeEntry.start_time)).all()

    def create(self, db: Session, obj_in: TimeEntryCreate, user_id: int) -> TimeEntry:
        """Create new time entry."""
        # Calculate duration if both start and end times are provided
        duration = None
        if obj_in.start_time and obj_in.end_time:
            duration = int(
                (obj_in.end_time - obj_in.start_time).total_seconds())
        elif obj_in.duration:
            duration = obj_in.duration

        db_obj = TimeEntry(
            **obj_in.dict(exclude={"duration"}),
            user_id=user_id,
            duration=duration
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def start_timer(self, db: Session, task_id: int, user_id: int, description: str = None) -> TimeEntry:
        """Start a new timer."""
        # Stop any running timer first
        self.stop_running_timer(db, user_id)

        db_obj = TimeEntry(
            task_id=task_id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            description=description,
            is_running=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def stop_timer(self, db: Session, entry_id: int, user_id: int, description: str = None, notes: str = None) -> Optional[TimeEntry]:
        """Stop a running timer."""
        entry = db.query(TimeEntry).filter(
            and_(
                TimeEntry.id == entry_id,
                TimeEntry.user_id == user_id,
                TimeEntry.is_running == True
            )
        ).first()

        if entry:
            now = datetime.utcnow()
            entry.end_time = now
            entry.duration = int((now - entry.start_time).total_seconds())
            entry.is_running = False

            if description:
                entry.description = description
            if notes:
                entry.notes = notes

            db.add(entry)
            db.commit()
            db.refresh(entry)

        return entry

    def stop_running_timer(self, db: Session, user_id: int) -> Optional[TimeEntry]:
        """Stop any currently running timer for user."""
        running_entry = self.get_running_entry(db, user_id)
        if running_entry:
            return self.stop_timer(db, running_entry.id, user_id)
        return None

    def update(self, db: Session, db_obj: TimeEntry, obj_in: TimeEntryUpdate) -> TimeEntry:
        """Update time entry."""
        update_data = obj_in.dict(exclude_unset=True)

        # Recalculate duration if start or end time is updated
        if "start_time" in update_data or "end_time" in update_data:
            start_time = update_data.get("start_time", db_obj.start_time)
            end_time = update_data.get("end_time", db_obj.end_time)

            if start_time and end_time:
                update_data["duration"] = int(
                    (end_time - start_time).total_seconds())

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, user_id: int) -> Optional[TimeEntry]:
        """Delete time entry."""
        entry = db.query(TimeEntry).filter(
            and_(TimeEntry.id == id, TimeEntry.user_id == user_id)
        ).first()

        if entry:
            db.delete(entry)
            db.commit()

        return entry

    def get_total_time_by_task(self, db: Session, task_id: int, user_id: int) -> int:
        """Get total time spent on a task in seconds."""
        result = db.query(func.sum(TimeEntry.duration)).filter(
            and_(
                TimeEntry.task_id == task_id,
                TimeEntry.user_id == user_id,
                TimeEntry.duration.isnot(None)
            )
        ).scalar()

        return result or 0

    def get_total_time_by_project(self, db: Session, project_id: int, user_id: int) -> int:
        """Get total time spent on a project in seconds."""
        result = db.query(func.sum(TimeEntry.duration)).filter(
            and_(
                TimeEntry.project_id == project_id,
                TimeEntry.user_id == user_id,
                TimeEntry.duration.isnot(None)
            )
        ).scalar()

        return result or 0

    def get_daily_total(self, db: Session, user_id: int, target_date: date) -> int:
        """Get total time for a specific date in seconds."""
        result = db.query(func.sum(TimeEntry.duration)).filter(
            and_(
                TimeEntry.user_id == user_id,
                func.date(TimeEntry.start_time) == target_date,
                TimeEntry.duration.isnot(None)
            )
        ).scalar()

        return result or 0


time_entry = CRUDTimeEntry()
