from dataclasses import dataclass
from datetime import datetime, date
from uuid import uuid4


@dataclass
class GameWord:
    username: str  # wordgame will have 'sys' username
    word: str
    game_timestamp: datetime
    game_date: date
    game_id: str = str(uuid4())

    def to_dynamo_json(self):
        return {
            "game_id": {
                "S": self.game_id
            },
            "game_timestamp": {
                "N": str(self.game_timestamp.timestamp())
            },
            "word": {
                "S": self.word
            },
            "username": {
                "S": self.username
            },
            "game_date": {
                "S": self.game_date.isoformat()
            }
        }
