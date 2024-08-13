import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import timedelta
from ..main import app
from database.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.schemas import User, Movie, Comment, Rating
from jwt_token import create_access_token
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a test database
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a test client
client = TestClient(app)

# Create a test database session
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db function with the test database session
app.dependency_overrides[get_db] = override_get_db

# Create the database tables
# Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_signup():
    response = client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_get_user():
    # First create a user
    client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    response = client.get("/user/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_login():
    client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    response = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    })
    print(response.json())  # Debugging line
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_password():
    # First create a user
    client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    response = client.post("/login", data={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

# Movie-related test cases

def test_create_movie():
    # First, authenticate the user
    token = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    }).json()["access_token"]

    response = client.post(
        "/movies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Movie",
            "release_date": "2024-08-13",
            "genre": "Action",
            "director": "Jane Doe",
            "synopsis": "An action-packed movie.",
            "runtime": 120,
            "language": "English",
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"

def test_get_movies():
    response = client.get("/movies/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_movie():
    movie_id = 1
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"

def test_update_movie():
    # First, authenticate the user
    token = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    }).json()["access_token"]

    movie_id = 1
    response = client.put(
        f"/movies/{movie_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Movie Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Movie Title"

def test_delete_movie():
    # First, authenticate the user
    token = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    }).json()["access_token"]

    movie_id = 1
    response = client.delete(
        f"/movies/{movie_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Movie deleted successfully"}

    # Check if the movie is really deleted
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 404
