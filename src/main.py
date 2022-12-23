from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
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
from src.config import Settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
ouath2 = OAuth2PasswordBearerWithCookie(tokenUrl="token")



@app.get("/login")
def login(request: Request):
    logger.info(request)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    user_form = await load_data_from_request(request)
    user_form_validation = validate_user_form(user_form)

    if not user_form_validation.valid:
        return user_form_validation.dict()

    try:
        authenticate_user(user_form)
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException as e:
        logger.info(e)
        return templates.TemplateResponse(
            "auth/login.html",
            {**user_form_validation.dict(), "request": request},
        )
