import duckdb
import pandas as pd
import os
import sys
from pathlib import Path
# 1. DB 연결
# 'src.'을 제거하고 수정 (이미 src 폴더 안이므로)


# src 폴더 안에 있으므로 부모 폴더(..)로 나가서 찾아야 함
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 모듈 임포트 경로 추가 (utils 폴더를 찾기 위함)
# 이 코드가 있어야 'from utils.steam_api'를 안정적으로 불러옵니다.
sys.path.append(str(BASE_DIR / "src"))

from utils.steam_api import get_current_players
from utils.db import get_connection, init_tables

# 3. 경로 정의 (수정된 부분)
CONFIG_PATH = BASE_DIR / "config" / "games.json"
# os.path.join 대신 이미 만든 BASE_DIR를 사용하세요!
DB_PATH = BASE_DIR / "db" / "steam.duckdb"

con = duckdb.connect(DB_PATH)

try:
    print("=== [Steam 데이터 수집 전체 현황] ===")
    
    # 1. 전체 데이터 개수 및 시간 범위 확인
    summary_query = """
    SELECT 
        count(*) as total_rows,
        min(collected_at) as start_time,
        max(collected_at) as end_time
    FROM raw_concurrency
    """
    summary = con.execute(summary_query).df()
    print(f"총 데이터 개수: {summary['total_rows'][0]}개")
    print(f"수집 시작: {summary['start_time'][0]}")
    print(f"최근 수집: {summary['end_time'][0]}")
    
    print("\n=== [게임별 수집 데이터 개수] ===")
    # 2. 게임별로 데이터가 골고루 쌓이고 있는지 확인
    game_stats = """
    SELECT 
        game_name, 
        count(*) as count,
        round(avg(concurrent_players), 0) as avg_players
    FROM raw_concurrency
    GROUP BY game_name
    ORDER BY count DESC
    """
    print(con.execute(game_stats).df())

    print("\n=== [최근 7개 데이터 상세] ===")
    # 3. 최신 순으로 7개만 출력 (시간 기준 확인용)
    print(con.execute("SELECT * FROM raw_concurrency ORDER BY collected_at DESC LIMIT 8").df())

finally:
    con.close()