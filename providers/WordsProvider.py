import logging
import requests
import os
import random


class WordsProvider:
    def __init__(self):
        self.endpoint = "https://wordsapiv1.p.rapidapi.com"
        self.api_key = os.getenv("WORDS_API_KEY")
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
            res = requests.get(request_url, self.headers, query_string_params)
            json_res = res.json()
            words: list[str] = json_res["results"]["data"]
            return random.choice(words)
        except requests.RequestException as re:
            logging.error(re)
            return ""

    def does_word_exist(self, word_attempt: str) -> bool:
        try:
            request_url = f"{self.api_endpoint}/words/{word_attempt}"
            res = requests.get(request_url, self.headers)
            return 200 <= res.status_code < 300
        except requests.RequestException as re:
            logging.error(re)
            return False

