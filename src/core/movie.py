import ast
import pprint

import pandas as pd
from pydantic import BaseModel
from datetime import datetime
from src.exceptions import NonExistentMovieException
from src.models.movie import Movie, RatingUpdateInput
from src.sqlite import (
    dict_from_row,
    get_database_cursor,
    get_database_cursor_and_commit,
)


QUERY_MOVIE = """
    --sql
    with movie_ratings as (
        SELECT AVG(rating) as mean_rating, 
                movies.id
        FROM ratings
        LEFT JOIN movies
        ON ratings.movie_id = movies.id
        GROUP BY ratings.movie_id
    ),
    actors_agg as (
        SELECT actor_occurences.movie_id,
                json_group_array(
                    json_object(
                    'name', actors.name,
                    'surname', actors.surname,
                    'birth_date', actors.birth_date
                    )
                ) as actors_data
        FROM actor_occurences
        LEFT JOIN actors
        ON actor_occurences.actor_id = actors.id
        GROUP BY actor_occurences.movie_id
    )
    SELECT movies.name, 
            movies.description,
            movie_ratings.mean_rating, 
            (directors.name || ' ' || directors.surname) as director,
            actors_agg.actors_data
    FROM movies
    LEFT JOIN movie_ratings
    ON movies.id = movie_ratings.id
    LEFT JOIN movie_categories
    ON movies.category_id = movie_categories.id
    LEFT JOIN directors
    ON movies.director_id = directors.id
    LEFT JOIN actors_agg
    ON movies.id = actors_agg.movie_id
    WHERE movies.id = :movie_id
    ORDER BY movie_ratings.mean_rating DESC;
"""
QUERY_CURRENT_USER_ID = """
    --sql
    SELECT id
    FROM users
    WHERE username = :username;
"""
UPDATE_RATING_QUERY = """
    --sql
    INSERT INTO ratings(user_id, movie_id, rating, rating_date)
    VALUES (:user_id, :movie_id, :rating, :rating_date)
    ON CONFLICT(user_id, movie_id) DO UPDATE SET
        rating=:rating,
        rating_date=:rating_date;
"""


class MoviePageCreator:
    def get_movie(self, movie_id: int) -> Movie:
        query_params = {"movie_id": movie_id}

        with get_database_cursor() as cursor:
            cursor.execute(QUERY_MOVIE, query_params)
            result = cursor.fetchone()

            if not result:
                raise NonExistentMovieException(
                    "Provided movie does not exist!"
                )

            result_dict = dict_from_row(result)
            result_dict["actors_data"] = ast.literal_eval(
                result_dict["actors_data"]
            )
            return Movie(**result_dict)


class MovieRatingUpdater:
    def __init__(self, username: str) -> None:
        self.user_id = self._get_user_id(username)

    def _get_user_id(self, username: str) -> int:
        query_params = {"username": username}

        with get_database_cursor() as cursor:
            cursor.execute(QUERY_CURRENT_USER_ID, query_params)
            result = cursor.fetchone()

            if not result:
                raise NonExistentMovieException(
                    "Provided movie does not exist!"
                )

            return result[0]

    def update_rating(self, rating_update_input: RatingUpdateInput) -> None:
        todays_date = datetime.today().strftime("%d-%m-%Y")
        query_params = {
            "user_id": self.user_id,
            "movie_id": rating_update_input.movie_id,
            "rating": rating_update_input.rating,
            "rating_date": todays_date,
        }

        with get_database_cursor_and_commit() as cursor:
            cursor.execute(UPDATE_RATING_QUERY, query_params)


if __name__ == "__main__":
    movie = MoviePageCreator()
    pprint.pprint(movie.get_movie(1).dict())
