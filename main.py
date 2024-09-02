from fastapi import FastAPI
from pymongo import MongoClient
from routers import auth, rating, movie, comments
from log import logger
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()


MONGO_DB_URL = os.getenv("MONGO_DB_URL")
client = MongoClient(MONGO_DB_URL)
db = client["movie_database"]  

app.state.db = db

# Include routers
app.include_router(auth.router)
app.include_router(rating.router)
app.include_router(movie.router)
app.include_router(comments.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

@app.get("/")
def index():
    logger.info("Received request to root endpoint")
    return {"message": "Movie listing API"}
