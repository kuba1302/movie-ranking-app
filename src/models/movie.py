from pydantic import BaseModel


class Movie(BaseModel):
    name: str | None = None
    description: str | None = None
    mean_rating: float | None = None
    director: str | None = None
    name: str | None = None
    actors_data: list[dict] | None = None


class RatingUpdateInput(BaseModel):
    movie_id: int
    rating: int