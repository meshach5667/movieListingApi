from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from schemas import schemas
from schemas.schemas import UpdateMovie  # Pydantic model
from oauth2 import get_current_user

async def create_movie(request: schemas.Movie, db: AsyncIOMotorDatabase, get_current_user: schemas.User):
    new_movie = {
        "title": request.title,
        "release_date": request.release_date,
        "genre": request.genre,
        "director": request.director,
        "synopsis": request.synopsis,
        "runtime": request.runtime,
        "language": request.language,
        "user_id": str(get_current_user.id)
    }

    result = await db["movies"].insert_one(new_movie)
    created_movie = await db["movies"].find_one({"_id": result.inserted_id})
    return schemas.MovieResponse(**created_movie)

async def get_movies(db: AsyncIOMotorDatabase):
    movies = await db["movies"].find().to_list(length=100)
    return [schemas.MovieResponse(**movie) for movie in movies]

async def get_movie(movie_id: str, db: AsyncIOMotorDatabase):
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return schemas.MovieResponse(**movie)

async def update_movie(movie_id: str, request: UpdateMovie, db: AsyncIOMotorDatabase, get_current_user: schemas.User):
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie["user_id"] != str(get_current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this movie")

    update_data = request.dict(exclude_unset=True)
    await db["movies"].update_one({"_id": ObjectId(movie_id)}, {"$set": update_data})
    updated_movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    return schemas.MovieResponse(**updated_movie)

async def delete_movie(movie_id: str, db: AsyncIOMotorDatabase, get_current_user: schemas.User):
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie["user_id"] != str(get_current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this movie")

    await db["movies"].delete_one({"_id": ObjectId(movie_id)})
    return {"message": "Movie deleted successfully"}
