from fastapi import Request
from pydantic import BaseModel

from movie_ranking_app.models.auth import UserFormValidation
from movie_ranking_app.models.movie import Movie


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
    username: str | None

    class Config:
        arbitrary_types_allowed = True


class UserInfoUpadeContex(UserContext):
    invalid_password: bool


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
