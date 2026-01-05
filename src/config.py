import os
from dotenv import load_dotenv

load_dotenv()

PUBG_API_KEY = os.getenv("PUBG_API_KEY")

if not PUBG_API_KEY:
    raise RuntimeError("PUBG_API_KEY가 .env 파일에 없습니다.")

BASE_URL = "https://api.pubg.com/shards/kakao"

HEADERS = {
    "Authorization": f"Bearer {PUBG_API_KEY}",
    "Accept": "application/vnd.api+json"
}
