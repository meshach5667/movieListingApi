from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt_token import SECRET_KEY, verify_token
from schemas import TokenData
import models
import database
from sqlalchemy.orm import Session
import jwt_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token:str= Depends(oauth2_scheme),db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = verify_token(token, credentials_exception)

   
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    return user