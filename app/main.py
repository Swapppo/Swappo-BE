from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from sqlalchemy.orm import Session
import os

from .models import (
    UserCreate, UserLogin, UserResponse, Token, 
    RefreshTokenRequest, ChangePassword
)
from .auth import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, verify_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Check if we should use SQL database or in-memory
USE_SQL_DB = os.getenv("DATABASE_URL") is not None

if USE_SQL_DB:
    from .database_sql import (
        get_user_by_email, create_user, update_user_password, get_user_by_id
    )
    from .db_config import get_db, init_db
    
    # Initialize database tables
    init_db()
else:
    from .database import (
        get_user_by_email, create_user, update_user_password, get_user_by_id
    )

app = FastAPI(
    title="Authentication Microservice",
    description="RESTful authentication API for mobile applications",
    version="1.0.0"
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your mobile app domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {
        "message": "Authentication Microservice API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "refresh": "/api/v1/auth/refresh",
            "me": "/api/v1/auth/me",
            "change-password": "/api/v1/auth/change-password"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db) if USE_SQL_DB else None):
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email) if USE_SQL_DB else get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    if USE_SQL_DB:
        user = create_user(db, user_data.email, user_data.username, hashed_password, user_data.full_name)
    else:
        user = create_user(user_data.email, user_data.username, hashed_password, user_data.full_name)
    
    return UserResponse(**user)


@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db) if USE_SQL_DB else None):
    """Login user and return access and refresh tokens."""
    # Get user from database
    user = get_user_by_email(db, user_credentials.email) if USE_SQL_DB else get_user_by_email(user_credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/v1/auth/refresh", response_model=Token)
async def refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db) if USE_SQL_DB else None):
    """Refresh access token using refresh token."""
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, "refresh")
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user still exists and is active
    user = get_user_by_id(db, user_id) if USE_SQL_DB else get_user_by_id(user_id)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": user_id, "email": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user_id, "email": email}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db) if USE_SQL_DB else None):
    """Get current authenticated user information."""
    user = get_user_by_id(db, current_user["user_id"]) if USE_SQL_DB else get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


@app.post("/api/v1/auth/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db) if USE_SQL_DB else None
):
    """Change user password."""
    user = get_user_by_id(db, current_user["user_id"]) if USE_SQL_DB else get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Update password
    new_hashed_password = get_password_hash(password_data.new_password)
    if USE_SQL_DB:
        update_user_password(db, current_user["user_id"], new_hashed_password)
    else:
        update_user_password(current_user["user_id"], new_hashed_password)
    
    return {"message": "Password changed successfully"}


@app.post("/api/v1/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (client should delete tokens)."""
    # In a production environment with token blacklisting, add token to blacklist here
    return {"message": "Logged out successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)