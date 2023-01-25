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
    cognito_client = client("cognito-idp")
    req.state.auth_provider: AuthenticationProvider = AuthenticationProvider(cognito_client)
    req.state.words_provider: WordsProvider = WordsProvider()
    req.state.dynamo_provider: DynamoProvider = DynamoProvider()
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start_server()


