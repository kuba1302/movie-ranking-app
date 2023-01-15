from fastapi import Request

from src.auth.crypt_context import crypt_context
from src.models.auth import UserChangeDataForm, UserUpdateInfo
from src.sqlite.db_connection import get_database_cursor_and_commit

UPDATE_USER = """
    UPDATE users
    SET password_hash = :password_hash
    WHERE username = :username;
"""


async def load_update_form_from_request(
    request: Request, username: str
) -> UserChangeDataForm:
    form = await request.form()
    return UserChangeDataForm(
        username=username,  # type: ignore
        password=form.get("password", None),  # type: ignore
        adress=form.get("adress", None),  # type: ignore
        city=form.get("city", None),  # type: ignore
        country=form.get("country", None),  # type: ignore
    )


class UserInfoChanger:
    def __init__(self, update_user_form: UserChangeDataForm, user_id: int) -> None:
        self.update_user_form = update_user_form
        self.user_id = user_id

    @staticmethod
    def _crypt_password(password: str) -> str:
        return crypt_context.hash(password)

    def _get_ready_user_with_hash(self) -> UserUpdateInfo:
        return UserUpdateInfo(
            username=self.update_user_form.username,
            user_id=self.user_id,
            password_hash=self._crypt_password(self.update_user_form.password)
            if self.update_user_form.password
            else None,
            adress=self.update_user_form.adress,
            city=self.update_user_form.city,
            country=self.update_user_form.country,
        )

    def _create_info_update_query(self, user_update_info: UserUpdateInfo) -> str:
        query = """
            update users_info
            set
        """
        for col in user_update_info.update_info_table_dict():
            if user_update_info.dict()[col]:
                query += f"{col} = {f':{col}'},"

        return f"""{query[:-1]}
                    WHERE user_id = :user_id;"""

    def update_user_data(self) -> None:
        user_update_info = self._get_ready_user_with_hash()
        if not user_update_info.anything_to_update:
            return

        with get_database_cursor_and_commit() as cursor:
            if user_update_info.user_table_to_update:
                cursor.execute(UPDATE_USER, user_update_info.dict())

            if user_update_info.user_info_table_to_update:
                cursor.execute(
                    self._create_info_update_query(user_update_info),
                    user_update_info.dict(),
                )
