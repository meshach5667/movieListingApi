from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    username: str
    password: str
    email: str
    firstName: str
    lastName: str

class UserResponse(BaseModel):
    id: int
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
    id: str

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
        from_attributes = True  # Ensures `from_orm` works

class MovieResponse(BaseModel):
    id: int
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
    movie_id: int
    
    class Config:
        orm_mode = True

class Comment(BaseModel):
    content: str
    movie_id: int
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    content: str
    movie_id: int
    user_id: int
    
    class Config:
        orm_mode = True

CommentResponse.update_forward_refs()
