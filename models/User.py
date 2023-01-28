from pydantic import BaseModel


class UserRequestModel(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str


class UserLoginRequestModel(BaseModel):
    username: str
    password: str


class RefreshRequestModel(BaseModel):
    refresh_token: str
    device_key: str




