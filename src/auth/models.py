from pydantic import BaseModel, root_validator


class UserForm(BaseModel):
    username: str | None
    password: str | None


class UserFormValidation(BaseModel):
    valid_username: bool
    valid_password: bool

    @property
    def valid(self) -> bool:
        return True if self.valid_username and self.valid_password else False


class SignUpForm(BaseModel):
    username: str
    password: str
    adress: str
    city: str
    country: str


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

