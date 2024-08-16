import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from jwt_token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token 
import schemas.schemas as schemas
from hashing import Hash
from bson import ObjectId

logger = logging.getLogger("auth")

router = APIRouter(
    tags=["Auth"]
)

# Dependency to get the MongoDB database
def get_db() -> AsyncIOMotorDatabase:
    from database.database import get_db
    return get_db()

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: schemas.User, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Received request to create a new user")
    
    existing_user = await db["users"].find_one({"username": request.username})
    if existing_user:
        logger.warning(f"Username {request.username} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    hashed_password = Hash.bcrypt(request.password)
    
    new_user = {
        "username": request.username,
        "password": hashed_password,
        "email": request.email,
        "firstName": request.firstName,
        "lastName": request.lastName,
        "movies": [],
        "ratings": [],
        "comments": []
    }
    
    result = await db["users"].insert_one(new_user)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    
    logger.info("User created successfully")
    return schemas.UserResponse(**created_user)

@router.get("/user/{id}", response_model=schemas.User)
async def get_user(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to retrieve user with id {id}")
    
    user = await db["users"].find_one({"_id": ObjectId(id)})
    if not user:    
        logger.warning(f"User with id {id} does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    logger.info(f"User with id {id} retrieved successfully")
    return schemas.User(**user)

@router.post("/login", response_model=schemas.Token)
async def login(request: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Received request to login with username {request.username}")
    
    user = await db["users"].find_one({"username": request.username})
    if not user:
        logger.warning(f"User with username {request.username} does not exist")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    if not Hash.verify(user["password"], request.password):
        logger.warning(f"Incorrect password for user with username {request.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful for user with username {request.username}")
    return schemas.Token(access_token=access_token, token_type="bearer")
