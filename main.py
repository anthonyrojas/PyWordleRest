import os
from fastapi import FastAPI, Request
from routers.WordsRouter import words_router
from routers.AuthRouter import auth_router
from fastapi.middleware.cors import CORSMiddleware
from boto3 import client
from providers.AuthenticationProvider import AuthenticationProvider
from providers.WordsProvider import WordsProvider
from providers.DynamoProvider import DynamoProvider
import logging
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def http_middleware(req: Request, call_next):
    cognito_client = client(
        "cognito-idp",
        region_name="us-west-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    if os.getenv("PROJECT_ENV") == "development":
        dynamo_client = client(
            "dynamodb",
            region_name="anywhere",
            endpoint_url="http://my-dynamodb:8000",
            aws_access_key_id="LOCAL_ACCESS_ID",
            aws_secret_access_key="LOCAL_ACCESS_SECRET_KEY"
        )
        req.state.dynamo_provider: DynamoProvider = DynamoProvider(dynamo_client)
    else:
        dynamo_client = client(
            "dynamodb",
            region_name="us-west-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        req.state.dynamo_provider: DynamoProvider = DynamoProvider(dynamo_client)
    words_api_key = os.getenv("WORDS_API_KEY")
    user_pool_id = os.getenv("USER_POOL_ID")
    app_client_id = os.getenv("APP_CLIENT_ID")
    req.state.auth_provider: AuthenticationProvider = AuthenticationProvider(
        cognito_client,
        user_pool_id,
        app_client_id
    )
    req.state.words_provider: WordsProvider = WordsProvider(words_api_key)
    response = await call_next(req)
    response.headers["Content-Type"] = "application/json"
    req.state.dynamo_provider.close_connection()
    return response


# include routers
app.include_router(words_router)
app.include_router(auth_router)


@app.get("/ping", status_code=200)
async def health_check():
    return {
        "Message": "All systems good!"
    }


def create_games_table(dynamo_client: client):
    # create the table to run this project locally
    logging.info("Project is in development environment. Creating the dynamodb table...")
    try:
        dynamo_client.create_table(
            AttributeDefinitions=[
                {
                    "AttributeName": "username",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "game_timestamp",
                    "AttributeType": "N"
                }
            ],
            TableName="PyWordGame",
            KeySchema=[
                {
                    "AttributeName": "username",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "game_timestamp",
                    "KeyType": "RANGE"
                }
            ],
            BillingMode="PAY_PER_REQUEST",
            Tags=[
                {
                    "Key": "env",
                    "Value": "development"
                }
            ],
            TableClass="STANDARD"
        )
    except RuntimeError as re:
        logging.error(re)


@app.on_event("startup")
async def startup_event():
    if os.getenv("PROJECT_ENV") == "development":
        # create the table to run this project locally
        dynamo_client = client(
            "dynamodb",
            endpoint_url="http://my-dynamodb:8000",
            region_name="anywhere",
            aws_access_key_id="LOCAL_ACCESS_ID",
            aws_secret_access_key="LOCAL_ACCESS_SECRET_KEY"
        )
        create_games_table(dynamo_client)


def start_server():
    print("running start_server")
    env_port = 8080 if os.getenv("PORT") is None else int(os.getenv("PORT"))
    uvicorn.run(app, host="0.0.0.0", port=env_port, reload=True)


if __name__ == "__main__":
    start_server()


