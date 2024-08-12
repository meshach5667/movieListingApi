import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import schemas.schemas as schemas, database.database as database, models.models as models, oauth2 as oauth2

logger = logging.getLogger("comments")

router = APIRouter(
    tags=["Comments"]
)

get_db = database.get_db

@router.post("/movie/{movie_id}/comment", response_model=schemas.CommentResponse)
def create_comment(movie_id: int, request: schemas.Comment, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to create a new comment for movie with id {movie_id}")
   
    request_data = request.dict(exclude={"movie_id"})
    
    new_comment = models.Comment(**request_data, user_id=get_current_user.id, movie_id=movie_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    logger.info(f"Comment created successfully for movie with id {movie_id}")
    return new_comment

@router.get("/movie/{movie_id}/comments", response_model=List[schemas.CommentResponse])
def get_comments(movie_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to retrieve comments for movie with id {movie_id}")
    comments = db.query(models.Comment).filter(models.Comment.movie_id == movie_id, models.Comment.parent_id == None).all()
    if not comments:
        logger.info(f"No comments found for movie with id {movie_id}")
        return [] 
    logger.info(f"Comments retrieved successfully for movie with id {movie_id}")
    return comments

@router.post("/movie/{movie_id}/comment/{parent_id}", response_model=schemas.CommentResponse)
def create_nested_comment(movie_id: int, parent_id: int, request: schemas.Comment, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to create a new nested comment for movie with id {movie_id} and parent comment with id {parent_id}")
    
  
    request_data = request.dict(exclude={"movie_id", "parent_id"})
    
    new_comment = models.Comment(**request_data, user_id=get_current_user.id, movie_id=movie_id, parent_id=parent_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    logger.info(f"Nested comment created successfully for movie with id {movie_id} and parent comment with id {parent_id}")
    return new_comment

@router.get("/movie/{movie_id}/comment/{parent_id}", response_model=List[schemas.CommentResponse])
def get_nested_comments(movie_id: int, parent_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to retrieve nested comments for movie with id {movie_id} and parent comment with id {parent_id}")
    comments = db.query(models.Comment).filter(models.Comment.movie_id == movie_id, models.Comment.parent_id == parent_id).all()
    if not comments:
        logger.info(f"No nested comments found for movie with id {movie_id} and parent comment with id {parent_id}")
        return [] 
    logger.info(f"Nested comments retrieved successfully for movie with id {movie_id} and parent comment with id {parent_id}")
    return comments
