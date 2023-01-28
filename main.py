import os

from fastapi import FastAPI, Request, Response
from routers.WordsRouter import words_router
from routers.AuthRouter import auth_router
from fastapi.middleware.cors import CORSMiddleware
from boto3 import client
from providers.AuthenticationProvider import AuthenticationProvider
from providers.WordsProvider import WordsProvider
from providers.DynamoProvider import DynamoProvider
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
        region_name="us-west-1"
    )
    dynamo_client = client(
        "dynamodb",
        region_name="us-west-1"
    )
    if os.getenv("PROJECT_ENVIRONMENT") == "development":
        dynamo_client = client(
            "dynamodb",
            endpoint_url="http://localhost:8000",
        )
    words_api_key = os.getenv("WORDS_API_KEY")
    print(words_api_key)
    req.state.auth_provider: AuthenticationProvider = AuthenticationProvider(cognito_client)
    req.state.words_provider: WordsProvider = WordsProvider(words_api_key)
    req.state.dynamo_provider: DynamoProvider = DynamoProvider(dynamo_client)
    response = await call_next(req)
    response.headers["Content-Type"] = "application/json"
    req.state.dynamo_provider.close_connection()
    return response


# include routers
app.include_router(words_router)
app.include_router(auth_router)


@app.get("/ping")
async def health_check(req: Request, res: Response):
    res.status_code = 200
    return {
        "Message": "All systems good!"
    }


def start_server():
    if os.getenv("PROJECT_ENVIRONMENT") == "development":
        # create the table to run this project locally
        dynamo_client = client("dynamodb", endpoint_url="http://localhost:8000")
        dynamo_client.create_table(
            AttributeDefinitions=[
                {
                    "AttributeName": "username",
                    "AttributeValue": "S"
                },
                {
                    "AttributeName": "game_timestamp",
                    "AttributeValue": "N"
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
    env_port = 8080 if os.getenv("PORT") is None else int(os.getenv("PORT"))
    uvicorn.run(app, host="0.0.0.0", port=env_port, reload=True)


if __name__ == "__main__":
    start_server()


