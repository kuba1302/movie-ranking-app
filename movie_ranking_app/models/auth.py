from pydantic import BaseModel, root_validator


class UserForm(BaseModel):
    username: str | None
    password: str | None


class NewUserInput(BaseModel):
    username: str
    password_hash: str


class UserFormValidation(BaseModel):
    valid_username: bool
    valid_password: bool

    @property
    def valid(self) -> bool:
        return True if self.valid_username and self.valid_password else False


class UserDataForm(BaseModel):
    username: str
    password: str
    adress: str
    city: str
    country: str


class UserChangeDataForm(BaseModel):
    username: str
    password: str | None
    adress: str | None
    city: str | None
    country: str | None


class SignUpFormValidation(BaseModel):
    valid_username: bool
    valid_password: bool
    valid_adress: bool
    valid_city: bool
    valid_country: bool

    @property
    def valid(self) -> bool:
        bool_values_to_check = [
            self.valid_username,
            self.valid_password,
            self.valid_adress,
            self.valid_city,
            self.valid_country,
        ]
        return True if all(bool_values_to_check) else False

    def update_value(self, key: str, value: bool) -> None:
        setattr(self, key, value)


class UserUpdateInfo(BaseModel):
    username: str
    user_id: int
    password_hash: str | None
    adress: str | None
    city: str | None
    country: str | None

    @property
    def user_table_to_update(self) -> bool:
        return True if self.password_hash else False

    @property
    def user_info_table_to_update(self) -> bool:
        bool_values_to_check = [
            self.adress,
            self.city,
            self.country,
        ]
        return True if any(bool_values_to_check) else False

    @property
    def anything_to_update(self) -> bool:
        return (
            True
            if self.user_table_to_update or self.user_info_table_to_update
            else False
        )

    def update_info_table_dict(self) -> dict:
        return {
            "adress": self.adress,
            "city": self.city,
            "country": self.country,
        }
