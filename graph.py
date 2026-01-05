import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

# --------------------------
# 0️⃣ 시각화 설정
# --------------------------
sns.set_theme(style="darkgrid")
plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14

# --------------------------
# 1️⃣ CSV 불러오기
# --------------------------
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "steam.duckdb")
df = pd.read_csv(DB_PATH, parse_dates=["created_at"])
print(f"총 매치 수: {len(df)}")
print(df.head())

# --------------------------
# 2️⃣ 시간대 전처리: UTC → KST
# --------------------------
df['created_at'] = df['created_at'] + timedelta(hours=9)  # UTC → KST
df['hour'] = df['created_at'].dt.hour

# bot_ratio 결측치 처리
df['bot_ratio'] = df['bot_ratio'].fillna(0)

# --------------------------
# 3️⃣ 맵별 매치 수
# --------------------------
map_name_dict = {
    "Tiger_Main": "태이고(Taego)",           #
    "Desert_Main": "미라마(Miramar)",         #
    "Baltic_Main": "에란겔(Erangel)",         #
    "DihorOtok_Main": "비켄디(Vikendi)",      #
    "Savage_Main": "사녹(Sanhok)",           #
    "Neon_Main": "론도(Rondo)",              #
    "Kiki_Main": "데스턴(Deston)",           #
    "Summerland_Main": "카라킨(Karakin)",     #
    "Chimera_Main": "파라모(Paramo)",         #
    "Heaven_Main": "헤이븐(Haven)",           #
    "Range_Main": "훈련장(Camp Jackal)",      #
    "PillarCompound_Main": "필라 컴파운드",    #
    "Italy_TDM_Main": "이탈리아(TDM)",
    "Boardwalk_Main": "보드워크(TDM)"
}

map_counts = df['map_name'].value_counts()
plot_data = map_counts.rename(index=lambda x: map_name_dict.get(x, x))

plt.figure(figsize=(10,5))
sns.barplot(x=plot_data.index, y=plot_data.values, palette="viridis")

plt.title("맵별 매치 수", fontsize=16)
plt.ylabel("매치 수", fontsize=12)
plt.xlabel("맵 이름", fontsize=12)
plt.xticks(rotation=30, ha='right', fontsize=10)
plt.tight_layout()
plt.show()

# --------------------------
# 4️⃣ 모드별 평균 생존 시간
# --------------------------
mode_survival = df.groupby("game_mode")["avg_survival_time"].mean().sort_values()
plt.figure(figsize=(8,5))
sns.barplot(x=mode_survival.index, y=mode_survival.values, palette="magma")
plt.title("모드별 평균 생존 시간", fontsize=16)
plt.ylabel("평균 생존 시간 (초)", fontsize=12)
plt.xlabel("게임 모드", fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# --------------------------
# 5️⃣ 평균 킬 분포
# --------------------------
plt.figure(figsize=(8,5))
sns.histplot(df["avg_kills"], bins=20, kde=True, color="skyblue")
plt.title("평균 킬 분포", fontsize=16)
plt.xlabel("평균 킬", fontsize=12)
plt.ylabel("매치 수", fontsize=12)
plt.tight_layout()
plt.show()

# --------------------------
# 6️⃣ 맵별 평균 킬 박스플롯
# --------------------------
plt.figure(figsize=(10,5))
sns.boxplot(x="map_name", y="avg_kills", data=df, palette="Set2")
plt.title("맵별 평균 킬 분포", fontsize=16)
plt.ylabel("평균 킬", fontsize=12)
plt.xlabel("맵 이름", fontsize=12)
plt.xticks(rotation=30, ha='right', fontsize=10)
plt.tight_layout()
plt.show()

# --------------------------
# 7️⃣ 봇 비율 vs 매치 지속 시간
# --------------------------
plt.figure(figsize=(8,5))
sns.scatterplot(x="bot_ratio", y="duration", data=df, hue="game_mode", palette="tab10", s=50)
plt.title("봇 비율과 매치 지속 시간 관계", fontsize=16)
plt.xlabel("봇 비율", fontsize=12)
plt.ylabel("매치 지속 시간 (초)", fontsize=12)
plt.legend(title="게임 모드", bbox_to_anchor=(1.05,1), loc='upper left')
plt.tight_layout()
plt.show()

# --------------------------
# 8️⃣ 시간대별 매치 수
# --------------------------
plt.figure(figsize=(10,5))
sns.countplot(x='hour', data=df, palette="coolwarm")
plt.title("시간대별 매치 수 (KST 기준)", fontsize=16)
plt.xlabel("시간 (24h)", fontsize=12)
plt.ylabel("매치 수", fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# --------------------------
# 9️⃣ 상관관계 히트맵
# --------------------------
corr_cols = ['avg_kills','kill_std','avg_survival_time','survival_std','duration','total_players','bot_ratio']
corr = df[corr_cols].corr()
plt.figure(figsize=(9,7))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, cbar=True)
plt.title("PUBG 매치 지표 상관관계", fontsize=16)
plt.tight_layout()
plt.show()
