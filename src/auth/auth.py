from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.sqlite.models import User
from src.sqlite import get_database_cursor, dict_from_row
import datetime
from src.config import Settings
from jose import jwt, JWTError
from loguru import logger

def _verify_password(
    pwd_context: CryptContext, plain_password: str, hashed_password: str
) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _get_password_hash(pwd_context: CryptContext, password: str) -> str:
    return pwd_context.hash(password)


def _query_user(username: str) -> User | None:
    query = """
                SELECT  id, 
                        username, 
                        password
                FROM users
                WHERE username = :username ;
                """
    query_params = {"username": username}

    with get_database_cursor() as cursor:
        cursor.execute(query, query_params)
        result = cursor.fetchone()
        if not result:
            return None
        else:
            return User(**dict_from_row(cursor.fetchone()))


def authenticate_user(username: str, password: str) -> User | bool:
    user = _query_user(username)

    if not user:
        return False
    # TODO CHANGE PASSWORD TO HASHED PASSWORD IN DB

    if not _verify_password(password, user.password):
        return False

    return user


def create_access_token(
    data: dict, expires_delta: datetime.timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(
            token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM]
        )
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        
    except JWTError as e:
        logger.info(e)
        raise credentials_exception

    user = _query_user(username)
    return user


