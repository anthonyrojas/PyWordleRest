## Local Testing

This program uses docker to easily standup and tear down a development server. Run the command below to start the uvicorn server with a local instance of DynamoDB.

```commandline
docker-compose -f docker-compose.development.yml up -d --build
```