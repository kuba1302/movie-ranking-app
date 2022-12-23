from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel

from src.auth import OAuth2PasswordBearerWithCookie
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
async def login(username: str = Form(), password: str = Form()):
    # credentials = UserCreds(username=username, password=password)
    logger.info(str(username))
