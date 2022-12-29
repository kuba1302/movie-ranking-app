from src.sqlite import get_database_connection
import pandas as pd


class TableCreator:
    SELECT_BEST_MOVIES_QUERY = """
        --sql
        with movie_ratings as (
            SELECT AVG(rating) as mean_rating, 
                   movies.id
            FROM ratings
            LEFT JOIN movies
            ON ratings.movie_id = movies.id
            GROUP BY ratings.movie_id
        )
        SELECT movies.name, 
               movies.description,
               movie_ratings.mean_rating
        FROM movies
        LEFT JOIN movie_ratings
        ON movies.id = movie_ratings.id
        LEFT JOIN movie_categories
        ON movies.category_id = movie_categories.id
        ORDER BY movie_ratings.mean_rating DESC
        ;
    """

    def get_movies_table(self) -> pd.DataFrame:
        with get_database_connection() as connection:
            return pd.read_sql(self.SELECT_BEST_MOVIES_QUERY, connection)

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


if __name__ == "__main__":
    table = TableCreator()
    movies = table.get_worst_movies()
    for one_movie in movies:
        print(one_movie["index"])
