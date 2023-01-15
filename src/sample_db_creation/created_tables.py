from src.sqlite import get_database_cursor

CREATE_USERS_QUERY = """
    --sql
    CREATE TABLE users
    (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        username VARCHAR(36), 
        password_hash VARCHAR(60)
    );  
"""
CREATE_USERS_INFO_QUERY = """
    --sql
    CREATE TABLE users_info
    (
        user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        adress VARCHAR(36), 
        city VARCHAR(36), 
        country VARCHAR(36), 
        picture_url VARCHAR(36),
        FOREIGN KEY(user_id) REFERENCES users(id) 
    );
"""
CREATE_MOVIE_CATEGORIES_QUERY = """
    --sql
    CREATE TABLE movie_categories(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR(36)
    );
"""
CREATE_DIRECTORS_QUERY = """
    --sql
    CREATE TABLE directors(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR(36),
        surname VARCHAR(36)
    );
"""
CREATE_MOVIES_QUERY = """
    --sql
        CREATE TABLE movies(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR(36), 
        description VARCHAR(36), 
        category_id INTEGER, 
        premiere_date TEXT, 
        director_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES movie_categories(id),
        FOREIGN KEY(director_id) REFERENCES directors(id) 
    );
"""
CREATE_RATINGS_QUERY = """
    --sql
        CREATE TABLE ratings(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        movie_id INTEGER, 
        rating INTEGER, 
        rating_date TEXT, 
        FOREIGN KEY(movie_id) REFERENCES movies(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
"""
CREATE_ACTORS_QUERY = """
    --sql
    CREATE TABLE actors(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR(36), 
        surname VARCHAR(36), 
        birth_date TEXT
    )
"""
CREATE_ACTOR_OCCURENCES_QUERY = """
    --sql 
    CREATE TABLE actor_occurences(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        movie_id INTEGER, 
        actor_id INTEGER, 
        FOREIGN KEY(actor_id) REFERENCES actors(id)
    );
"""

queries_to_execute = [
    CREATE_USERS_QUERY,
    CREATE_USERS_INFO_QUERY,
    CREATE_MOVIE_CATEGORIES_QUERY,
    CREATE_DIRECTORS_QUERY,
    CREATE_MOVIES_QUERY,
    CREATE_RATINGS_QUERY,
    CREATE_ACTORS_QUERY,
    CREATE_ACTOR_OCCURENCES_QUERY,
]


def create_all_tables(queries: list[str]) -> None:
    with get_database_cursor() as cursor:
        for query in queries:
            cursor.execute(query)


def create_one_table(query: str) -> None:
    with get_database_cursor() as cursor:
        cursor.execute(query)


if __name__ == "__main__":
    create_one_table(CREATE_RATINGS_QUERY)
