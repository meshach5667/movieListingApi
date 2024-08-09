import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app and database models
from main import app
from database.database import Base, get_db
from models.models import *
from schemas.schemas import *

# Database connection URL
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Create a test database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session maker for the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

# Pytest fixture for the test database
@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()

# Test functions
def test_signup(test_db):
    response = client.post("/signup", json={
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["firstName"] == "Test"
    assert data["lastName"] == "User"

def test_login(test_db):
    # First, create a user
    client.post("/signup", json={
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_user(test_db):
    # First, create a user
    response = client.post("/signup", json={
        "username": "testuser2",
        "password": "testpassword2",
        "email": "testuser2@example.com",
        "firstName": "Test2",
        "lastName": "User2"
    })
    user_id = response.json()["id"]
    
    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser2"
    assert data["email"] == "testuser2@example.com"
    assert data["firstName"] == "Test2"
    assert data["lastName"] == "User2"