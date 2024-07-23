from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException,status
from jwt_token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token 
import schemas,database
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from hashing import Hash
import models, schemas, hashing

router = APIRouter(
    tags=["Auth"]
    
)

get_db = database.get_db

@router.post("/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
   
    new_user = models.User(
        username=request.username,
        password=Hash.bcrypt(request.password),
        email=request.email,
        firstName=request.firstName,
        lastName=request.lastName
    )


   
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/user/{id}",response_model=schemas.User)
def get_user(id:int,  db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,details ="User dose not exist")  
    return user



@router.post("/login", response_model=schemas.Token)
def login(request:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not hashing.Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}