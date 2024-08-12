from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session
from models.models import Movie  # SQLAlchemy model
from schemas import schemas
from schemas.schemas import UpdateMovie  # Pydantic model
from oauth2 import get_current_user
from database.database import get_db

def create_movie(request: schemas.Movie, db: Session, get_current_user: schemas.User):
    new_movie = Movie(
        title=request.title,
        release_date=request.release_date,
        genre=request.genre,
        director=request.director,
        synopsis=request.synopsis,
        runtime=request.runtime,
        language=request.language,
        user_id=get_current_user.id  
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

def get_movies(db: Session):
    movies = db.query(Movie).all()
    return movies

def get_movie(movie_id: int, db: Session):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

def update_movie(movie_id: int, request: UpdateMovie, db: Session, get_current_user: schemas.User):
    movie_query = db.query(Movie).filter(Movie.id == movie_id)
    movie = movie_query.first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this movie")

    movie_query.update(request.dict(), synchronize_session=False)
    db.commit()
    return movie_query.first()

def delete_movie(movie_id: int, db: Session, get_current_user: schemas.User):
    movie_query = db.query(Movie).filter(Movie.id == movie_id)
    movie = movie_query.first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this movie")

    movie_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
