from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId 

class User(BaseModel):
    id:str
    username: str
    password: str
    email: str
    firstName: str
    lastName: str

    class Config:
        orm_mode = True  

class UserResponse(BaseModel):
    id: str  
    username: str
    password: str

    class Config:
        orm_mode = True

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: str  # Changed to str to match MongoDB ObjectId type

class Movie(BaseModel):
    title: str
    release_date: datetime
    genre: str
    director: str
    synopsis: Optional[str] = None
    runtime: Optional[int] = None
    language: Optional[str] = None
    
    class Config:
        orm_mode = True

class MovieResponse(BaseModel):
    id: str  # Changed to str to match MongoDB ObjectId type
    title: str
    genre: str
    synopsis: str
    language: str
    release_date: datetime
    
    class Config:
        orm_mode = True

class UpdateMovie(Movie):
    pass

class Rating(BaseModel):
    rating: float
    movie_id: str  # Changed to str to match MongoDB ObjectId type
    
    class Config:
        orm_mode = True

class Comment(BaseModel):
    content: str
    movie_id: str  # Changed to str to match MongoDB ObjectId type
    parent_id: Optional[str] = None  # Changed to str to match MongoDB ObjectId type

class CommentResponse(BaseModel):
    id: str  
    content: str
    movie_id: str  
    user_id: str
    class Config:
        orm_mode = True

CommentResponse.update_forward_refs()
