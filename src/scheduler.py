import time
import schedule
from datetime import datetime
import sys
import os

# 현재 파일(scheduler.py)이 있는 src 폴더의 절대 경로를 계산
current_dir = os.path.dirname(os.path.abspath(__file__))

# 파이썬 경로 리스트의 맨 앞에 src 폴더를 추가 (가장 높은 우선순위)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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