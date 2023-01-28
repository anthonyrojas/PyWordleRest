from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class GameTurn:
    username: str
    game_date: date
    game_timestamp: datetime
    word: str
    win: bool
    game_id: str

    def to_dynamo_json(self):
        return {
            "username": {
                "S": self.username
            },
            "game_date": {
                "S": self.game_date.isoformat()
            },
            "game_timestamp": {
                "N": str(self.game_timestamp.timestamp())
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
