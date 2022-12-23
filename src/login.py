from fastapi import HTTPException, Request, status
from pydantic import BaseModel

from src.sqlite.models import User
from src.sqlite import dict_from_row, get_database_cursor


class WrongCredentialException(Exception):
    "Wrong credentials!"


class RequestUser(BaseModel):
    username: str
    password: str


class Authenticator:
    def __init__(self) -> None:
        self.request_user: RequestUser | None = None

    def load_request(self, request: Request):
        request_user = RequestUser(**request)
        # self.user_input_validator.validate(request_user=request_user)
        self.request_user = request_user

    def _query_user_credentials(self, username: str) -> User:
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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return User(**dict_from_row(cursor.fetchone()))

    def validate_user(self) -> None:
        true_credentials = self._query_user_credentials(
            username=self.request_user.username
        )

        if not self.request_user.password == true_credentials.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
