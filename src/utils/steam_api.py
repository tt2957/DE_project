import requests

STEAM_CONCURRENT_API = (
    "https://api.steampowered.com/ISteamUserStats/"
    "GetNumberOfCurrentPlayers/v1/"
)

def get_current_players(appid: int) -> int:
    params = {
        "appid": appid
    }
    response = requests.get(STEAM_CONCURRENT_API, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data["response"]["player_count"]
