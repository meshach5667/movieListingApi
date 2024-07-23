from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from hashing import Hash
import models, schemas, hashing
from database import engine, get_db
from routers import users, movie, ratings,comments

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(movie.router)
app.include_router(ratings.router)
app.include_router(comments.router)



@app.get("/")
def index():
    return {"message":"Movie listing API"}




