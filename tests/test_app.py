import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from datetime import datetime
from ..main import app
from schemas.schemas import User, Movie, Comment, Rating
from jwt_token import create_access_token
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB test database setup
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
client = MongoClient(MONGO_DB_URL)
db = client["test_database"]

# Create a test client
test_client = TestClient(app)

# Override the database dependency with test database
def override_get_db():
    try:
        yield db
    finally:
        # No need to close MongoDB client explicitly
        pass

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # Drop collections before each test
    db.users.drop()
    db.movies.drop()
    db.ratings.drop()
    db.comments.drop()
    yield
    # Drop collections after each test
    db.users.drop()
    db.movies.drop()
    db.ratings.drop()
    db.comments.drop()

def authenticate_test_user():
    response = test_client.post(
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

def test_signup():
    response = test_client.post("/signup", json={
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
    test_client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    response = test_client.get("/user/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login():
    test_client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    response = test_client.post("/login", data={
        "username": "testuser",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_password():
    # First create a user
    test_client.post("/signup", json={
        "username": "testuser",
        "password": "password123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User"
    })
    response = test_client.post("/login", data={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

def test_create_movie(token):
    response = test_client.post(
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

def test_get_movies():
    # Create a movie to ensure there's data
    test_create_movie(token)

    response = test_client.get("/movies/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_movie():
    # Create a movie first
    test_create_movie(token)

    movie_id = "1"  # Replace with dynamic ID retrieval if necessary
    response = test_client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"

def test_update_movie():
    # Create a movie first
    test_create_movie(token)

    movie_id = "1"  # Replace with dynamic ID retrieval if necessary
    response = test_client.put(
        f"/movies/{movie_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Movie Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Movie Title"

def test_delete_movie():
    # Create a movie first
    test_create_movie(token)

    movie_id = "1"  # Replace with dynamic ID retrieval if necessary
    response = test_client.delete(
        f"/movies/{movie_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Movie deleted successfully"}

    # Check if the movie is really deleted
    response = test_client.get(f"/movies/{movie_id}")
    assert response.status_code == 404

def test_rate_movie():
    # First, authenticate the user
    token = authenticate_test_user()

    # Create a movie to rate
    test_client.post(
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
    response = test_client.post(
        "/movie/1/rate",
        headers={"Authorization": f"Bearer {token}"},
        json={"rating": 5}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5

def test_get_all_ratings():
    # Create a movie and rate it
    test_rate_movie()

    response = test_client.get("/movie/1/ratings")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["rating"] == 5

def test_create_comment():
    # First, authenticate the user
    token = authenticate_test_user()

    # Create a movie to comment on
    test_client.post(
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
    response = test_client.post(
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

    response = test_client.get("/movie/1/comments")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["content"] == "Great movie!"

def test_create_nested_comment():
    # First, authenticate the user
    token = authenticate_test_user()

    # Create a comment to nest under
    test_create_comment()

    # Add a nested comment to the existing comment
    response = test_client.post(
        "/movie/1/comment/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "I agree!"}
    )
    assert response.status_code == 200
    assert response.json()["content"] == "I agree!"
