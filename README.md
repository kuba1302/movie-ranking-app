# Movie ranking app

Simple webapp prepared for university course that allows users to rate movies. It aggregates user rankings and show which of them were most liked by users. It was written using FastApi framework and jinja2 templates. Easiest way to install is to use poetry:
- Clone repository
- poetry install movie-ranking-app

File tree:
```
├── movie_ranking_app/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-310.pyc
│   │   ├── config.cpython-310.pyc
│   │   ├── exceptions.cpython-310.pyc
│   │   ├── main.cpython-310.pyc
│   │   ├── models.cpython-310.pyc
│   │   ├── movie.cpython-310.pyc
│   │   └── ranking.cpython-310.pyc
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── auth.cpython-310.pyc
│   │   │   ├── change_credentials.cpython-310.pyc
│   │   │   ├── crypt.cpython-310.pyc
│   │   │   ├── crypt_context.cpython-310.pyc
│   │   │   ├── crypto_context.cpython-310.pyc
│   │   │   ├── login.cpython-310.pyc
│   │   │   ├── models.cpython-310.pyc
│   │   │   ├── oauth2_with_cookies.cpython-310.pyc
│   │   │   └── sign_up.cpython-310.pyc
│   │   ├── change_credentials.py
│   │   ├── crypt_context.py
│   │   ├── login.py
│   │   ├── oauth2_with_cookies.py
│   │   └── sign_up.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── movie.cpython-310.pyc
│   │   │   ├── ranking.cpython-310.pyc
│   │   │   └── user_ratings.cpython-310.pyc
│   │   ├── movie.py
│   │   ├── ranking.py
│   │   └── user_ratings.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── auth.cpython-310.pyc
│   │   │   ├── context.cpython-310.pyc
│   │   │   ├── db.cpython-310.pyc
│   │   │   └── movie.cpython-310.pyc
│   │   ├── auth.py
│   │   ├── context.py
│   │   ├── db.py
│   │   └── movie.py
│   ├── sample_db_creation/
│   │   ├── created_tables.py
│   │   ├── insert_sample_values.py
│   │   └── sample_data.json
│   ├── sqlite/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── db_connection.cpython-310.pyc
│   │   │   └── models.cpython-310.pyc
│   │   └── db_connection.py
│   └── templates/
│       ├── auth/
│       │   ├── credentials_expired.html
│       │   ├── login.html
│       │   └── signup.html
│       ├── base.html
│       ├── home.html
│       ├── movie.html
│       ├── ranking.html
│       ├── user_info.html
│       └── user_ranking.html
```
