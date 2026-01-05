import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import os 
# 1. DB 연결 및 데이터 로드
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "steam.duckdb")
con = duckdb.connect(DB_PATH)

query = """
SELECT game_name, concurrent_players, collected_at
FROM raw_concurrency
WHERE game_name = 'PUBG: Battlegrounds'
ORDER BY collected_at ASC
"""
df = con.execute(query).df()
con.close()

# 2. 전처리 (UTC → KST)
df['collected_at'] = pd.to_datetime(df['collected_at']) + timedelta(hours=9)

# 3. 그래프 생성
plt.figure(figsize=(15, 6))

for game in df['game_name'].unique():
    game_df = df[df['game_name'] == game]
    plt.plot(
        game_df['collected_at'],
        game_df['concurrent_players'],
        marker='o',
        linestyle='-',
        label=game
    )

# 4. X축을 "시간(시)" 단위로 포맷
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))   # 1시간 단위
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H시'))

# 5. 그래프 설정
plt.title("Concurrent Players Over Time (KST)", fontsize=16, fontweight='bold')
plt.xlabel("Time (KST)", fontsize=12)
plt.ylabel("Concurrent Players", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
