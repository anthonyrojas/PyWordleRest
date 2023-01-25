import os
from models.User import UserRequestModel, UserLoginRequestModel, RefreshRequestModel


class AuthenticationProvider:
    def __init__(self, cognito_client):
        self.cognito_client = cognito_client

    def verify_token(self, token: str) -> dict:
        return self.cognito_client.get_user(
            AccessToken=token
        )

    def signup_user(self, user: UserRequestModel) -> dict:
        cognito_user = self.cognito_client.admin_create_user(
            UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
            Username=user.username,
            UserAttributes={
                {
                    "Name": "family_name",
                    "Value": user.last_name
                },
                {
                    "Name": "given_name",
                    "Value": user.first_name
                },
                {
                    "Name": "email",
                    "Value": user.email
                }
            },
            TemporaryPassword=user.password,
            DesiredDeliveryMediums=["EMAIL"]
        )
        return cognito_user["User"]

    def signin_user(self, login: UserLoginRequestModel):
        cognito_auth_result: dict = self.cognito_client.initiate_auth(
            ClientId=os.getenv("COGNITO_CLIENT_ID"),
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": login.username,
                "PASSWORD": login.password
            }
        )
        return cognito_auth_result["AuthenticationResult"]

    def refresh_token(self, refresh_request: RefreshRequestModel):
        cognito_auth_result: dict = self.cognito_client.initiate_auth(
            ClientId=os.getenv("COGNITO_CLIENT_ID"),
            AuthFlow="REFRESH_TOKEN",
            AuthParameters={
                "REFRESH_TOKEN": refresh_request.refresh_token,
                "DEVICE_KEY": refresh_request.device_key
            }
        )
        return cognito_auth_result["AuthenticationResult"]

    def get_user_info(self, token: str) -> dict:
        cognito_user_info = self.cognito_client.get_user(
            AccessToken=token
        )
        return {
            "Username": cognito_user_info["Username"],
            "UserAttributes": cognito_user_info["UserAttributes"]
        }






