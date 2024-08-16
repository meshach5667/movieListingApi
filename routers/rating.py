import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from database.database import get_db
from schemas import schemas
from bson import ObjectId
import oauth2

logger = logging.getLogger("ratings")

router = APIRouter(
    tags=["Ratings"]
)

# Dependency to get the MongoDB database
def get_db() -> AsyncIOMotorDatabase:
    from database.database import get_db
    return get_db()

@router.post("/movie/{movie_id}/rate", response_model=schemas.Rating)
async def rate_movie(movie_id: str, request: schemas.Rating, db: AsyncIOMotorDatabase = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    logger.info(f"Received request to rate movie with id {movie_id}")
    
    # Create a new rating
    new_rating = {
        "rating": request.rating,
        "movie_id": movie_id,
        "user_id": str(get_current_user.id)
    }
    
    result = await db["ratings"].insert_one(new_rating)
    created_rating = await db["ratings"].find_one({"_id": result.inserted_id})
    
    logger.info(f"Rating created successfully for movie with id {movie_id}")
    return schemas.Rating(**created_rating)

@router.get("/movie/{movie_id}/ratings", response_model=List[schemas.Rating])
async def get_all_ratings(movie_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to retrieve ratings for movie with id {movie_id}")
    
    ratings = await db["ratings"].find({"movie_id": movie_id}).to_list(length=100)
    
    if not ratings:
        logger.info(f"No ratings found for movie with id {movie_id}")
    else:
        logger.info(f"Ratings retrieved successfully for movie with id {movie_id}")
    
    return [schemas.RatingResponse(**rating) for rating in ratings]
