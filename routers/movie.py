from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import schemas, database, models, oauth2

router = APIRouter(
    tags=["Movies"]
)

get_db = database.get_db

@router.post("/movies", response_model=schemas.Movie)
def create_movie(request: schemas.Movie, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_movie = models.Movie(
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

@router.get("/movies", response_model=List[schemas.Movie])
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(models.Movie).all()
    return movies

@router.get("/movies/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

@router.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, request: schemas.UpdateMovie, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    movie_query = db.query(models.Movie).filter(models.Movie.id == movie_id)
    movie = movie_query.first()

    if movie.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this movie")

    movie_query.update(request.dict())
    db.commit()
    return movie_query.first()

@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    movie_query = db.query(models.Movie).filter(models.Movie.id == movie_id)
    movie = movie_query.first()

    if movie.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this movie")

    movie_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)