from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.timer_service import timer_service
from app.schemas.user import User
from app.schemas.time_entry import TimerStart, TimerStop, TimerUpdate, TimerStatus


router = APIRouter()


@router.post("/start")
def start_timer(
    timer_data: TimerStart,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Start a new timer for a task."""
    return timer_service.start_timer(db, current_user.id, timer_data)


@router.post("/stop")
def stop_timer(
    timer_data: TimerStop,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Stop the currently running timer."""
    return timer_service.stop_timer(db, current_user.id, timer_data)


@router.post("/pause")
def pause_timer(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Pause the currently running timer."""
    return timer_service.pause_timer(db, current_user.id)


@router.get("/status", response_model=TimerStatus)
def get_timer_status(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get current timer status."""
    return timer_service.get_timer_status(db, current_user.id)


@router.put("/update")
def update_running_timer(
    timer_data: TimerUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update the currently running timer."""
    return timer_service.update_running_timer(db, current_user.id, timer_data)


@router.post("/switch/{task_id}")
def switch_task(
    task_id: int,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Switch timer to a different task."""
    return timer_service.switch_task(db, current_user.id, task_id, description)


@router.get("/stats")
def get_timer_stats(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get timer statistics for today."""
    return timer_service.get_timer_stats(db, current_user.id)
