import logging
import requests
import random


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

