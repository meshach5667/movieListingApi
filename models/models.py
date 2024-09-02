from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

# Custom Pydantic Field for MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# Base Pydantic model with common attributes
class MongoModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

# User model
class User(MongoModel):
    username: str
    password: str
    email: EmailStr
    firstName: str
    lastName: str
    movies: Optional[List[str]] = []  
    comments: Optional[List[str]] = []

# Movie model
class Movie(MongoModel):
    title: str
    release_date: Optional[datetime]
    genre: Optional[str]
    director: Optional[str]
    synopsis: Optional[str]
    runtime: Optional[int]
    language: Optional[str]
    user_id: str  
    ratings: Optional[List[str]] = []  
    comments: Optional[List[str]] = [] 

# Rating model
class Rating(MongoModel):
    rating: float
    movie_id: str  
    user_id: str  

# Comment model
class Comment(MongoModel):
    content: str
    movie_id: str 
    user_id: str  
    parent_id: Optional[str] = None 
    replies: Optional[List[str]] = []  
