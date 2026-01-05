import duckdb
import pandas as pd
import streamlit as st
from datetime import timedelta

DB_PATH = r"C:\Users\ouzum\OneDrive\Desktop\데엔 심화\db\steam.duckdb"
MATCH_DATA_PATH = r"C:\Users\ouzum\OneDrive\Desktop\데엔 심화\data\processed\matches.csv"
GAME_NAME = "PUBG: Battlegrounds"

# 맵 이름 변환 딕셔너리
ACTIVE_MAPS = {
    "Baltic_Main": {"name": "에란겔", "img": "https://i.namu.wiki/i/95SD2Fj-78mSu2McyOjhvS37k4jSm5sx9hBTwF4K8JafNS6wTxrT69CKLeM4NuwZkj_O8tCN_DfbO1k0MePmogWMsYcvR8lPtn5AGIsjO3KOdht2rneIUyO07T77fGoXNWvPSt41I7NXbZqDJOK9tQ.webp"},
    "Desert_Main": {"name": "미라마", "img": "https://i.namu.wiki/i/lV_4PvFUUrrD8aeuvf7GITlyBeoacNrmS6xWMl7h6aQNyfnN5EuRLsONql2G0BtQeWzvEU93I0fU_4x5NJYUatqnzMf70wA67Wsqixk_rOqEdpVCWfxaSLyl9iIhwi0aFQeWA9IOaWCfWRXYBFfA-w.webp"},
    "Tiger_Main": {"name": "태이고", "img": "https://i.namu.wiki/i/k6V4aoOntVkpIFC4xfHmGr4b_ajtGkG3m-GbjlBYeZBRJbMLDJ1DWe47hubQSvotLE-d5JcW6Iu1Lbz13SfVJgBrXYyxEFxvHxMj5KTEtSZhHiKVNIW7gtBo1_oLD1YnBPwRjhklZ880oVEPBJphpA.webp"},
    "Savage_Main": {"name": "사녹", "img": "https://i.namu.wiki/i/BvG-vAJRK6Ssd2XsILDha7xyFqAu3Fc_0l6ZzvBJELS6n3z1mKOS8PryaU9gnV9dPT12dZd4zEalGa7ia5L4Ewx7OwM-6SnUG6sv-RuNiwcBgyFM7IP6FxTwugqdNDPhdPhXNqbinFnQu5g-8rOoyQ.webp"},
    "Neon_Main": {"name": "론도", "img": "https://i.namu.wiki/i/_i77U8qe8wseQa6dxsEfLkLGjVPh4q5Xo985ZgCNfLLGBd7iDuBDOO62m5z6BpzEQs2tS7Hg5ZDdJZn1bOG6T6l0itP9Uy9kVKK0V7Hn21pHxMJzKHSzXt3vV6yRp60DJ6Sv6CrRc2biVpC5QWz5Mw.webp"},
    "DihorOtok_Main": {"name": "비켄디", "img": "https://i.namu.wiki/i/s90tKv65c8cM7QSsnPF6mMUPv7uZRW61rMbFCGJ57wRziAViYIq5BIJKUu998TIBywlWL1zIhhxX8WlCl7eyPoVjF3igH6EM60zjDxZFd_6cbxn7JAQL2L4luRgLotgv64sjjaSd7rhGnBtWt5E_lA.webp"},
    "Kiki_Main": {"name": "데스턴", "img": "https://i.namu.wiki/i/i9_XCCrTrHqGMt7roXVR9lLiy7x4EMEvJ2SmOfo3vS_eXP6N0ORqQS17UfYiOf2x6PvRZZvEZHyy1X6H4zcTmLpBmZaGgH7Ryrym77BM6RI0eHOliC41JZ6Bnq6zp-5B0IG_i-Rthi2zKjaWnGwGYg.webp"},
    "Summerland_Main": {"name": "카라킨", "img": "https://i.namu.wiki/i/57RCsymAlxM-ksqzWJvG7zESnlGfPN1gib1liZ0wc2OEy-RMwZMT15Mchn_PSIRK50Q5oVlZSEynFa5X_0niTiciCPvoCO9kbRgLGsshLHwdRZdxGyZUX8MiHEhNG2HWMJ7S10i84ZWqaL5uwkDIJQ.webp"},
    "Chimera_Main": {"name": "파라모", "img": "https://i.namu.wiki/i/7ORZrmtkA4hhTsxm1xfxlnsafBH6k7cN626cDhRD_Dx1V9weCQ4WN6PMEYvKTWj25Gf0EhKonI66R7qDWYwUeRcl4iWp8-EysC9TxWGDlJac3aY0wo_YLCYqmm2Umguh4kB7oZcf4UxHB95JMCPM-Q.webp"}
}

@st.cache_data(ttl=600)
def load_match_data():
    """CSV 기반 배그 매치 데이터 로드 + display_map 컬럼 생성"""
    try:
        df = pd.read_csv(MATCH_DATA_PATH)
        df['created_at'] = pd.to_datetime(df['created_at'])
        # 맵 이름만 표시
        df['display_map'] = df['map_name'].map(lambda x: ACTIVE_MAPS[x]['name'] if x in ACTIVE_MAPS else x)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_ccu_data():

    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        # 6시간 제한을 없애고 최근 3일(또는 전체) 데이터를 가져옴
        query = f"""
            SELECT collected_at AS timestamp, concurrent_players AS player_count
            FROM raw_concurrency
            WHERE game_name = '{GAME_NAME}'
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

def calculate_pubg_status(ccu_df):
    """동접자 기반 쾌적도 계산"""
    if ccu_df.empty:
        return "데이터 없음", 0
    
    ccu_now = int(ccu_df.iloc[-1]["player_count"])
    ccu_avg = int(ccu_df["player_count"].mean())
    ratio = ccu_now / ccu_avg
    
    if ratio >= 1.1: 
        return "쾌적", 90
    elif ratio >= 0.8: 
        return "보통", 60
    else: 
        return "혼잡", 30

def get_map_detailed_stats(match_df, map_id="All"):
    """
    map_id: ACTIVE_MAPS 키값, 'All'이면 통합 통계
    """
    if match_df.empty:
        return None

    df = match_df.copy()
    if map_id != "All":
        df = df[df['map_name'] == map_id]

    if df.empty:
        return None

    return {
        "avg_kills": df['avg_kills'].mean(),
        "max_kills_peak": df['max_kills'].max(),
        "kill_volatility": df['kill_std'].mean() if 'kill_std' in df.columns else 0,
        "bot_pct": df['bot_ratio'].mean() * 100,
        "avg_players": df['total_players'].mean(),
        "survival_avg": df['avg_survival_time'].mean() / 60,
        "survival_std": df['survival_std'].mean() / 60 if 'survival_std' in df.columns else 0,
        "match_duration": df['duration'].mean() / 60 if 'duration' in df.columns else 0,
        "total_matches": len(df)
    }