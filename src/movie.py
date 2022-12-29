from src.sqlite import get_database_connection
import pandas as pd


class Movie:
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
               directors.name,
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
        ORDER BY movie_ratings.mean_rating DESC
        ;
    """

    def get_movie(self) -> pd.DataFrame:
        with get_database_connection() as connection:
            return pd.read_sql(self.QUERY_MOVIE, connection)


if __name__ == "__main__":
    movie = Movie()
    print(movie.get_movie().actors_data[0])
