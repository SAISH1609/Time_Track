from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate, UserLogin
from app.core.security import security


class AuthService:
    def __init__(self):
        pass

    def register_user(self, db: Session, user_data: UserCreate):
        """Register a new user."""
        # Check if user already exists
        existing_user = crud_user.get_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        existing_username = crud_user.get_by_username(db, user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists"
            )

        # Create new user
        user = crud_user.create(db, user_data)
        return user

    def authenticate_user(self, db: Session, login_data: UserLogin):
        """Authenticate user and return tokens."""
        user = crud_user.authenticate(
            db, login_data.username, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Update last login
        crud_user.update_last_login(db, user)

        # Create access token
        access_token_expires = timedelta(
            minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": security.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user
        }

    def get_current_user(self, db: Session, token: str):
        """Get current user from JWT token."""
        user_id = security.verify_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = crud_user.get(db, id=int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        return user

    def refresh_token(self, db: Session, refresh_token: str):
        """Refresh access token using refresh token."""
        user_id = security.verify_token(refresh_token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = crud_user.get(db, id=int(user_id))
        if not user or not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Create new access token
        access_token_expires = timedelta(
            minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": security.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def change_password(self, db: Session, user_id: int, old_password: str, new_password: str):
        """Change user password."""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not security.verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        # Update password
        hashed_password = security.get_password_hash(new_password)
        user.hashed_password = hashed_password
        db.add(user)
        db.commit()

        return {"message": "Password updated successfully"}


auth_service = AuthService()
