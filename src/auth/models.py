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
