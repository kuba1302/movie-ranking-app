from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from loguru import logger

from src.auth.crypt_context import crypt_context
from src.config import settings
from src.models.auth import UserForm, UserFormValidation
from src.models.db import User
from src.sqlite import dict_from_row, get_database_cursor

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return crypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return crypt_context.hash(password)


def _query_user(username: str) -> User | None:
    query = """
                SELECT  id, 
                        username, 
                        password_hash
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
            return User(**dict_from_row(result))


def authenticate_user(user_form: UserForm) -> User:
    user = _query_user(user_form.username)
    if not user:
        raise credentials_exception

    if not _verify_password(user_form.password, user.password_hash):
        raise credentials_exception

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> str:
    if not token:
        raise credentials_exception

    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception

    except JWTError as e:
        logger.info(e)
        raise credentials_exception

    user = _query_user(username)
    return user


def get_user_from_cookie(request: Request) -> User:
    token = request.cookies.get(settings.COOKIE_NAME)
    return decode_token(token)


async def load_data_from_request(request: Request) -> UserForm:
    form = await request.form()
    return UserForm(username=form.get("username"), password=form.get("password"))


def validate_user_form(user_form: UserForm) -> UserFormValidation:
    return UserFormValidation(
        valid_username=True if user_form.username else False,
        valid_password=True if user_form.password else False,
    )
