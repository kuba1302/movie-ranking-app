from typing import Any
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger


from src.auth import (
    OAuth2PasswordBearerWithCookie,
    UserCreator,
    UserInputValidator,
    authenticate_user,
    create_access_token,
    decode_token,
    get_user_from_cookie,
    load_data_from_request,
    load_sign_up_form_from_request,
    validate_user_form,
)
from src.config import settings
from src.core import (
    MoviePageCreator,
    MovieRatingUpdater,
    TableCreator,
    load_movie_rating_form_from_request,
    UserRatingsCreator
)
from src.exceptions import NonExistentMovieException
from src.models.movie import RatingUpdateInput
from src.models.context import (
    LoginResponseContext,
    MoviesContext,
    RankingContext,
    UserContext,
)
from src.models.db import User

app = FastAPI()
app.mount("/static", StaticFiles(directory="/"), name="static")

templates = Jinja2Templates(directory="templates")
ouath2 = OAuth2PasswordBearerWithCookie(tokenUrl="token", templates=templates)


# class ContextArbitraryTypesBase(BaseModel):
#     class Config:
#         arbitrary_types_allowed = True


def get_current_user_from_token(token: str = Depends(ouath2)) -> str | Any:
    return decode_token(token)


@app.post("token")
def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
) -> dict[str, str]:
    user = authenticate_user(form_data)
    access_token = create_access_token(data={"username": user.username})
    response.set_cookie(
        key=settings.COOKIE_NAME, value=f"Bearer {access_token}", httponly=True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


@app.get("/login", response_class=HTMLResponse)
def login_post(request: Request):
    context = LoginResponseContext.base_correct_context(request=request)
    return templates.TemplateResponse("auth/login.html", context.dict())


@app.post("/login")
async def login(request: Request):
    user_form = await load_data_from_request(request)
    user_form_validation = validate_user_form(user_form)

    if not user_form_validation.valid:
        context = LoginResponseContext(
            **user_form_validation.dict(),
            request=request,
            unmatched_credentials=False,
        )
        return templates.TemplateResponse("auth/login.html", context.dict())

    try:
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        login_for_access_token(response=response, form_data=user_form)  # type: ignore
        return response

    except HTTPException:
        context = LoginResponseContext(
            **user_form_validation.dict(),
            request=request,
            unmatched_credentials=True,
        )
        return templates.TemplateResponse(
            "auth/login.html",
            context.dict(),
        )


@app.get("/signup", response_class=HTMLResponse)
def sign_up(request: Request):
    return templates.TemplateResponse(
        "auth/signup.html", {"request": request, "invalid_fields": []}
    )


@app.post("/signup", response_class=HTMLResponse)
async def sign_up_post(request: Request):
    sing_up_form = await load_sign_up_form_from_request(request)
    validator = UserInputValidator(sing_up_form=sing_up_form)

    if not validator.is_valid():
        context_not_valid = {
            "request": request,
            "invalid_fields": validator.get_invalid_fields(),
        }
        return templates.TemplateResponse(
            "auth/signup.html", context_not_valid
        )

    user_creator = UserCreator(sing_up_form)
    user_creator.insert_user_data()

    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout", response_class=HTMLResponse)
def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


@app.get("/credentials-expired", response_class=HTMLResponse)
def credentials_expired(request: Request):
    return templates.TemplateResponse(
        "auth/credentials_expired.html", {"request": request}
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        user = get_user_from_cookie(request)
        context = UserContext(request=request, user=user.dict())
        return templates.TemplateResponse("home.html", context.dict())

    except HTTPException:
        context = UserContext(request=request, user=None)
        return templates.TemplateResponse("home.html", context.dict())


@app.get("/ranking", response_class=HTMLResponse)
def ranking(
    request: Request, user: User = Depends(get_current_user_from_token)
):
    table_creator = TableCreator()
    table = table_creator.get_best_movies()
    context = RankingContext(request=request, table=table)
    return templates.TemplateResponse("ranking.html", context.dict())


@app.get("/user-ranking", response_class=HTMLResponse)
def user_ranking(
    request: Request, user: User = Depends(get_current_user_from_token)
):
    table_creator = UserRatingsCreator(user_id=user.id)
    table = table_creator.get_best_movies()
    context = RankingContext(request=request, table=table)
    return templates.TemplateResponse("user_ranking.html", context.dict())

@app.get("/movie/{movie_id}", response_class=HTMLResponse)
def movie(
    movie_id: int,
    request: Request,
    user: User = Depends(get_current_user_from_token),
):
    movie_page_creator = MoviePageCreator(movie_id=movie_id)

    try:
        movie = movie_page_creator.get_movie()
        movie_plot = movie_page_creator.generate_plot()
        context = MoviesContext(
            request=request, plot=movie_plot, **movie.dict()
        )
        return templates.TemplateResponse("movie.html", context.dict())

    except NonExistentMovieException:
        context = MoviesContext.wrong_movie_context(request=request)
        return templates.TemplateResponse("movie.html", context.dict())


@app.post("/movie/{movie_id}", response_class=HTMLResponse)
async def movie_post(
    movie_id: int,
    request: Request,
    user: User = Depends(get_current_user_from_token),
):
    logger.info(user)
    rating = await load_movie_rating_form_from_request(request)
    rating_input = RatingUpdateInput(movie_id=movie_id, rating=rating)
    updater = MovieRatingUpdater(user.id)
    updater.update_rating(rating_input)

    movie_page_creator = MoviePageCreator(movie_id=movie_id)
    movie = movie_page_creator.get_movie()
    context = MoviesContext(request=request, **movie.dict())
    return templates.TemplateResponse("movie.html", context.dict())
