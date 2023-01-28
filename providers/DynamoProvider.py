from boto3 import client
from boto3.dynamodb.conditions import Key, Attr
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from models.GameTurn import GameTurn
from models.GameWord import GameWord
from datetime import date, datetime
import math


class DynamoProvider:
    def __init__(self, dynamo_client: client):
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()
        self.__dynamo: client = dynamo_client
        self.table_name = "PyWordGame"

    def close_connection(self):
        self.__dynamo.close()

    def get_user_attempt_count_for_game(self, game_date: date, username: str, game_id: str) -> int:
        timestamp = datetime.fromisoformat(game_date.isoformat()).timestamp()
        dynamo_response = self.__dynamo.query(
            TableName=self.table_name,
            Select="ALL_ATTRIBUTES",
            ConsistentRead=True,
            KeyConditionExpression="username=:username AND game_timestamp >= :game_timestamp",
            FilterExpression="game_id=:game_id",
            ExpressionAttributeValues={
                ":username": {
                    "S": username
                },
                ":game_timestamp": {
                    "N": str(timestamp)
                },
                ":game_id": {
                    "S": game_id
                }
            }
        )
        return int(dynamo_response["Count"])

    def get_user_attempts_for_game(self, game_date: date, username: str, game_id: str) -> list[GameTurn]:
        timestamp = datetime.fromisoformat(game_date.isoformat()).timestamp()
        results = self.__dynamo.query(
            TableName=self.table_name,
            Select="ALL_ATTRIBUTES",
            ConsistentRead=True,
            KeyConditionExpression="username = :username AND game_timestamp >= :game_timestamp",
            FilterExpression="game_id = :game_id",
            ExpressionAttributeValues={
                ":username": {
                    "S": username
                },
                ":game_timestamp": {
                    "N": str(timestamp)
                },
                ":game_id": {
                    "S": game_id
                }
            }
        )
        items: list[dict] = results["Items"]
        game_turns = []
        for item in items:
            game_turns.append(GameTurn(
                username=item["username"],
                game_date=date.fromisoformat(item["game_date"]),
                game_timestamp=datetime.fromtimestamp(item["game_timestamp"]),
                word=item["word"],
                win=item["win"],
                game_id=item["game_id"]
            ))
        return game_turns

    def get_game_for_date(self, game_date: date) -> GameWord | None:
        timestamp = datetime.fromisoformat(game_date.isoformat()).timestamp()
        game: dict = self.__dynamo.get_item(
            TableName=self.table_name,
            Key={
                "username": {
                    "S": "sys"
                },
                "game_timestamp": {
                    "N": str(timestamp)
                }
            }
        )
        if game is None or "Item" not in game.keys():
            return None
        dynamo_game_item: dict = game["Item"]
        game_item = {}
        for k in dynamo_game_item.keys():
            deserialized_val = self.deserializer.deserialize(dynamo_game_item[k])
            game_item[k] = deserialized_val
        word_game = GameWord(
            username=game_item["username"],
            word=game_item["word"],
            game_timestamp=datetime.fromtimestamp(int(game_item["game_timestamp"])),
            game_date=date.fromisoformat(game_item["game_date"]),
            game_id=game_item["game_id"]
        )
        return word_game

    def get_user_game_turns(self, username: str, timestamp: datetime = 0) -> dict:
        pagination_dict = {}
        if timestamp.timestamp() > 0:
            pagination_dict = {
                "username": username,
                "game_timestamp": timestamp
            }
        attempts = self.__dynamo.query(
            TableName=self.table_name,
            Select="ALL_ATTRIBUTES",
            ConsistentRead=True,
            KeyConditionExpression="username=:username",
            ExpressionAttributeValues={
                ":username": {
                    "S": username
                }
            },
            ExclusiveStartKey=pagination_dict
        )
        game_turns: list[GameTurn] = []
        for attempt in attempts["Items"]:
            game_turns.append(GameTurn(
                game_id=attempt["game_id"],
                username=attempt["username"],
                game_timestamp=attempt["game_timestamp"],
                game_date=attempt["game_date"],
                word=attempt["word"],
                win=attempt["win"]
            ))
        return {
            "GameTurns": game_turns,
            "LastEvaluatedKey": attempts["LastEvaluatedKey"],
            "Count": attempts["Count"]
        }

    def save_user_attempt(self, game_attempt: GameTurn):
        self.__dynamo.put_item(
            TableName=self.table_name,
            Item=game_attempt.to_dynamo_json()
        )

    def save_word_game(self, word_game: GameWord):
        self.__dynamo.put_item(
            TableName=self.table_name,
            Item=word_game.to_dynamo_json()
        )
