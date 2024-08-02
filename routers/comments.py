from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import schemas, database, models, oauth2

router = APIRouter(
    tags=["Comments"]
)

get_db = database.get_db

@router.post("/movie/{movie_id}/comment", response_model=schemas.CommentResponse)
def create_comment(movie_id: int, request: schemas.Comment, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_comment = models.Comment(**request.dict(), movie_id=movie_id, user_id=get_current_user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/movie/{movie_id}/comments", response_model=List[schemas.CommentResponse])
def get_comments(movie_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.movie_id == movie_id).all()
    return comments
