from pydantic import BaseModel


class User(BaseModel): 
    id: int 
    username: str
    password: str
    
class UserInfo(BaseModel):
    user_id: int 
    adress: str
    city: str
    country: str
    picture_url: str
    
class Movie(BaseModel):
    id: int
    name: str
    title: str
    category_id: int
    premiere_date: str
    director: str

class MovieCategories(BaseModel):
    id: int
    name: str

class Rating(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: int
    rating_date: str
    
class AutorOccurence:
    id: int
    movie_id: int
    actor: int

class Actor(BaseModel):
    id: int
    name: str
    surname: str
    birth_date: str