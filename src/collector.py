import os
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import random
from collections import deque

# 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("PUBG_API_KEY")
PLATFORM = "steam"
BASE_URL = f"https://api.pubg.com/shards/{PLATFORM}"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/vnd.api+json"}

# 파일/폴더 경로
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_MATCH_DIR = BASE_DIR / "data" / "raw" / "matches"
RAW_MATCH_DIR.mkdir(parents=True, exist_ok=True)

COLLECTED_PLAYERS_FILE = BASE_DIR / "collected_player_ids.txt"
COLLECTED_MATCH_FILE = BASE_DIR / "collected_match_ids.txt"
QUEUE_FILE = BASE_DIR / "pending_queue.txt"
SEED_FILE = BASE_DIR / "seed_players.txt"

def load_list(path):
    if not path.exists(): 
        return set()
    with open(path, "r") as f: 
        return set(line.strip() for line in f if line.strip())

def save_queue(pending_queue):
    with open(QUEUE_FILE, "w") as f:
        f.write("\n".join(pending_queue))

def run_collector():
    collected_players = load_list(COLLECTED_PLAYERS_FILE)
    collected_matches = load_list(COLLECTED_MATCH_FILE)
    pending_queue = deque(load_list(QUEUE_FILE))

    # 대기열이 비었으면 시드 보충
    if not pending_queue:
        seeds = load_list(SEED_FILE)
        pending_queue.extend([s for s in seeds if s not in collected_players])

    print(f"🚀 수집 시작! 초기 대기열: {len(pending_queue)}명")

    while True:  # 무한 수집
        if not pending_queue:
            # 큐 비면 시드 다시 넣기
            seeds = load_list(SEED_FILE)
            pending_queue.extend([s for s in seeds if s not in collected_players])
            if not pending_queue:
                print("큐가 비었습니다. 시드 플레이어가 없습니다. 1분 후 재시도...")
                time.sleep(60)
                continue

        player_id = pending_queue.popleft()
        if player_id in collected_players:
            continue

        print(f"\n[유저 처리 중] ID: {player_id}")

        # --- 플레이어 매치 목록 가져오기 ---
        for attempt in range(3):  # 최대 3회 재시도
            try:
                res = requests.get(f"{BASE_URL}/players/{player_id}", headers=HEADERS)
                if res.status_code == 429:
                    print("429 Too Many Requests 발생, 1분 대기...")
                    time.sleep(60)
                    continue
                elif res.status_code != 200:
                    print(f"플레이어 API 실패: {res.status_code}")
                    break
                player_data = res.json()
                break
            except requests.exceptions.RequestException as e:
                print(f"플레이어 요청 예외: {e}, 5초 후 재시도")
                time.sleep(5)
        else:
            # 3회 실패 시 스킵
            pending_queue.append(player_id)
            continue

        match_ids = [m["id"] for m in player_data.get("data", {}).get("relationships", {}).get("matches", {}).get("data", [])][:5]

        for m_id in match_ids:
            if m_id in collected_matches:
                continue

            # --- 매치 상세 데이터 가져오기 ---
            for attempt in range(3):
                try:
                    m_res = requests.get(f"{BASE_URL}/matches/{m_id}", headers=HEADERS)
                    if m_res.status_code == 429:
                        print("429 Too Many Requests 발생, 1분 대기...")
                        time.sleep(60)
                        continue
                    elif m_res.status_code != 200:
                        print(f"매치 API 실패: {m_res.status_code} (match {m_id})")
                        break
                    match_data = m_res.json()
                    break
                except requests.exceptions.RequestException as e:
                    print(f"매치 요청 예외: {e}, 5초 후 재시도")
                    time.sleep(5)
            else:
                # 3회 실패 시 스킵
                continue

            # --- 참가자 수 체크 (50명 이하 건너뛰기) ---
            participants = [p for p in match_data.get("included", []) if p.get("type")=="participant"]
            if len(participants) <= 45:
                print(f"매치 {m_id} 참가자 {len(participants)}명 → 건너뜀")
                continue  # 매치 건너뛰기

            # --- 파일 저장 ---
            with open(RAW_MATCH_DIR / f"{m_id}.json", "w") as f:
                json.dump(match_data, f)
            collected_matches.add(m_id)
            with open(COLLECTED_MATCH_FILE, "a") as f:
                f.write(m_id + "\n")

            # --- 새로운 플레이어 추출 ---
            new_faces = []
            for item in participants:
                p_id = item.get("relationships", {}).get("player", {}).get("data", {}).get("id")
                if not p_id:
                    stats = item.get("attributes", {}).get("stats", {})
                    p_id = stats.get("playerId") or stats.get("name")
                if p_id and not p_id.startswith("ai.") and p_id not in collected_players:
                    new_faces.append(p_id)

            # 최대 5명 랜덤 큐 추가
            random.shuffle(new_faces)
            added_count = 0
            for nf in new_faces[:5]:
                if nf not in pending_queue:
                    pending_queue.append(nf)
                    added_count += 1

            print(f"   - 매치 {m_id} 완료: 새 플레이어 발견 {len(new_faces)}명, 큐 추가 {added_count}명")
            time.sleep(1)  # API 부담 완화

        collected_players.add(player_id)
        with open(COLLECTED_PLAYERS_FILE, "a") as f:
            f.write(player_id + "\n")

        # 중간 저장
        save_queue(pending_queue)

        print(f"현재 대기열: {len(pending_queue)}명, 수집 완료 플레이어: {len(collected_players)}명")
        time.sleep(1)  # API 부담 완화

if __name__ == "__main__":
    run_collector()
