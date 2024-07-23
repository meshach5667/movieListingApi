from datetime import timedelta
from fastapi import APIRouter, Depends, Form,HTTPException,status,Response
import schemas,database
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models, schemas
from typing import Annotated, List
import oauth2

router = APIRouter(
    tags=["Comments"]
    
)

get_db = database.get_db


@router.post("/movie/{movie_id}/comment", response_model=schemas.CommentResponse)
def add_comment(movie_id: int, request: schemas.Comment, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_comment = models.Comment(content=request.content, movie_id=movie_id, user_id=get_current_user.id, parent_id=request.parent_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get("/movie/{movie_id}/comments", response_model=List[schemas.CommentResponse])
def get_comments(movie_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.movie_id == movie_id, models.Comment.parent_id == None).all()
    return comments


@router.get("/comment/{comment_id}/replies", response_model=List[schemas.CommentResponse])
def get_replies(comment_id: int, db: Session = Depends(get_db)):
    replies = db.query(models.Comment).filter(models.Comment.parent_id == comment_id).all()
    return replies

