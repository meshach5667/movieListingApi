import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import schemas.schemas as schemas, oauth2 as oauth2
from bson import ObjectId

logger = logging.getLogger("comments")

router = APIRouter(
    tags=["Comments"]
)

# Dependency to get the MongoDB database
def get_db() -> AsyncIOMotorDatabase:
    from database.database import get_db
    return get_db()

@router.post("/movie/{movie_id}/comment", response_model=schemas.CommentResponse)
async def create_comment(movie_id: str, request: schemas.Comment, db: AsyncIOMotorDatabase = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to create a new comment for movie with id {movie_id}")
   
    request_data = request.dict(exclude={"movie_id"})
    
    new_comment = {
        **request_data,
        "user_id": str(get_current_user.id),
        "movie_id": movie_id,
        "parent_id": None
    }
    
    result = await db["comments"].insert_one(new_comment)
    created_comment = await db["comments"].find_one({"_id": result.inserted_id})
    
    logger.info(f"Comment created successfully for movie with id {movie_id}")
    return schemas.CommentResponse(**created_comment)

@router.get("/movie/{movie_id}/comments", response_model=List[schemas.CommentResponse])
async def get_comments(movie_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to retrieve comments for movie with id {movie_id}")
    comments = await db["comments"].find({"movie_id": movie_id, "parent_id": None}).to_list(length=100)
    
    if not comments:
        logger.info(f"No comments found for movie with id {movie_id}")
        return [] 
    
    logger.info(f"Comments retrieved successfully for movie with id {movie_id}")
    return [schemas.CommentResponse(**comment) for comment in comments]

@router.post("/movie/{movie_id}/comment/{parent_id}", response_model=schemas.CommentResponse)
async def create_nested_comment(movie_id: str, parent_id: str, request: schemas.Comment, db: AsyncIOMotorDatabase = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to create a new nested comment for movie with id {movie_id} and parent comment with id {parent_id}")
    
    request_data = request.dict(exclude={"movie_id", "parent_id"})
    
    new_comment = {
        **request_data,
        "user_id": str(get_current_user.id),
        "movie_id": movie_id,
        "parent_id": parent_id
    }
    
    result = await db["comments"].insert_one(new_comment)
    created_comment = await db["comments"].find_one({"_id": result.inserted_id})
    
    logger.info(f"Nested comment created successfully for movie with id {movie_id} and parent comment with id {parent_id}")
    return schemas.CommentResponse(**created_comment)

@router.get("/movie/{movie_id}/comment/{parent_id}", response_model=List[schemas.CommentResponse])
async def get_nested_comments(movie_id: str, parent_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to retrieve nested comments for movie with id {movie_id} and parent comment with id {parent_id}")
    comments = await db["comments"].find({"movie_id": movie_id, "parent_id": parent_id}).to_list(length=100)
    
    if not comments:
        logger.info(f"No nested comments found for movie with id {movie_id} and parent comment with id {parent_id}")
        return [] 
    
    logger.info(f"Nested comments retrieved successfully for movie with id {movie_id} and parent comment with id {parent_id}")
    return [schemas.CommentResponse(**comment) for comment in comments]
