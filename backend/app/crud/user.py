from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import security


class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create new user."""
        hashed_password = security.get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            hashed_password=hashed_password,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """Update user."""
        update_data = obj_in.dict(exclude_unset=True)

        if "password" in update_data:
            hashed_password = security.get_password_hash(
                update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        # Try to find user by username or email
        user = self.get_by_username(db, username)
        if not user:
            user = self.get_by_email(db, username)

        if not user:
            return None

        if not security.verify_password(password, user.hashed_password):
            return None

        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser

    def update_last_login(self, db: Session, user: User) -> User:
        """Update user's last login timestamp."""
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user = CRUDUser()
