from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas, database, models, oauth2

router = APIRouter(
    tags=["Ratings"]
)

get_db = database.get_db

@router.post("/movie/{movie_id}/rate", response_model=schemas.Rating)
def rate_movie(movie_id: int, request: schemas.Rating, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_rating = models.Rating(rating=request.rating, movie_id=movie_id, user_id=get_current_user.id)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@router.get("/movie/{movie_id}/ratings", response_model=List[schemas.Rating])
def get_all_ratings(movie_id: int, db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
    return ratings
