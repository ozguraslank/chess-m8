import json
import requests

def get_game_data(game_id: str) -> json:
    """
    Gets game data of the given game ID from the Lichess API
    
    Parameters
    ----------
    game_id : str
        The ID of the game to get data from

    Returns
    -------
    json
        Game data in JSON format
    """
    url = f"https://lichess.org/game/export/{game_id}"
    params = {"analysed":"true", "clocks":"true", "evals":"true", "literate": "true", "opening":"true", "accuracy":"true", "pgnInJson": True}
    headers = {"Accept": "application/json"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    
    return response.json()

def get_user_games(username: str):
    """
    Gets the last 10 games of the given username from the Lichess API

    Parameters
    ----------
    username: str
        The Lichess username to get the games from
    
    Returns
    -------
    list
        List of games in JSON format
    """
    url = f"https://lichess.org/api/games/user/{username}"
    params = {"max": 10, "analysed":"true", "clocks":"true", "evals":"true", "literate": "true", "opening":"true", "accuracy": "true", "pgnInJson": True}
    headers = {"Accept": "application/x-ndjson"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    
    response = response.content.decode("utf-8")
    games = [json.loads(s) for s in response.split("\n")[:-1]]
    return games