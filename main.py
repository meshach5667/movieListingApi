from fastapi import FastAPI
import models.models as models
from database.database import engine
from routers import auth, rating, movie, comments

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(rating.router)
app.include_router(movie.router)
app.include_router(comments.router)




@app.get("/")
def index():
    return {"message":"Movie listing API"}




