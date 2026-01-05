import requests
from config import BASE_URL, HEADERS

def fetch_player_by_name(player_name: str):
    url = f"{BASE_URL}/players"
    params = {
        "filter[playerNames]": player_name
    }

    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code != 200:
        raise RuntimeError(
            f"요청 실패: {res.status_code}\n{res.text}"
        )

    return res.json()

if __name__ == "__main__":
    player_name = "Tosibari"

    data = fetch_player_by_name(player_name)

    print("API 호출 성공")
    print("Player ID:", data["data"][0]["id"])
