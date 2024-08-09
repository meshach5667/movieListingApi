from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from auth.jwt_token import SECRET_KEY, verify_token
from schemas.schemas import TokenData
import models.models as models
import database.database as database
from sqlalchemy.orm import Session
import auth.jwt_token as jwt_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == int(token_data.id)).first()
    if user is None:
        raise credentials_exception
    return user