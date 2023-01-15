import pandas as pd
from loguru import logger

from src.sqlite import get_database_connection


def get_user_ratings(user_id: int) -> str:
    return f"""
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
        WHERE user_id = {user_id}
        ) 
    WHERE dest_rank = 1
    )
    SELECT movies.name, 
           movies.description,
           ratings_newest.rating
    FROM movies
    LEFT JOIN ratings_newest
    ON movies.id = ratings_newest.movie_id
    LEFT JOIN movie_categories
    ON movies.category_id = movie_categories.id
    WHERE ratings_newest.rating IS NOT NULL
    ORDER BY ratings_newest.rating DESC;
"""


class UserRatingsCreator:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def get_movies_table(self) -> pd.DataFrame:
        with get_database_connection() as connection:
            return pd.read_sql(get_user_ratings(user_id=self.user_id), connection)

    def get_best_movies(self) -> list[dict]:
        table = self.get_movies_table()
        logger.info(table)
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
