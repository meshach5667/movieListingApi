import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..main import app
from database.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.schemas import User, Movie, Comment, Rating
from jwt_token import create_access_token
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

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create a test user
@pytest.fixture
def test_user():
    user = User(username="test3", password="test3", email="test3@example.com", firstName="Test3", lastName="User3")
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Create a test movie
@pytest.fixture
def test_movie(test_user):
    movie = Movie(title="Test Movie", release_date="2022-01-01", genre="Action", director="Test Director", synopsis="Test synopsis", runtime=120, language="English")
    db = TestingSessionLocal()
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

# Create a test comment
@pytest.fixture
def test_comment(test_movie, test_user):
    comment = Comment(content="Test comment", movie_id=test_movie.id, user_id=test_user.id)
    db = TestingSessionLocal()
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

# Create a test rating
@pytest.fixture
def test_rating(test_movie, test_user):
    rating = Rating(rating=5, movie_id=test_movie.id, user_id=test_user.id)
    db = TestingSessionLocal()
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

# Test the create user endpoint
def test_create_user():
    response = client.post("/signup", json={"username": "test3", "password": "test3", "email": "test3@example.com", "firstName": "Test3", "lastName": "User3"})
    assert response.status_code == 201
    assert response.json()["username"] == "test3"

# Test the login endpoint
def test_login(test_user):
    response = client.post("/login", data={"username": test_user.username, "password": test_user.password})
    assert response.status_code == 200
    assert response.json()["access_token"]

# Test the create movie endpoint
def test_create_movie(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    response = client.post("/movies", json={"title": "Test Movie", "release_date": "2022-01-01", "genre": "Action", "director": "Test Director", "synopsis": "Test synopsis", "runtime": 120, "language": "English"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"

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
# def test_delete_movie(test_movie, test_user):
#     access_token = create_access_token(data={"sub": test_user.username})
#     response =