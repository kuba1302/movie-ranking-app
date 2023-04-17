# Movie ranking app

Simple webapp prepared for university course that allows users to rate movies. It aggregates user rankings and show which of them were most liked by users. It was written using FastApi framework and jinja2 templates. 

## Installation
The easiest way to install the app is to use Poetry:

- Clone the repository
- Install Poetry: `pip install poetry`
- Install the app: `poetry install movie-ranking-app`

## Modules
#### auth
The auth module contains code related to user authentication, including the creation of user accounts, login, and changing account credentials. It also includes code for implementing OAuth2 authentication using cookies.

- change_credentials.py: This module contains code for changing user credentials (passwords).
- crypt_context.py: This module contains code for creating a password hashing context for user credentials.
- login.py: This module contains code for user login.
- oauth2_with_cookies.py: This module contains code for implementing OAuth2 authentication using cookies.
- sign_up.py: This module contains code for user account creation.
- 
#### config
The config module contains configuration settings for the application.

#### core
The core module contains the application's core functionality for movies, rankings, and user ratings.

- movie.py: This module contains code for handling movie data.
- ranking.py: This module contains code for calculating movie rankings based on user ratings.
- user_ratings.py: This module contains code for handling user ratings of movies.

#### exceptions
The exceptions module contains custom exceptions used throughout the application.

#### models
The models module contains database models used by the application.

#### sample_db_creation
The sample_db_creation module contains code for creating a sample database and inserting sample data into it.

#### sqlite
The sqlite module contains code for connecting to and interacting with a SQLite database.

- db_connection.py: This module contains code for creating and managing a database connection.

#### templates
The templates module contains Jinja2 HTML templates used by the application to render web pages.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
