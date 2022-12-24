from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    status,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from loguru import logger
from pydantic import BaseModel

from src.auth import OAuth2PasswordBearerWithCookie
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from src.auth.auth import (
    load_data_from_request,
    validate_user_form,
    authenticate_user,
    decode_token,
    get_user_from_cookie,
    create_access_token,
)
from src.config import settings
from src.auth.models import UserFormValidation
from src.sqlite.models import User

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
ouath2 = OAuth2PasswordBearerWithCookie(tokenUrl="token")


class ResponseContext(UserFormValidation):
    request: Request
    unmatched_credentials: bool

    class Config:
        arbitrary_types_allowed = True


class UserContext(BaseModel):
    request: Request
    user: dict[str, str] | None

    class Config:
        arbitrary_types_allowed = True


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
    context = ResponseContext(
        valid_password=True,
        valid_username=True,
        request=request,
        unmatched_credentials=False,
    )
    return templates.TemplateResponse("auth/login.html", context.dict())


@app.post("/login")
async def login(request: Request):
    user_form = await load_data_from_request(request)
    user_form_validation = validate_user_form(user_form)

    if not user_form_validation.valid:
        context = ResponseContext(
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
        context = ResponseContext(
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
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@app.get("/logout", response_class=HTMLResponse)
def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        user = get_user_from_cookie(request)
        context = UserContext(request=request, user=user.dict())
        return templates.TemplateResponse("home.html", context.dict())

    except HTTPException:
        context = UserContext(request=request, user=None)
        return templates.TemplateResponse("home.html", context.dict())
