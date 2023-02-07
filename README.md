## Local Testing

This program uses docker to easily standup and tear down a development server. Run the command below to start the uvicorn server with a local instance of DynamoDB.

```commandline
docker-compose -f docker-compose.development.yml up -d --build
```

To verify the table was made locally, run:
```commandline
aws dynamodb list-tables --endpoint-url http://localhost:8000
```