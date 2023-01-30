import logging
import requests
import random
from models.GameWord import GameWord
from models.GameTurn import GameTurn
from models.GameTurnResult import GameTurnResult


class WordsProvider:
    def __init__(self, api_key: str):
        self.endpoint = "https://wordsapiv1.p.rapidapi.com"
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
        }

    def get_random_word(self) -> str:
        try:
            query_string_params = {
                "letters": 5,
                "partsOfSpeech": "noun",
                "limit": 50,
                "page": 1,
                "hasDetails": "hasCategories"
            }
            request_url = f"{self.endpoint}/words/"
            res = requests.get(request_url, headers=self.headers, params=query_string_params)
            json_res = res.json()
            words: list[str] = json_res["results"]["data"]
            logging.info(f"Pulled words from the api: ${words}")
            return random.choice(words)
        except requests.RequestException as re:
            logging.error(re)
            return ""

    def does_word_exist(self, word_attempt: str) -> bool:
        try:
            request_url = f"{self.endpoint}/words/{word_attempt}/frequency"
            res = requests.get(request_url, headers=self.headers)
            return 200 <= res.status_code < 300
        except requests.RequestException as re:
            logging.error(re)
            return False

    def compare_word_attempt(self, game_word: GameWord, game_turn: GameTurn) -> GameTurnResult:
        correct_letters = []
        misplaced_letters = []
        # find correctly placed letters
        winning_game_word = game_word.word
        for i, letter in enumerate(game_turn.word):
            if letter == winning_game_word[i]:
                correct_letters.append(i)
        # find misplaced letters
        for i, letter in enumerate(game_turn.word):
            if letter in winning_game_word and i not in correct_letters:
                misplaced_letters.append(i)
        game_win = game_word.word == game_turn.word
        game_turn_result = GameTurnResult(
            word_attempt=game_turn.word,
            correct_letters=correct_letters,
            misplaced_letters=misplaced_letters,
            win=game_win
        )
        return game_turn_result

