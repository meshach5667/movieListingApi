import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..main import app
from database.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.schemas import User, Movie, Comment, Rating
from oauth2 import create_access_token
from dotenv import load_dotenv
import os

# Create a test database


load_dotenv()


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

# Create a test user
@pytest.fixture
def test_user():
    user = User(username="testuser", password="testpassword", email="testuser@example.com", firstName="Test", lastName="User")
    return user

# Create a test movie
@pytest.fixture
def test_movie():
    movie = Movie(title="Test Movie", release_date="2022-01-01", genre="Action", director="Test Director", synopsis="Test synopsis", runtime=120, language="English")
    return movie

# Create a test comment
@pytest.fixture
def test_comment():
    comment = Comment(content="Test comment")
    return comment

# Create a test rating
@pytest.fixture
def test_rating():
    rating = Rating(rating=5)
    return rating

# Test the create user endpoint
def test_create_user(test_user):
    response = client.post("/signup", json=test_user.dict())
    assert response.status_code == 201
    assert response.json()["username"] == test_user.username

# Test the login endpoint
def test_login(test_user):
    response = client.post("/login", data={"username": test_user.username, "password": test_user.password})
    assert response.status_code == 200
    assert response.json()["access_token"]

# Test the create movie endpoint
def test_create_movie(test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.post("/movies", json=test_movie.dict(), headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["title"] == test_movie.title

# Test the get movies endpoint
def test_get_movies(test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.get("/movies", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

# Test the get movie endpoint
def test_get_movie(test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.get(f"/movies/{test_movie.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["title"] == test_movie.title

# Test the update movie endpoint
def test_update_movie(test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.put(f"/movies/{test_movie.id}", json={"title": "Updated title"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"

# Test the delete movie endpoint
def test_delete_movie(test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.delete(f"/movies/{test_movie.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204

# Test the create comment endpoint
def test_create_comment(test_comment, test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.post(f"/movie/{test_movie.id}/comment", json=test_comment.dict(), headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["content"] == test_comment.content

# Test the get comments endpoint
def test_get_comments(test_comment, test_movie, test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.get(f"/movie/{test_movie.id}/comments", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0
