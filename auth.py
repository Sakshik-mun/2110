import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models import User

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 8
pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(p: str) -> str:
    return pwd.hash(p)


def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)


def create_token(user_id: int) -> str:
    exp = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    try:
        uid = int(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"])
    except (JWTError, KeyError, ValueError):
        raise err
    user = db.get(User, uid)
    if not user:
        raise err
    return user
