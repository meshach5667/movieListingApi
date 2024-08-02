from datetime import datetime, timedelta, timezone
from typing import Union
from jose import JWTError
import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
from jwt.exceptions import InvalidTokenError
from schemas import TokenData
from dotenv import load_dotenv
import os


load_dotenv()


class TokenData(BaseModel):
    id: int
    username: str

    



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print("Decoded payload:", payload)  # Debugging line
        id = payload.get("id")
        username = payload.get("sub")
        if id is None or username is None:
            raise credentials_exception
        return TokenData(id=id, username=username)
    except jwt.PyJWTError:
        raise credentials_exception