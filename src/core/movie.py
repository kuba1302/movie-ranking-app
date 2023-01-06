import ast
import pprint
from fastapi import Request

from datetime import datetime

import pandas as pd
from src.exceptions import NonExistentMovieException
from src.models.movie import Movie, RatingUpdateInput
from src.sqlite import (
    dict_from_row,
    get_database_cursor,
    get_database_cursor_and_commit,
)
from loguru import logger
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt

import matplotlib as mpl
import io
import base64

from src.sqlite.db_connection import get_database_connection

COLOR = '#565656'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR
plt.switch_backend("Agg")

QUERY_MOVIE = """
    --sql
    with ratings_newest as (
    SELECT movie_id, user_id, rating_date, rating FROM ( 
        SELECT 
            movie_id, 
            user_id, 
            rating_date, 
            rating,
            RANK() OVER (PARTITION BY movie_id, user_id 
            ORDER BY rating_date DESC) dest_rank
        FROM ratings
        ) 
    WHERE dest_rank = 1
    ),
    movie_ratings as (
        SELECT AVG(rating) as mean_rating, 
                movies.id
        FROM ratings_newest
        LEFT JOIN movies
        ON ratings_newest.movie_id = movies.id
        GROUP BY ratings_newest.movie_id
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
    VALUES (:user_id, :movie_id, :rating, :rating_date);
"""


def get_query_movei_ratigns_by_date(movie_id: int) -> str:
    return f"""
        --sql
        SELECT movie_id, 
            AVG(rating), 
            strftime('%d-%m-%Y', rating_date) AS rating_date
        FROM ratings
        WHERE movie_id = {movie_id}
        GROUP BY rating_date, movie_id
        ORDER BY rating_date
    ;"""


class MoviePageCreator:
    def __init__(self, movie_id: int) -> None:
        self.movie_id = movie_id

    def get_movie(self) -> Movie:
        query_params = {"movie_id": self.movie_id}

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

    def _get_query_movie_ratigns_by_date(self) -> str:
        return f"""
            --sql
            SELECT 
                AVG(rating) as rating, 
                rating_date
            FROM (
                SELECT 
                    rating, 
                    strftime('%d-%m-%Y', rating_date) AS rating_date
                FROM ratings
                WHERE movie_id = {self.movie_id}
            )
            GROUP BY rating_date
            ORDER BY rating_date ASC
        ;"""

    def _get_plot_data(self) -> pd.DataFrame:
        with get_database_connection() as connection:
            return pd.read_sql(
                self._get_query_movie_ratigns_by_date(), connection
            )

    def generate_plot(self) -> str:
        fig, ax = plt.subplots(1, 1)
        ax.set_title("Movie mean rating over time")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Mean rating")
        ax.grid()
        ax.set_facecolor("#D7CEC7")
        ax.set_ylim(0, 10)
        fig.set_facecolor("#D7CEC7")
        data = self._get_plot_data()
        logger.info(data)
        ax.plot(data["rating_date"], data["rating"], "ro-", color="#76323F")

        pngImage = io.BytesIO()
        FigureCanvas(fig).print_png(pngImage)

        pngImageB64String = "data:image/png;base64,"
        pngImageB64String += base64.b64encode(pngImage.getvalue()).decode(
            "utf8"
        )
        return pngImageB64String


class MovieRatingUpdater:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def update_rating(self, rating_update_input: RatingUpdateInput) -> None:
        todays_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        query_params = {
            "user_id": self.user_id,
            "movie_id": rating_update_input.movie_id,
            "rating": rating_update_input.rating,
            "rating_date": todays_date,
        }

        with get_database_cursor_and_commit() as cursor:
            cursor.execute(UPDATE_RATING_QUERY, query_params)


async def load_movie_rating_form_from_request(
    request: Request,
) -> int:
    form = await request.form()
    return form["rating"]  # type: ignore
