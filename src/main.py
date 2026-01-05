import json
import duckdb
import os
from datetime import datetime
from pathlib import Path

# 'src.'을 제거하고 수정 (이미 src 폴더 안이므로)
from utils.steam_api import get_current_players
from utils.db import get_connection, init_tables

# src 폴더 안에 있으므로 부모 폴더(..)로 나가서 찾아야 함
current_file_path = Path(__file__).resolve()

# 2. 부모 폴더(src)의 부모(Root)를 찾습니다.
# .parent는 src/, .parent.parent는 Root/ 입니다.
BASE_DIR = current_file_path.parent.parent

# 3. 이제 Root에서 db 폴더로 들어갑니다.
DB_PATH = BASE_DIR / "db" / "steam.duckdb"
CONFIG_PATH = BASE_DIR / "config" / "games.json"

def load_games():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def collect():
    print(f"[{datetime.now()}] 수집 시작...")
    init_tables()
    games = load_games()
    
    # with 문으로 자동 Commit/Close 보장
    with duckdb.connect(DB_PATH) as conn:
        collected_at = datetime.utcnow() # UTC 기준
        
        for game in games:
            appid = game["appid"]
            name = game["name"]
            try:
                players = get_current_players(appid)
                
                # [수정] 데이터 검증: players가 None이 아니고 0보다 클 때만 저장
                if players is not None and players > 0:
                    conn.execute(
                        """
                        INSERT INTO raw_concurrency (appid, game_name, concurrent_players, collected_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (appid, name, players, collected_at)
                    )
                    print(f"  [SUCCESS] {name} ({appid}) -> {players}")
                else:
                    # 데이터가 0이거나 가져오지 못했을 경우 저장하지 않고 로그만 남김
                    print(f"  [SKIP] {name} ({appid}): 유효하지 않은 데이터 ({players})")

            except Exception as e:
                print(f"  [FAIL] {name} ({appid}) -> {e}")
                
    print(f"[{datetime.now()}] DB 저장 완료 및 연결 종료")

if __name__ == "__main__":
    collect()