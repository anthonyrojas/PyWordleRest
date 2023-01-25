from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class GameTurn:
    username: str
    date: date
    timestamp: datetime
    word: str
    win: bool
    game_id: str

    def to_dynamo_json(self):
        return {
            "username": {
                "S": self.username
            },
            "date": {
                "S": self.date.isoformat()
            },
            "timestamp": {
                "N": self.timestamp.timestamp()
            },
            "word": {
                "S": self.word
            },
            "win": {
                "BOOL": self.win
            },
            "game_id": {
                "S": self.game_id
            }
        }
