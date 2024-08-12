import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jwt_token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token 
import schemas.schemas as schemas, database.database as database
from hashing import Hash
import models.models as models
import jwt_token as jwt_token

logger = logging.getLogger("auth")

router = APIRouter(
    tags=["Auth"]
)

get_db = database.get_db

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
    logger.info("Received request to create a new user")
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
    logger.info("User created successfully")
    return new_user

@router.get("/user/{id}", response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to retrieve user with id {id}")
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:    
        logger.warning(f"User with id {id} does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    logger.info(f"User with id {id} retrieved successfully")
    return user
@router.post("/login", response_model=schemas.Token)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Received request to login with username {request.username}")
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        logger.warning(f"User with username {request.username} does not exist")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not Hash.verify(user.password, request.password):
        logger.warning(f"Incorrect password for user with username {request.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    logger.info(f"Login successful for user with username {request.username}")
    return schemas.Token(access_token=access_token, token_type="bearer")