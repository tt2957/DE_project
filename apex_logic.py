import duckdb
import pandas as pd
import math
import streamlit as st
from datetime import timedelta

# =========================
# 1. 설정 및 상수 정의
# =========================
import os 
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "steam.duckdb")
GAME_NAME = "Apex Legends"

TIER_ORDER = [
    "Bronze 4", "Bronze 3", "Bronze 2", "Bronze 1",
    "Silver 4", "Silver 3", "Silver 2", "Silver 1",
    "Gold 4", "Gold 3", "Gold 2", "Gold 1",
    "Platinum 4", "Platinum 3", "Platinum 2", "Platinum 1",
    "Diamond 4", "Diamond 3", "Diamond 2", "Diamond 1",
    "Master", "Predator"
]

TIER_DISTRIBUTION = {
    "Bronze 4": 4.728, "Bronze 3": 1.741, "Bronze 2": 1.774, "Bronze 1": 1.539,
    "Silver 4": 7.49, "Silver 3": 4.149, "Silver 2": 3.094, "Silver 1": 2.521,
    "Gold 4": 8.571, "Gold 3": 6.843, "Gold 2": 5.119, "Gold 1": 3.772,
    "Platinum 4": 7.011, "Platinum 3": 9.795, "Platinum 2": 8.431, "Platinum 1": 6.88,
    "Diamond 4": 6.671, "Diamond 3": 5.41, "Diamond 2": 1.288, "Diamond 1": 0.552,
    "Master": 0.646, "Predator": 0.42
}

SERVER_DISTRIBUTION = {"Tokyo": 0.60, "Taiwan": 0.25, "Singapore": 0.15}
SERVER_BASE_QUALITY = {"Tokyo": 1.00, "Taiwan": 0.95, "Singapore": 0.97}
SERVER_BASE_RISK = {"Tokyo": 0.8, "Taiwan": 1.0, "Singapore": 0.9}
PARTY_FACTOR_QUEUE = {1: 1.0, 2: 1.0, 3: 0.8}
PARTY_RISK = {1: 1.0, 2: 0.9, 3: 0.8}

# =========================
# 2. 데이터 처리 함수
# =========================

@st.cache_data(ttl=600)
def load_full_dataframe():
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

def get_expanded_tier_ratio(current_tier: str) -> float:
    try:
        idx = TIER_ORDER.index(current_tier)
        target_indices = {idx}
        if idx > 0: target_indices.add(idx - 1)
        if idx < len(TIER_ORDER) - 1: target_indices.add(idx + 1)
        combined_ratio = sum(TIER_DISTRIBUTION[TIER_ORDER[i]] for i in target_indices)
        return combined_ratio / 100
    except:
        return TIER_DISTRIBUTION.get(current_tier, 5.0) / 100

def tier_level(tier: str) -> int:
    if any(t in tier for t in ["Bronze", "Silver", "Gold"]): return 1
    if "Platinum" in tier: return 2
    if "Diamond" in tier: return 3
    return 4 

# =========================
# 3. 핵심 매칭 지표 계산
# =========================

def calculate_metrics(tier, server, party_size, ccu_now, ccu_60, ccu_avg):
    expanded_ratio = get_expanded_tier_ratio(tier)
    server_ratio = SERVER_DISTRIBUTION.get(server, 0.33)
    
    pool_now = ccu_now * expanded_ratio * server_ratio
    pool_eff = (0.65 * pool_now) + (0.35 * (ccu_60 * expanded_ratio * server_ratio))
    
    # 1. 큐 시간 계산
    effective_pool = max(pool_eff / PARTY_FACTOR_QUEUE[party_size], 1)
    K, MIN_WAIT = 2000, 20
    queue_sec = (K / math.log(effective_pool + 1)) * (1 + (500 / (effective_pool + 30)))
    if effective_pool < 3000: queue_sec *= 1.4
    queue_min = max(queue_sec, MIN_WAIT) / 60
    q_lab = "쾌속" if queue_min <= 3 else "보통" if queue_min <= 6 else "지연"

    # 2. 매칭 품질 점수
    mu_seg = 100000 * expanded_ratio * server_ratio
    sig_seg = 50000 * expanded_ratio * server_ratio
    dist = abs(pool_eff - mu_seg)
    q_pop = 0.8 * math.exp(-0.5 * (dist / (sig_seg * (1.0 if pool_eff < mu_seg else 1.5))) ** 2)
    low_pop_factor = max(0.5, min(1.0, pool_eff / max(1, ccu_avg * expanded_ratio * server_ratio)))

    party_map = {1: 0.7, 2: 0.80, 3: 0.90}
    t_lvl = tier_level(tier)
    q_party = max(0.55, party_map[party_size] - (0.07 * (t_lvl - 1) if party_size == 1 else 0))
    
    s_base = SERVER_BASE_QUALITY[server]
    if t_lvl <= 1 and server == "Taiwan": s_base += 0.03
    elif t_lvl >= 3:
        if server == "Tokyo": s_base += 0.03
        elif server == "Taiwan": s_base -= 0.15
    
    m_score = max(min(((q_pop * low_pop_factor) * 45) + (q_party * 30) + (max(0, min(1.0, s_base)) * 20), 100), 0)
    m_lab = "매우 좋음" if m_score >= 85 else "좋음" if m_score >= 65 else "보통" if m_score >= 40 else "나쁨"

    # 3. 핵 위험도 계산
    server_ccu = ccu_now * server_ratio
    r_pop = 1 / (1 + math.exp(-0.0001 * (server_ccu - (70000 * server_ratio))))
    r_tier = 0.2 * math.exp(0.5 * (t_lvl - 1))
    r_server = SERVER_BASE_RISK[server]
    if t_lvl >= 3:
        r_server *= (1.2 if server == "Taiwan" else 1.1)
    
    risk = max(min(100 * 1.5 * r_pop * r_tier * r_server * PARTY_RISK[party_size], 100), 0)
    h_lab = "청정" if risk < 30 else "주의" if risk < 55 else "위험"

    # 4. 종합 쾌적도 지수
    comfort = max(min((0.4 * m_score) + (0.25 * (200 * math.exp(-0.25 * queue_min))) + (0.35 * (100 - risk)), 100), 0)
    c_lab = "쾌적" if comfort >= 65 else "보통" if comfort >= 40 else "혼잡"

    return round(queue_min, 2), q_lab, round(m_score, 1), m_lab, round(risk, 1), h_lab, round(comfort, 1), c_lab, int(pool_now)