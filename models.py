from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    firstName = Column(String)
    lastName = Column(String)

    movies = relationship("Movie", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    release_date = Column(DateTime)
    genre = Column(String)
    director = Column(String)
    synopsis = Column(String)
    runtime = Column(Integer)
    language = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    movie = relationship("Movie", back_populates="ratings")
    user = relationship("User", back_populates="ratings")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    movie = relationship("Movie", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", back_populates="parent", remote_side=[id])
    parent = relationship("Comment", back_populates="replies")
