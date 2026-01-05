import requests

API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMDMwNzAzMC1jYzM1LTAxM2UtYjc5Zi0yYTc1NTI5Nzg2MjMiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzY3NTk3OTUxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImRlcCJ9.tw5RFCb3apshAugSlraqOVnyVKh2XO3k8Y9VZle2sGY"
PLAYER_ID = "account.b6be8cb79e664194969c0b1be01628ea"

url = f"https://api.pubg.com/shards/steam/players/{PLAYER_ID}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json"
}

res = requests.get(url, headers=headers)
data = res.json()

matches = data["data"]["relationships"]["matches"]["data"]

print(f"총 매치 수: {len(matches)}")
print("최근 매치 ID 5개:")
for m in matches[:5]:
    print(m["id"])
