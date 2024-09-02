from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from schemas import schemas
from schemas.schemas import UpdateMovie
from oauth2 import get_current_user

router = APIRouter()

@router.post("/movies", response_model=schemas.MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    request: schemas.Movie, 
    db: AsyncIOMotorDatabase = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    new_movie = {
        "title": request.title,
        "release_date": request.release_date,
        "genre": request.genre,
        "director": request.director,
        "synopsis": request.synopsis,
        "runtime": request.runtime,
        "language": request.language,
        "user_id": str(current_user.id)  # Ensure the current_user object has an id attribute
    }

    result = await db["movies"].insert_one(new_movie)
    created_movie = await db["movies"].find_one({"_id": result.inserted_id})
    return schemas.MovieResponse(**created_movie)

@router.get("/movies", response_model=List[schemas.MovieResponse])
async def get_movies(db: AsyncIOMotorDatabase = Depends(get_db)):
    movies = await db["movies"].find().to_list(length=100)
    return [schemas.MovieResponse(**movie) for movie in movies]

@router.get("/movies/{movie_id}", response_model=schemas.MovieResponse)
async def get_movie(movie_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return schemas.MovieResponse(**movie)

@router.put("/movies/{movie_id}", response_model=schemas.MovieResponse)
async def update_movie(
    movie_id: str, 
    request: UpdateMovie, 
    db: AsyncIOMotorDatabase = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie["user_id"] != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this movie")

    update_data = request.dict(exclude_unset=True)
    await db["movies"].update_one({"_id": ObjectId(movie_id)}, {"$set": update_data})
    updated_movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    return schemas.MovieResponse(**updated_movie)

@router.delete("/movies/{movie_id}", response_model=dict)
async def delete_movie(
    movie_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie["user_id"] != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this movie")

    await db["movies"].delete_one({"_id": ObjectId(movie_id)})
    return {"message": "Movie deleted successfully"}
