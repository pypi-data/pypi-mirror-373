from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.staticfiles import StaticFiles
from fastapi import Request
from fastapi import Request, FastAPI
from fastapi.templating import Jinja2Templates  
from typing import Dict, Optional, List
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from urllib.parse import urlencode
import fnmatch

LOGOUT_FUNCTION = "google_sso_logout"
LOGIN_FUNCTION = "google_sso_login"

class iTutorGoogleSSORoutesMiddleware:
    """
    Middleware to define which routes need to be validated with @itutor.com google sso
    Params:
        -  `app`: Starlette of FastAPI instance
        -  `allowed_routes`: List with allowed routes routes, if a path is present here will not be validated if is protected, it supports asterisk. I.E `/admin/*`
        -  `protected_routes`: List with protected routes, it supports asterisk. I.E `/admin/*`
        -  `login_url`: Path to login form.
    """
    def __init__(
        self,
        app: ASGIApp,
        allowed_routes: List[str],
        protected_routes: List[str],
        login_url: str,
        allowed_users: Optional[List[str]] = None,
    ) -> None:
        """
        Params:
          -  `app`: Starlette of FastAPI instance
          -  `allowed_routes`: List with allowed routes routes, if a path is present here will not be validated if is protected, it supports asterisk. I.E `/admin/*`
          -  `protected_routes`: List with protected routes, it supports asterisk. I.E `/admin/*`
          -  `login_url`: Path to login form.
          -  `allowed_users`: If present, only users in this list will be allowed to access the protected routes. Otherwhise all users with @itutor.com domain will be allowed.
        """

        self.app = app
        self.protected_routes = protected_routes
        self.allowed_routes = allowed_routes + ["/sso-statics*"] #static fields should be exposed
        self.login_url = login_url
        self.allowed_users = allowed_users

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive=receive)
        path = scope.get("path")
        if self._is_allowed(path):
            await self.app(scope, receive, send)
            return 
        if self._is_protected(path):
            response: Response
            user = request.session.get('user')
            if not user:
                params = urlencode(
                    {
                    "redirect_to": path
                    })
                response = RedirectResponse(f"{self.login_url}?{params}")
                await response(scope, receive, send)
                return 
            email: str = user.get("email")
            _, provider = email.split("@")
            if provider not in ["itutor.com", "fullmindlearning.com"]:
               message = "Sorry, only @itutor.com and @fullmindlearning.com email addresses are allowed."
               response = RedirectResponse(f"{self.login_url}?error_message={str(message)}")
               await response(scope, receive, send)
               return 
            if self.allowed_users and email not in self.allowed_users:
                message = f"Sorry {user.get('name')}, you are not allowed to access this page. Please contact your administrator to get access."
                response = RedirectResponse(f"{self.login_url}?error_message={str(message)}")
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


    def _is_protected(self, path: str) -> bool:
        """
        Returns whether the path is protected or not
        Arguments:
          -  `path`: an string
        """
        return any([fnmatch.fnmatch(path, protected_route) for protected_route in self.protected_routes])

    def _is_allowed(self, path: str) -> bool:
        """
        Returns whether the path is allowed or not
        Arguments:
          -  `path`: an string
        """
        return any([fnmatch.fnmatch(path, allowed_route) for allowed_route in self.allowed_routes])


def install_google_sso(
    app: FastAPI,
    client_id: str,
    client_secret: str,
    login_base_path: Optional[str] = "/admin",
    allowed_routes: List[str] = [],
    protected_routes: List[str] = [],
    scope_kwargs: Dict[str,str] = {"scope": "openid email profile"},
    allowed_users: Optional[List[str]] = None,
    *args,
    **kwargs,
    ) -> FastAPI:
    """
    Install google sso routes for login and logout
    Params:
        -  `client_id`: `string`, Google Oauth client_id.
        -  `client_secret`: `string`, Google Oauth client_secret.
        -  `login_base_path`: `string`, base url for the login form.
        -  `redirect_after_login`: `string`, path to redirect after logged in with google sso.
        -  `allowed_routes`: List with allowed routes routes, if a path is present here will not be validated if is protected, it supports asterisk. I.E `/admin/*`
        -  `protected_routes`: List with protected routes, it supports asterisk. I.E `/admin/*`
        -  `allowed_users`: If present, only users in this list will be allowed to access the protected routes. Otherwhise all users with @itutor.com domain will be allowed.
        -  `scope_kwargs`: `Dict[str,str]`, scope requested to the client.
    """
    oauth = OAuth()
    oauth.register(
        "google",
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs=scope_kwargs,
    )
    #return init_routes(app, oauth, login_base_path, redirect_after_login)
    init_routes(app, oauth, login_base_path)
    app.add_middleware(
    iTutorGoogleSSORoutesMiddleware,
    allowed_routes = [login_base_path + "*"] + allowed_routes,
    protected_routes = protected_routes,
    login_url = app.url_path_for(LOGIN_FUNCTION),
    allowed_users = allowed_users,
    )

def init_routes(
    app: FastAPI, 
    oauth: OAuth, 
    login_base_path: str, 
    ) -> FastAPI:
    templates = Jinja2Templates("itutor_google_sso/templates")
    templates.env.loader = ChoiceLoader(
        [
            FileSystemLoader("itutor_google_sso/templates"),
            PackageLoader("fastapi_middlewares", "itutor_google_sso/templates"),
        ]
    )
    app.mount("/sso-statics", app=StaticFiles(packages=['fastapi_middlewares']), name="sso-statics"),

    @app.get(f"{login_base_path}/login/google", include_in_schema=False)
    async def google_sso(request: Request, redirect_to: Optional[str] = None):
        # absolute url for callback
        # we will define it below
        redirect_uri = str(request.url_for("auth"))
        kwargs = {}
        if redirect_to:
            # Using state to pass the redirect_to url
            # https://developers.google.com/identity/protocols/oauth2/web-server#creatingclient
            kwargs["state"] = redirect_to
        return await oauth.google.authorize_redirect(request, redirect_uri, **kwargs)


    @app.get(f"{login_base_path}/login", include_in_schema=False)
    async def google_sso_login(request: Request, error_message: Optional[str] = None, redirect_to: Optional[str] = None):
        # absolute url for callback
        # we will define it below
        auth_url = str(request.url_for("google_sso"))
        if redirect_to:
            auth_url += f"?{urlencode({'redirect_to': redirect_to})}"
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "redirect_uri_google_sso": auth_url,
                "error_message": error_message
            },
        )

    @app.get(f"{login_base_path}/google_auth", include_in_schema=False)
    async def auth(request: Request, state: Optional[str] = None):
        token = await oauth.google.authorize_access_token(request)
        # <=0.15
        # user = await oauth.google.parse_id_token(request, token)
        user = token.get("userinfo")
        if user:
            request.session["user"] = dict(user)
        return RedirectResponse(url=state)


    @app.get(f"{login_base_path}/logout", include_in_schema=False)
    async def google_sso_logout(request: Request):
        request.session.pop("user", None)
        login_url = str(request.url_for(LOGIN_FUNCTION))
        return RedirectResponse(url=login_url)
    return app



