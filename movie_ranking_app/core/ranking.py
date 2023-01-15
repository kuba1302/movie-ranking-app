import pandas as pd

from movie_ranking_app.sqlite import get_database_connection

SELECT_BEST_MOVIES_QUERY = """
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
    )
    SELECT movies.name, 
           movies.description,
           movie_ratings.mean_rating
    FROM movies
    LEFT JOIN movie_ratings
    ON movies.id = movie_ratings.id
    LEFT JOIN movie_categories
    ON movies.category_id = movie_categories.id
    ORDER BY movie_ratings.mean_rating DESC;
"""


class TableCreator:
    def get_movies_table(self) -> pd.DataFrame:
        with get_database_connection() as connection:
            return pd.read_sql(SELECT_BEST_MOVIES_QUERY, connection)

    def get_best_movies(self) -> list[dict]:
        table = self.get_movies_table()
        table["index"] = table.index
        table["ranking_place"] = table.index + 1
        return table.to_dict(orient="records")

    def get_worst_movies(self) -> list[dict]:
        table = (
            self.get_movies_table()
            .sort_values(by="mean_rating", ascending=True)
            .reset_index(drop=False)
        )
        table["ranking_place"] = table.index + 1
        return table.to_dict(orient="records")
