import requests

API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMDMwNzAzMC1jYzM1LTAxM2UtYjc5Zi0yYTc1NTI5Nzg2MjMiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzY3NTk3OTUxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImRlcCJ9.tw5RFCb3apshAugSlraqOVnyVKh2XO3k8Y9VZle2sGY"
MATCH_ID = "1f215354-cb29-4636-a2a8-1d6dd27edb2e"

url = f"https://api.pubg.com/shards/steam/matches/{MATCH_ID}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json"
}

res = requests.get(url, headers=headers)
match = res.json()

print("맵:", match["data"]["attributes"]["mapName"])
print("게임모드:", match["data"]["attributes"]["gameMode"])
print("시작시간:", match["data"]["attributes"]["createdAt"])
print("매치 길이(초):", match["data"]["attributes"]["duration"])
