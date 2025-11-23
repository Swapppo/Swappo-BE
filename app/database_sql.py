from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from .db_config import UserDB


def get_user_by_email(db: Session, email: str) -> Optional[dict]:
    """Get user by email."""
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user:
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "is_active": user.is_active
        }
    return None


def get_user_by_id(db: Session, user_id: str) -> Optional[dict]:
    """Get user by ID."""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "is_active": user.is_active
        }
    return None


def create_user(db: Session, email: str, username: str, hashed_password: str, full_name: Optional[str] = None) -> dict:
    """Create a new user."""
    user_id = str(uuid.uuid4())
    db_user = UserDB(
        id=user_id,
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        created_at=datetime.utcnow(),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "hashed_password": db_user.hashed_password,
        "full_name": db_user.full_name,
        "created_at": db_user.created_at,
        "is_active": db_user.is_active
    }


def update_user_password(db: Session, user_id: str, hashed_password: str) -> bool:
    """Update user password."""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        user.hashed_password = hashed_password
        db.commit()
        return True
    return False


def deactivate_user(db: Session, user_id: str) -> bool:
    """Deactivate user account."""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        return True
    return False
