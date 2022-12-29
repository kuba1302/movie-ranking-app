from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
from src.core import MoviePageCreator, TableCreator
from src.exceptions import NonExistentMovieException
from src.models.context import (
    LoginResponseContext,
    MoviesContext,
    RankingContext,
    UserContext,
)
from src.models.db import User

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
ouath2 = OAuth2PasswordBearerWithCookie(tokenUrl="token", templates=templates)


# class ContextArbitraryTypesBase(BaseModel):
#     class Config:
#         arbitrary_types_allowed = True


def get_current_user_from_token(token: str = Depends(ouath2)) -> User:
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
def login(request: Request):
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
        login_for_access_token(response=response, form_data=user_form)
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
async def sign_up(request: Request):
    sing_up_form = await load_sign_up_form_from_request(request)
    validator = UserInputValidator(sing_up_form=sing_up_form)

    if not validator.is_valid():
        context_not_valid = {
            "request": request,
            "invalid_fields": validator.get_invalid_fields(),
        }
        return templates.TemplateResponse("auth/signup.html", context_not_valid)

    user_creator = UserCreator(sing_up_form)
    user_creator.insert_user_data()

    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout", response_class=HTMLResponse)
def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


@app.get("/credentials-expired", response_class=HTMLResponse)
def sign_up(request: Request):
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
def ranking(request: Request, user: User = Depends(get_current_user_from_token)):
    table_creator = TableCreator()
    table = table_creator.get_best_movies()
    context = RankingContext(request=request, table=table)
    return templates.TemplateResponse("ranking.html", context.dict())


@app.get("/movie/{movie_id}", response_class=HTMLResponse)
def movie(
    movie_id: int,
    request: Request,
    user: User = Depends(get_current_user_from_token),
):
    movie_page_creator = MoviePageCreator()

    try:
        movie = movie_page_creator.get_movie(movie_id=movie_id)
        context = MoviesContext(request=request, **movie.dict())
        return templates.TemplateResponse("movie.html", context.dict())
    except NonExistentMovieException:
        context = MoviesContext.wrong_movie_context(request=request)
        return templates.TemplateResponse("movie.html", context.dict())
