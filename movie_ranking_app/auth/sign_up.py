from fastapi import Request
from loguru import logger

from movie_ranking_app.auth.crypt_context import crypt_context
from movie_ranking_app.models.auth import NewUserInput, SignUpFormValidation, UserDataForm
from movie_ranking_app.models.db import User, UserInfo
from movie_ranking_app.sqlite import get_database_cursor, get_database_cursor_and_commit


async def load_sign_up_form_from_request(request: Request) -> UserDataForm:
    form = await request.form()
    return UserDataForm(
        username=form["username"],
        password=form["password"],
        adress=form["adress"],
        city=form["city"],
        country=form["country"],
    )


class UserInputValidator:
    def __init__(self, sing_up_form: UserDataForm) -> None:
        self.sign_up_form = sing_up_form
        self.sign_up_validation = SignUpFormValidation(
            valid_adress=True,
            valid_city=True,
            valid_country=True,
            valid_password=True,
            valid_username=True,
        )

    @staticmethod
    def detect_spaces(form: str | None) -> bool:
        if not form:
            return False
        elif " " in form:
            return True
        else:
            return False

    def check_if_no_spaces(self) -> None:
        fields_to_check = ["password", "username"]
        for field in fields_to_check:
            if self.detect_spaces(self.sign_up_form.dict()[field]):
                self.sign_up_validation.update_value(f"valid_{field}", False)

    def check_if_not_none(self) -> None:
        for key, value in self.sign_up_form.dict().items():
            if not value:
                self.sign_up_validation.update_value(f"valid_{key}", value)

    def check_if_user_exists(self) -> bool:
        query = """
                SELECT username
                FROM users
                WHERE username = :username;
                """
        query_params = {"username": self.sign_up_form.username}

        with get_database_cursor() as cursor:
            cursor.execute(query, query_params)
            result = cursor.fetchone()

            if result:
                return False
            else:
                return True

    def is_valid(self) -> bool:
        self.check_if_not_none()
        self.check_if_no_spaces()

        if self.sign_up_validation.valid and self.check_if_user_exists():
            return True
        else:
            return False

    def get_validation(self) -> SignUpFormValidation:
        return self.sign_up_validation

    def get_invalid_fields(self) -> list:
        return [
            field.split("_")[1]
            for field, bool_value in self.sign_up_validation.dict().items()
            if not bool_value
        ]


class UserCreator:
    USER_CREATE_QUERY = f"""
        --sql
        INSERT INTO users(username, password_hash)
        VALUES (:username, :password_hash)
        RETURNING id;
    """
    USER_INFO_CREATE_QUERY = """
        --sql
        INSERT INTO users_info(user_id, adress, city, country)
        VALUES (:user_id, :adress, :city, :country);
    """

    def __init__(self, sign_up_form: UserDataForm) -> None:
        self.sign_up_form = sign_up_form

    @staticmethod
    def crypt_password(password: str) -> str:
        return crypt_context.hash(password)

    def get_ready_user_with_hash(self) -> NewUserInput:
        return NewUserInput(
            username=self.sign_up_form.username,
            password_hash=self.crypt_password(self.sign_up_form.password),
        )

    def insert_user_data(self) -> None:
        with get_database_cursor_and_commit() as cursor:
            user = self.get_ready_user_with_hash()
            cursor.execute(self.USER_CREATE_QUERY, user.dict())

            user_id = cursor.fetchone()[0]
            user_info = UserInfo(user_id=user_id, **self.sign_up_form.dict())
            cursor.execute(self.USER_INFO_CREATE_QUERY, user_info.dict())
