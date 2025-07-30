from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import auth_service
from app.schemas.user import UserCreate, UserLogin, Token, User


router = APIRouter()


@router.post("/register", response_model=User)
def register(user_data: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    return auth_service.register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db=Depends(get_db)):
    """Authenticate user and return access token."""
    result = auth_service.authenticate_user(db, login_data)
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "expires_in": result["expires_in"]
    }


@router.post("/refresh")
def refresh_token(refresh_token: str, db=Depends(get_db)):
    """Refresh access token."""
    return auth_service.refresh_token(db, refresh_token)


@router.post("/change-password", response_model=None)
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Change user password."""
    return auth_service.change_password(db, current_user.id, old_password, new_password)


@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
