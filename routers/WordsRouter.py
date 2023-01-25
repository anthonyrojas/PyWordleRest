from providers.WordsProvider import WordsProvider
from providers.DynamoProvider import DynamoProvider
from fastapi import Request, HTTPException, Depends, APIRouter
from models.GameWord import GameWord
from models.GameTurn import GameTurn
from datetime import date, datetime
from pydantic import BaseModel, Field
from middleware.AuthMiddleware import validate_token


class GameWordAttempt(BaseModel):
    word: str = Field(..., min_length=5, max_length=5, regex="^[a-zA-Z]+$")


words_router = APIRouter(prefix="/word")


@words_router.get("/game-word", status_code=200, dependencies=[Depends(validate_token)])
async def get_game_word(req: Request):
    words_provider: WordsProvider = req.state.words_provider
    dynamo_provider: DynamoProvider = req.state.dynamo_provider
    current_date = date.today()
    current_game_word = dynamo_provider.get_game_for_date(current_date)
    if current_game_word is None:
        random_word = words_provider.get_random_word()
        current_game_word = GameWord(
            "sys",
            current_date,
            datetime.fromisoformat(current_date.isoformat()),
            random_word
        )
        dynamo_provider.save_word_game()
    return {
        "GameWord": current_game_word.word
    }


@words_router.put("/check-word", status_code=200, dependencies=[Depends(validate_token)])
async def check_word_attempt(req: Request, game_word_attempt: GameWordAttempt):
    username: str = req.state.username
    words_provider: WordsProvider = req.state.words_provider
    dynamo_provider: DynamoProvider = req.state.dynamo_provider
    word_attempt = game_word_attempt.word.lower().strip()
    if not words_provider.does_word_exist(word_attempt):
        raise HTTPException(400, {"message": "Bad word attempt! The word must consist of 5 alphabetic characters"})
    # check word against game word
    timestamp = datetime.now().timestamp()
    game_word = dynamo_provider.get_game_for_date(date.fromtimestamp(timestamp))
    game_date = date.fromtimestamp(timestamp)
    game_turn = GameTurn(
        username,
        game_date,
        timestamp,
        word_attempt,
        False
    )
    game_attempt_count = dynamo_provider.get_user_attempt_count_for_game(
        game_date,
        "sys",
        game_word.game_id
    )
    if game_attempt_count >= 6:
        raise HTTPException(400, {
            "Message": "You cannot have more than 6 attempts per game!"
        })
    if game_word == word_attempt:
        game_turn.win = True
    dynamo_provider.save_user_attempt(game_turn)
    return {
        "Message": "Correct!" if game_turn.win is True else "Wrong!"
    }


@words_router.get("/game-attempts/{game_date}", status_code=200, dependencies=[Depends(validate_token)])
async def get_game_attempts_by_date(req: Request, game_date: str):
    username: str = req.state.username
    dynamo_provider: DynamoProvider = req.state.dynamo_provider
    game_word = dynamo_provider.get_game_for_date(date.fromisoformat(game_date))
    attempts: list[GameTurn] = dynamo_provider.get_user_attempts_for_game(
        game_word.date,
        username,
        game_word.game_id
    )
    if len(attempts) < 1:
        raise HTTPException(404, {
            "Message": "No game attempts found for this game!"
        })
    return {"GameAttempts": attempts}


@words_router.get("/game-attempts", status_code=200, dependencies=[Depends(validate_token)])
async def get_user_game_attempts(req: Request, last_timestamp: float = 0):
    username: str = req.state.username
    dynamo_provider: DynamoProvider = req.state.dynamo_provider
    game_attempts = dynamo_provider.get_user_game_turns(username, datetime.fromtimestamp(last_timestamp))
    return game_attempts

