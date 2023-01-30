from dataclasses import dataclass


@dataclass
class GameTurnResult:
    word_attempt: str
    correct_letters: list[int]
    misplaced_letters: list[int]
    win: bool

    def to_json_response(self):
        return {
            "WordAttempt": self.word_attempt,
            "CorrectLetters": self.correct_letters,
            "MisplacedLetters": self.misplaced_letters,
            "Win": self.win
        }
