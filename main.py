from fastapi import FastAPI
import models.models as models
from database.database import engine
from routers import auth, rating, movie, comments
from log import logger

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

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