# oauth2.py
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import database
from schemas import schemas
from jwt_token import verify_token
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from database.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(database.database.get_db)) -> schemas.User:
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
    
    
    user_data = {
        "id": str(user["_id"]),  # Convert ObjectId to string
        **{key: user[key] for key in user if key != "_id"}  # Include other fields
    }
    
    # Create a Pydantic model instance
    return schemas.User(**user_data)
