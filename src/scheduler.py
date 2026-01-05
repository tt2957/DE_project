import time
import schedule
from datetime import datetime
import sys
import os
from pathlib import Path
# 현재 파일(scheduler.py)이 있는 src 폴더의 절대 경로를 계산
current_file_path = Path(__file__).resolve()

# 2. 부모 폴더(src)의 부모(Root)를 찾습니다.
# .parent는 src/, .parent.parent는 Root/ 입니다.
BASE_DIR = current_file_path.parent.parent

# 3. 이제 Root에서 db 폴더로 들어갑니다.
DB_PATH = BASE_DIR / "db" / "steam.duckdb"
CONFIG_PATH = BASE_DIR / "config" / "games.json"

# 3. 파이썬 경로 설정
# 메인 파일과 utils를 찾기 위해 루트와 src를 모두 등록합니다.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

import main 
import importlib

def job():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now}] === 10분 주기 수집 사이클 시작 ===")
    try:
        importlib.reload(main)
        main.collect()
        print(f"[{now}] === 사이클 완료! ===")
    except Exception as e:
        print(f"[{now}] 에러 발생: {e}")

schedule.every(10).minutes.do(job)
job() # 즉시 시작

print("\n🚀 스케줄러 가동 중 (src 폴더 통합 버전)")
while True:
    schedule.run_pending()
    time.sleep(1)