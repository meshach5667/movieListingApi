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
def authenticate_test_user():
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200, "Authentication failed"
    token_data = response.json()
    assert "access_token" in token_data, f"Expected 'access_token' in response, got {token_data}"
    return token_data["access_token"]

@pytest.fixture(scope="module")
def token():
    return authenticate_test_user()

def test_create_movie(token):
    response = client.post(
        "/movies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Movie",
            "release_date": "2024-08-14",
            "genre": "Drama",
            "director": "John Doe",
            "synopsis": "A drama-packed movie.",
            "runtime": 150,
            "language": "English",
        }
    )
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Test Movie"

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
    # Create a movie to ensure there's data
    test_create_movie()

    response = client.get("/movies/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_movie():
    # Create a movie first
    test_create_movie()

    movie_id = 1
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"

def test_update_movie():
    # Create a movie first
    test_create_movie()

    # Authenticate the user
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
    # Create a movie first
    test_create_movie()

    # Authenticate the user
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
def test_rate_movie():
    # First, authenticate the user
    token = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    }).json()["access_token"]

    # Create a movie to rate
    client.post(
        "/movies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Movie for Rating",
            "release_date": "2024-08-14",
            "genre": "Drama",
            "director": "John Doe",
            "synopsis": "A drama-packed movie.",
            "runtime": 150,
            "language": "English",
        }
    )

    # Rate the movie
    response = client.post(
        "/movie/1/rate",
        headers={"Authorization": f"Bearer {token}"},
        json={"rating": 5}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5

def test_get_all_ratings():
    # Create a movie and rate it
    test_rate_movie()

    response = client.get("/movie/1/ratings")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["rating"] == 5

def test_create_comment():
    # First, authenticate the user
    token = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    }).json()["access_token"]

    # Create a movie to comment on
    client.post(
        "/movies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Movie for Comment",
            "release_date": "2024-08-14",
            "genre": "Comedy",
            "director": "Jane Smith",
            "synopsis": "A comedy-packed movie.",
            "runtime": 110,
            "language": "English",
        }
    )

    # Add a comment to the movie
    response = client.post(
        "/movie/1/comment",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content": "Great movie!",
            "parent_id": None
        }
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Great movie!"

def test_get_comments():
    # Create a comment
    test_create_comment()

    response = client.get("/movie/1/comments")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["content"] == "Great movie!"

def test_create_nested_comment():
    # First, authenticate the user
    token = client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    }).json()["access_token"]

    # Create a comment to nest under
    test_create_comment()

    # Add a nested comment to the existing comment
    response = client.post(
        "/movie/1/comment/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "I agree!"}
    )
    assert response.status_code == 200
    assert response.json()["content"] == "I agree!"

def test_get_nested_comments():
    # Create a nested comment
    test_create_nested_comment()

    response = client.get("/movie/1/comment/1")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["content"] == "I agree!"
