import pandas as pd
import duckdb
from datetime import timedelta

# DB 파일 경로
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "steam.duckdb")

# 사용자 제공 매핑 (필요 시 활용)
NAME_MAPPER = {
    "Tekken 8": "TEKKEN 8",
    "FC 26": "EA SPORTS FC™ 26",
    "GTA 5": "Grand Theft Auto V",
    "Counter-Strike 2": "Counter-Strike 2",
    "Dota 2": "Dota 2"
}

def load_ccu_data(ui_game_name):
    db_game_name = NAME_MAPPER.get(ui_game_name, ui_game_name)
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        # 6시간 제한을 없애고 최근 3일(또는 전체) 데이터를 가져옴
        query = f"""
            SELECT collected_at AS timestamp, concurrent_players AS player_count
            FROM raw_concurrency
            WHERE game_name = '{db_game_name}'
              AND collected_at >= now() - INTERVAL '3 days' 
            ORDER BY timestamp ASC
        """
        df = con.execute(query).fetchdf()
        con.close()
        
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"]) + timedelta(hours=9)
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def calculate_steam_status(ccu_df):
    """
    제공해주신 로직에 따라 동접자 기반 쾌적도를 계산합니다.
    """
    if ccu_df is None or ccu_df.empty:
        return "데이터 없음", 0, "데이터를 불러올 수 없습니다."
    
    # 최근 6시간 데이터만 추출 (차트용 및 계산용)
    latest_ts = ccu_df['timestamp'].max()
    six_hours_ago = latest_ts - timedelta(hours=6)
    recent_df = ccu_df[ccu_df['timestamp'] >= six_hours_ago]

    # 현재 동접자 및 전체 평균 계산
    ccu_now = int(ccu_df.iloc[-1]["player_count"])
    ccu_avg = int(ccu_df["player_count"].mean())
    
    # 쾌적도 점수 계산용 비중 (Ratio)
    ratio = ccu_now / ccu_avg if ccu_avg > 0 else 1.0
    
    # 사용자 로직 적용
    if ratio >= 1.1: 
        status = "쾌적"
        score = 90
        desc = "평소보다 유저가 많아 매칭이 매우 빠르게 잡힙니다."
    elif ratio >= 0.8: 
        status = "보통"
        score = 60
        desc = "안정적인 유저 수가 유지되어 원활한 플레이가 가능합니다."
    else: 
        status = "혼잡"
        score = 30
        desc = "유저 수가 적어 매칭 대기 시간이 길어질 수 있습니다."
        
    return status, score, desc, ccu_now