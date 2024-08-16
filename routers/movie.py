import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

import oauth2
from database.database import get_db
from schemas import schemas

logger = logging.getLogger("movies")

router = APIRouter(
    tags=["Movies"]
)

@router.post("/movies", response_model=schemas.MovieResponse)
async def create_movie_endpoint(
    request: schemas.Movie,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)  # Updated variable name
):
    logger.info("Received request to create a new movie")
    
    # Ensure the current_user object has an 'id' attribute
    if not hasattr(current_user, 'id'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User ID is missing")

    movie_data = request.dict()
    movie_data["user_id"] = str(current_user.id)
    
    result = await db["movies"].insert_one(movie_data)
    created_movie = await db["movies"].find_one({"_id": result.inserted_id})
    
    return schemas.MovieResponse(**created_movie)

@router.get("/movies", response_model=List[schemas.MovieResponse])
async def get_movies_endpoint(db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Received request to retrieve all movies")
    
    movies = await db["movies"].find().to_list(length=100)
    return [schemas.MovieResponse(**movie) for movie in movies]

@router.get("/movies/{movie_id}", response_model=schemas.MovieResponse)
async def get_movie_endpoint(movie_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to retrieve movie with id {movie_id}")
    
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    return schemas.MovieResponse(**movie)

@router.put("/movies/{movie_id}", response_model=schemas.MovieResponse)
async def update_movie_endpoint(
    movie_id: str,
    request: schemas.UpdateMovie,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)  # Updated variable name
):
    logger.info(f"Received request to update movie with id {movie_id}")
    
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    if str(movie["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this movie")

    update_data = request.dict(exclude_unset=True)
    await db["movies"].update_one({"_id": ObjectId(movie_id)}, {"$set": update_data})
    
    updated_movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    
    return schemas.MovieResponse(**updated_movie)

@router.delete("/movies/{movie_id}")
async def delete_movie_endpoint(
    movie_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)  # Updated variable name
):
    logger.info(f"Received request to delete movie with id {movie_id}")
    
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    if str(movie["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this movie")

    await db["movies"].delete_one({"_id": ObjectId(movie_id)})
    
    return {"detail": "Movie deleted successfully"}
