from models.User import UserRequestModel, UserLoginRequestModel, RefreshRequestModel


class AuthenticationProvider:
    def __init__(self, cognito_client):
        self.cognito_client = cognito_client
        self.user_pool_id = "us-west-1_PsMmjMgT5"
        self.app_client_id = "3rg6hee3f944prdeb2km7vgq8m"

    def verify_token(self, token: str) -> dict:
        return self.cognito_client.get_user(
            AccessToken=token
        )

    def signup_user(self, user: UserRequestModel) -> dict:
        cognito_user_res = self.cognito_client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=user.username,
            UserAttributes=[
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
            ],
            MessageAction="SUPPRESS",
            DesiredDeliveryMediums=["EMAIL"]
        )
        self.cognito_client.admin_set_user_password(
            UserPoolId=self.user_pool_id,
            Username=user.username,
            Password=user.password,
            Permanent=True
        )
        cognito_user = cognito_user_res["User"]
        username = cognito_user["Username"]
        # put user attributes into a dictionary
        user_attributes = {}
        for user_attribute in cognito_user["Attributes"]:
            user_attributes[user_attribute["Name"]] = user_attribute["Value"]
        user = {
            "Username": username,
            "UserAttributes": user_attributes
        }
        return user

    def signin_user(self, login: UserLoginRequestModel):
        cognito_auth_result: dict = self.cognito_client.initiate_auth(
            ClientId=self.app_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": login.username,
                "PASSWORD": login.password
            }
        )
        return cognito_auth_result["AuthenticationResult"]

    def refresh_token(self, refresh_request: RefreshRequestModel):
        cognito_auth_result: dict = self.cognito_client.initiate_auth(
            ClientId=self.app_client_id,
            AuthFlow="REFRESH_TOKEN",
            AuthParameters={
                "REFRESH_TOKEN": refresh_request.refresh_token
            }
        )
        return cognito_auth_result["AuthenticationResult"]

    def get_user_info(self, token: str) -> dict:
        cognito_user_info = self.cognito_client.get_user(
            AccessToken=token
        )
        username = cognito_user_info["Username"]
        user_attributes = {}
        for user_attribute in cognito_user_info["UserAttributes"]:
            user_attributes[user_attribute["Name"]] = user_attribute["Value"]
        return {
            "Username": username,
            "UserAttributes": user_attributes
        }






