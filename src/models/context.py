from fastapi import Request
from pydantic import BaseModel

from src.models.auth import UserFormValidation
from src.models.movie import Movie

# class ContextArbitraryTypesBase(BaseModel):
#     class Config:
#         arbitrary_types_allowed = True


class LoginResponseContext(UserFormValidation):
    request: Request
    unmatched_credentials: bool

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def base_correct_context(cls, request: Request):
        return cls(
            valid_password=True,
            valid_username=True,
            request=request,
            unmatched_credentials=False,
        )


class UserContext(BaseModel):
    request: Request
    user: dict[str, str] | None

    class Config:
        arbitrary_types_allowed = True


class RankingContext(BaseModel):
    request: Request
    table: list[dict]

    class Config:
        arbitrary_types_allowed = True


class MoviesContext(Movie):
    request: Request
    plot: str | None = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def wrong_movie_context(cls, request: Request):
        return cls(request=request)


# class MoviesUserRatingContext(MovieUserRating):
#     request: Request

#     class Config:
#         arbitrary_types_allowed = True
