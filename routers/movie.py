import logging
from typing import List
from fastapi import APIRouter, Depends, status
import oauth2
from crud.movies import create_movie, get_movies, get_movie, update_movie, delete_movie
from sqlalchemy.orm import Session
from database.database import get_db
from schemas import schemas

logger = logging.getLogger("movies")

router = APIRouter(
    tags=["Movies"]
)

@router.post("/movies", response_model=schemas.Movie)
def create_movie_endpoint(request: schemas.Movie, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info("Received request to create a new movie")
    return create_movie(request, db, get_current_user)

@router.get("/movies", response_model=List[schemas.MovieResponse])
def get_movies_endpoint(db: Session = Depends(get_db)):
    logger.info("Received request to retrieve all movies")
    return get_movies(db)

@router.get("/movies/{movie_id}", response_model=schemas.MovieResponse)
def get_movie_endpoint(movie_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to retrieve movie with id {movie_id}")
    return get_movie(movie_id, db)

@router.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie_endpoint(movie_id: int, request: schemas.UpdateMovie, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to update movie with id {movie_id}")
    return update_movie(movie_id, request, db, get_current_user)

@router.delete("/movies/{movie_id}")
def delete_movie_endpoint(movie_id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to delete movie with id {movie_id}")
    return delete_movie(movie_id, db, get_current_user)