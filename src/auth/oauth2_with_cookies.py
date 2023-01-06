from fastapi import HTTPException, Request, Response, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates

from src.config import settings


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class has been inspired by https://github.com/SamEdwardes/samedwardes.com/blob/main/blog/2022-04-14-fastapi-webapp-with-auth/main.py
    """

    def __init__(
        self,
        tokenUrl: str,
        templates: Jinja2Templates,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        self.templates = templates
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> str | None | Response:
        authorization: str | None = request.cookies.get(settings.COOKIE_NAME)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                return self.templates.TemplateResponse(
                    "auth/credentials_expired.html", {"request": request}
                )
            else:
                return None
        return param
