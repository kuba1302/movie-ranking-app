from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from loguru import logger
from pydantic import BaseModel

from src.auth import OAuth2PasswordBearerWithCookie
from src.auth.auth import (
    load_data_from_request,
    validate_user_form,
    authenticate_user,
)
from src.auth.models import UserFormValidation
from src.config import Settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
ouath2 = OAuth2PasswordBearerWithCookie(tokenUrl="token")


class ResponseContext(UserFormValidation):
    request: Request
    unmatched_credentials: bool

    class Config:
        arbitrary_types_allowed = True


@app.get("/login")
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
            unmatched_credentials=False
        )
        return templates.TemplateResponse("auth/login.html", context.dict())

    try:
        authenticate_user(user_form)
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException:
        context = ResponseContext(
            **user_form_validation.dict(),
            request=request,
            unmatched_credentials=True
        )
        return templates.TemplateResponse(
            "auth/login.html",
            context.dict(),
        )
