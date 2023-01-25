from boto3 import client
from boto3.dynamodb.conditions import Key, Attr
from models.GameTurn import GameTurn
from models.GameWord import GameWord
from datetime import date, datetime


class DynamoProvider:
    def __init__(self):
        self.__dynamo: client = client("dynamodb")
        self.table_name = "PyWordGame"

    def close_connection(self):
        self.__dynamo.close()

    def get_user_attempt_count_for_game(self, game_date: date, username: str, game_id: str) -> int:
        timestamp = datetime.fromisoformat(game_date.isoformat())
        dynamo_response = self.__dynamo.query(
            TableName=self.table_name,
            Select="COUNT",
            ConsistentRead=True,
            KeyConditionExpression=Key("username").eq(username) & Key("timestamp").gte(timestamp),
            FilterExpression=Attr.eq("game_id", game_id)
        )
        return int(dynamo_response["Count"])

    def get_user_attempts_for_game(self, game_date: date, username: str, game_id: str) -> list[GameTurn]:
        timestamp = datetime.fromisoformat(game_date.isoformat())
        results = self.__dynamo.query(
            TableName=self.table_name,
            Select="ALL_ATTRIBUTES",
            ConsistentRead=True,
            KeyConditionExpression=Key("username").eq(username) & Key("timestamp").gte(timestamp),
            FilterExpression=Attr.eq("game_id", game_id)
        )
        items: list[dict] = results["Items"]
        game_turns = []
        for item in items:
            game_turns.append(GameTurn(
                item["username"],
                date.fromisoformat(item["date"]),
                datetime.fromtimestamp(item["timestamp"]),
                item["word"],
                item["win"],
                item["game_id"]
            ))
        return game_turns

    def get_game_for_date(self, game_date: date) -> GameWord | None:
        timestamp = datetime.fromisoformat(game_date.isoformat())
        game = self.__dynamo.get_item(
            TableName=self.table_name,
            Key={
                "username": "sys",
                "timestamp": timestamp
            }
        )
        if game["Item"] is None:
            return None
        game_item = game["Item"]
        word_game = GameWord(
            game_item["username"],
            game_item["word"],
            datetime.fromtimestamp(game_item["timestamp"]),
            date.fromisoformat(game_item["date"])
        )
        return word_game

    def get_user_game_turns(self, username: str, timestamp: datetime = 0) -> dict:
        pagination_dict = {}
        if timestamp > 0:
            pagination_dict = {
                "username": username,
                "timestamp": timestamp
            }
        attempts = self.__dynamo.query(
            TableName=self.table_name,
            Select="ALL_ATTRIBUTES",
            ConsistentRead=True,
            KeyConditionExpression=Key("username").eq(username),
            ExclusiveStartKey=pagination_dict
        )
        game_turns: list[GameTurn] = []
        for attempt in attempts["Items"]:
            game_turns.append(GameTurn(
                attempt["game_id"],
                attempt["username"],
                attempt["date"],
                attempt["word"],
                attempt["win"]
            ))
        return {
            "GameTurns": game_turns,
            "LastEvaluatedKey": attempts["LastEvaluatedKey"],
            "Count": attempts["Count"]
        }

    def save_user_attempt(self, game_attempt: GameTurn):
        self.__dynamo.put_item(
            Item=game_attempt.to_dynamo_json()
        )

    def save_word_game(self, word_game: GameWord):
        self.__dynamo.put_item(
            Item=word_game.to_dynamo_json()
        )
