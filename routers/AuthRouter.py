from fastapi import Request, Depends, APIRouter
from providers.AuthenticationProvider import AuthenticationProvider
from models.User import UserRequestModel, UserLoginRequestModel, RefreshRequestModel
from middleware.AuthMiddleware import validate_token


auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register", status_code=200)
async def register_user(req: Request, user: UserRequestModel):
    auth_provider: AuthenticationProvider = req.state.auth_provider
    user = auth_provider.signup_user(user)
    return {"user": user}


@auth_router.post("/login", status_code=200)
async def login(req: Request, user_login: UserLoginRequestModel):
    auth_provider: AuthenticationProvider = req.state.auth_provider
    auth_result: dict = auth_provider.signin_user(user_login)
    return {
        "AuthResult": auth_result
    }


@auth_router.post("/refresh", status_code=200)
async def refresh(req: Request, refresh_request: RefreshRequestModel):
    auth_provider: AuthenticationProvider = req.state.auth_provider
    auth_result: dict = auth_provider.refresh_token(refresh_request)
    return {
        "AuthResult": auth_result
    }


@auth_router.get("/user", status_code=200, dependencies=[Depends(validate_token)])
async def get_user(req: Request):
    auth_provider: AuthenticationProvider = req.state.auth_provider
    token = req.headers["authorization"].split(" ")[1]
    user_info = auth_provider.get_user_info(token)
    return {
        "UserInfo": user_info
    }





