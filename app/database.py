from typing import Optional, Dict
from datetime import datetime
import uuid

# In-memory database (for development)
# In production, replace with actual database (PostgreSQL, MongoDB, etc.)
users_db: Dict[str, dict] = {}
user_email_index: Dict[str, str] = {}  # email -> user_id mapping


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email."""
    user_id = user_email_index.get(email)
    if user_id:
        return users_db.get(user_id)
    return None


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    return users_db.get(user_id)


def create_user(
    email: str, username: str, hashed_password: str, full_name: Optional[str] = None
) -> dict:
    """Create a new user."""
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": email,
        "username": username,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "created_at": datetime.utcnow(),
        "is_active": True,
    }
    users_db[user_id] = user
    user_email_index[email] = user_id
    return user


def update_user_password(user_id: str, hashed_password: str) -> bool:
    """Update user password."""
    if user_id in users_db:
        users_db[user_id]["hashed_password"] = hashed_password
        return True
    return False


def deactivate_user(user_id: str) -> bool:
    """Deactivate user account."""
    if user_id in users_db:
        users_db[user_id]["is_active"] = False
        return True
    return False
