from src.sqlite import get_database_cursor, dict_from_row
import pandas as pd
from pydantic import BaseModel
import ast
import pprint
from src.exceptions import NonExistentMovieException
from src.models.context import Movie


class MoviePageCreator:
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
        ORDER BY movie_ratings.mean_rating DESC
        ;
    """

    def get_movie(self, movie_id: int) -> Movie:
        query_params = {"movie_id": movie_id}

        with get_database_cursor() as cursor:
            cursor.execute(self.QUERY_MOVIE, query_params)
            result = cursor.fetchone()
            if not result:
                raise NonExistentMovieException()
            else:
                result_dict = dict_from_row(result)
                result_dict["actors_data"] = ast.literal_eval(
                    result_dict["actors_data"]
                )
                return Movie(**result_dict)


if __name__ == "__main__":
    movie = MoviePageCreator()
    pprint.pprint(movie.get_movie(1).dict())
