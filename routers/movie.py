from datetime import timedelta
from fastapi import APIRouter, Depends, Form,HTTPException,status,Response
import schemas,database
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models, schemas
from typing import Annotated
import oauth2

router = APIRouter(
    tags=["Movies"]
    
)

get_db = database.get_db


@router.post("/movie", status_code=status.HTTP_201_CREATED, response_model=schemas.Movie)
def list_movie(request: schemas.Movie, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_movie = models.Movie(
        title=request.title,
        release_date=request.release_date,
        genre=request.genre,
        director=request.director,
        synopsis=request.synopsis,
        rating=request.rating,
        runtime=request.runtime,
        language=request.language,
        user_id=get_current_user
    )

    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie



@router.get("/movie",status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
 
    return movies


@router.get("/movie/{id}")
def get(id:int, db:Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == id).first()

    if not  movie:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Movie not found")
    
    return movie

@router.put("/movie/{id}", response_model=schemas.Movie)
def update_movie(id: int, request: schemas.UpdateMovie, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    movie = db.query(models.Movie).filter(models.Movie.id == id).first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this movie")

    movie.title = request.title
    movie.release_date = request.release_date
    movie.genre = request.genre
    movie.director = request.director
    movie.synopsis = request.synopsis
    movie.rating = request.rating
    movie.runtime = request.runtime
    movie.language = request.language

    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/movie/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    movie = db.query(models.Movie).filter(models.Movie.id == id).first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie.user_id != get_current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this movie")

    db.delete(movie)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
