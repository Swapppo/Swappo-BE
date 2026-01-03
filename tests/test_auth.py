import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_db, user_email_index

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_database():
    """Clear database before each test."""
    users_db.clear()
    user_email_index.clear()
    yield
    users_db.clear()
    user_email_index.clear()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_register_user():
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email():
    """Test registration with duplicate email."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }
    # First registration
    client.post("/api/v1/auth/register", json=user_data)

    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    """Test successful login."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Login
    login_data = {"email": "test@example.com", "password": "testpassword123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Login with wrong password
    login_data = {"email": "test@example.com", "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_login_nonexistent_user():
    """Test login with nonexistent user."""
    login_data = {"email": "nonexistent@example.com", "password": "testpassword123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user information."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    }
    client.post("/api/v1/auth/register", json=user_data)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]


def test_get_current_user_no_token():
    """Test getting current user without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_refresh_token():
    """Test refreshing access token."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }
    client.post("/api/v1/auth/register", json=user_data)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_change_password():
    """Test changing password."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "oldpassword123",
    }
    client.post("/api/v1/auth/register", json=user_data)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "oldpassword123"},
    )
    token = login_response.json()["access_token"]

    # Change password
    response = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "oldpassword123", "new_password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Try login with old password (should fail)
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "oldpassword123"},
    )
    assert old_login.status_code == 401

    # Try login with new password (should succeed)
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "newpassword123"},
    )
    assert new_login.status_code == 200


def test_logout():
    """Test logout endpoint."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }
    client.post("/api/v1/auth/register", json=user_data)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Logout
    response = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
