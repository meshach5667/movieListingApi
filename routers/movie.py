# routers/movie.py
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from bson import ObjectId
import logging
from schemas import schemas
from oauth2 import get_current_user
from database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("movies")

router = APIRouter(tags=["Movies"])

@router.post("/movies", response_model=schemas.MovieResponse)
async def create_movie_endpoint(
    request: schemas.Movie,
    db: AsyncIOMotorDatabase = Depends(get_db),
    get_current_user: schemas.User = Depends(get_current_user)
):
    logger.info("Received request to create a new movie")
    movie_data = request.dict()
    movie_data["user_id"] = str(get_current_user.id)
    
    result = await db["movies"].insert_one(movie_data)
    created_movie = await db["movies"].find_one({"_id": result.inserted_id})
    
    # Convert MongoDB _id to id and map the movie fields
    movie_data = {
        "id": str(created_movie["_id"]),  # Convert ObjectId to string
        **{key: created_movie[key] for key in created_movie if key != "_id"}  # Include other fields
    }
    
    return schemas.MovieResponse(**movie_data)

@router.get("/movies", response_model=List[schemas.MovieResponse])
async def get_movies_endpoint(db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Received request to retrieve all movies")
    movies = await db["movies"].find().to_list(length=100)
    
    # Convert MongoDB _id to id for each movie
    movie_list = [
        schemas.MovieResponse(
            id=str(movie["_id"]),
            **{key: movie[key] for key in movie if key != "_id"}
        ) for movie in movies
    ]
    return movie_list

@router.get("/movies/{movie_id}", response_model=schemas.MovieResponse)
async def get_movie_endpoint(movie_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to retrieve movie with id {movie_id}")
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    return schemas.MovieResponse(
        id=str(movie["_id"]),
        **{key: movie[key] for key in movie if key != "_id"}
    )

@router.put("/movies/{movie_id}", response_model=schemas.MovieResponse)
async def update_movie_endpoint(
    movie_id: str,
    request: schemas.UpdateMovie,
    db: AsyncIOMotorDatabase = Depends(get_db),
    get_current_user: schemas.User = Depends(get_current_user)
):
    logger.info(f"Received request to update movie with id {movie_id}")
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    if str(movie["user_id"]) != str(get_current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this movie")
    
    update_data = request.dict(exclude_unset=True)
    await db["movies"].update_one({"_id": ObjectId(movie_id)}, {"$set": update_data})
    
    updated_movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    return schemas.MovieResponse(
        id=str(updated_movie["_id"]),
        **{key: updated_movie[key] for key in updated_movie if key != "_id"}
    )

@router.delete("/movies/{movie_id}")
async def delete_movie_endpoint(
    movie_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    get_current_user: schemas.User = Depends(get_current_user)
):
    logger.info(f"Received request to delete movie with id {movie_id}")
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    if str(movie["user_id"]) != str(get_current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this movie")
    
    await db["movies"].delete_one({"_id": ObjectId(movie_id)})
    return {"detail": "Movie deleted successfully"}
