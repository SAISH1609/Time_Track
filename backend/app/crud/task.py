from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class CRUDTask:
    def get(self, db: Session, id: int) -> Optional[Task]:
        """Get task by ID."""
        return db.query(Task).filter(Task.id == id).first()

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by user ID."""
        return db.query(Task).filter(
            and_(Task.user_id == user_id, Task.is_active == True)
        ).offset(skip).limit(limit).all()

    def get_by_project(self, db: Session, project_id: int, user_id: int) -> List[Task]:
        """Get tasks by project ID for a specific user."""
        return db.query(Task).filter(
            and_(
                Task.project_id == project_id,
                Task.user_id == user_id,
                Task.is_active == True
            )
        ).all()

    def get_active_tasks(self, db: Session, user_id: int) -> List[Task]:
        """Get active (non-completed) tasks for user."""
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.is_active == True,
                Task.status.in_(["todo", "in_progress"])
            )
        ).all()

    def get_sub_tasks(self, db: Session, parent_task_id: int, user_id: int) -> List[Task]:
        """Get sub-tasks for a parent task."""
        return db.query(Task).filter(
            and_(
                Task.parent_task_id == parent_task_id,
                Task.user_id == user_id,
                Task.is_active == True
            )
        ).all()

    def search_tasks(self, db: Session, user_id: int, query: str) -> List[Task]:
        """Search tasks by title or description."""
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.is_active == True,
                or_(
                    Task.title.ilike(f"%{query}%"),
                    Task.description.ilike(f"%{query}%")
                )
            )
        ).all()

    def create(self, db: Session, obj_in: TaskCreate, user_id: int) -> Task:
        """Create new task."""
        db_obj = Task(
            **obj_in.dict(),
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Task, obj_in: TaskUpdate) -> Task:
        """Update task."""
        update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def complete_task(self, db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """Mark task as completed."""
        from datetime import datetime

        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if task:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            db.add(task)
            db.commit()
            db.refresh(task)

        return task

    def archive_task(self, db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """Archive task (soft delete)."""
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if task:
            task.status = "archived"
            task.is_active = False
            db.add(task)
            db.commit()
            db.refresh(task)

        return task

    def delete(self, db: Session, id: int, user_id: int) -> Optional[Task]:
        """Delete task (hard delete)."""
        task = db.query(Task).filter(
            and_(Task.id == id, Task.user_id == user_id)
        ).first()

        if task:
            db.delete(task)
            db.commit()

        return task

    def get_tasks_by_status(self, db: Session, user_id: int, status: str) -> List[Task]:
        """Get tasks by status."""
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.status == status,
                Task.is_active == True
            )
        ).all()

    def get_overdue_tasks(self, db: Session, user_id: int) -> List[Task]:
        """Get overdue tasks."""
        from datetime import datetime

        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.due_date < datetime.utcnow(),
                Task.status.in_(["todo", "in_progress"]),
                Task.is_active == True
            )
        ).all()


task = CRUDTask()
