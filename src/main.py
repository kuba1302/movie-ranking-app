from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from loguru import logger
templates = Jinja2Templates(directory="templates")

from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


@app.get("/login")
def login(request: Request):
    logger.info(request)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    # credentials = UserCreds(username=username, password=password)
    logger.info(str(username))
