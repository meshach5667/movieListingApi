from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt_token import SECRET_KEY, verify_token
from schemas import schemas
from schemas.schemas import TokenData
import models.models as models  # Ensure this file contains Pydantic models
import database.database as database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token and extract token data
    token_data = verify_token(token, credentials_exception)
    
    # Query MongoDB using Motor
    user = await db["users"].find_one({"_id": ObjectId(token_data.id)})
    
    if user is None:
        raise credentials_exception
    
    # Assuming User is a Pydantic model that matches the schema of the user document
    return schemas.User(**user)
