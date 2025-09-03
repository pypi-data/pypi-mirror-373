from itutor_google_sso import (
    install_google_sso, 
)
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

GOOGLE_CLIENT_ID=str(input("GOOGLE_CLIENT_ID: "))
GOOGLE_CLIENT_SECRET=str(input("GOOGLE_CLIENT_SECRET: "))

app = FastAPI()
install_google_sso(
    app=app,
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    login_base_path="/google-sso",
    redirect_after_login = "/asd",
    protected_routes = ["/admin*"],
)

# SessionMiddleware should be added after iTutorGoogleSSORoutesMiddleware
# or it is not going to work.

app.add_middleware(SessionMiddleware, secret_key="mySecretKey")

