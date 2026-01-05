import duckdb
import pandas as pd
import os
# 1. DB 연결
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "steam.duckdb")

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