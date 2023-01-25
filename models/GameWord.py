from dataclasses import dataclass
from datetime import datetime, date
import uuid


@dataclass
class GameWord:
    username: str  # wordgame will have 'sys' username
    word: str
    timestamp: datetime
    date: date
    game_id: str = uuid.uuid4()

    def to_dynamo_json(self):
        return {
            "game_id": {
                "S": self.game_id
            },
            "timestamp": {
                "N": self.timestamp.timestamp()
            },
            "word": {
                "S": self.word
            },
            "username": {
                "S": self.username
            },
            "date": {
                "S": self.date.isoformat()
            }
        }
