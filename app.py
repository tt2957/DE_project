from datetime import timedelta
import streamlit as st
import apex_logic as al
import pubg_logic as pl # 배그 로직 임포트
import pandas as pd
import steam_logic as sl
import plotly.express as px
# =========================
# 1. 초기 설정 및 페이지 상태
# =========================
st.set_page_config(page_title="Gaming Data Hub", layout="wide", page_icon="🎮")

if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# 게임별 메타데이터 (아이콘 URL 및 설명)
# 팁: 나중에 직접 찍은 스크린샷이나 로컬 파일 경로로 교체 가능합니다.
GAMES_CONFIG = {
    "Apex Legends": {
        "img": "https://i.namu.wiki/i/XWkJjcOQb1SdUrUnaBPwNr8ZbylfkHutHiY89ViXgQI5lb3mtnK3WVtl73gB50FWi2AI9_ySzOROdaLJ2szX3g.webp",
    },
    "PUBG": {
        "img": "https://i.namu.wiki/i/-39mmyx2w53w1_YD7TH5AM55BukpjzibRZxSHbQOCTwdtNj8mxq2ZkxQrInLHr5WvR3wR9CuUEMSAon11jQ3aA.webp",
    },
    "Counter-Strike 2": {
        "img": "https://i.namu.wiki/i/bO3yoP9X2Q2mmBli4mn80ku4xVRFQO0-WrG5gWH1MGwEZNFrTRlrndctF4O8McBL8RqmRnkxIZxKe91ZQ_Yi-g.webp",
    },
    "Tekken 8": {
        "img": "https://images.start.gg/images/profileWidgetPageLayout/2513195/image-3ef196c3446d5835f58f25e55c2c507c.png?ehk=bGNyqRCiZ7pzhqR6N3l6VWL0iKq2Gjg6d477%2B1%2FBgNk%3D&ehkOptimized=DYCCd4k%2B37bWOoQ1kILYP344aRKFwWWMRnBW9MXYRSQ%3D",
    },
    "Dota 2": {
        "img": "https://seekvectors.com/files/download/dota-2-logo.png",
    },
    "FC 26": {
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/EAFC26_SEASONAL_SOLID_CHALK_WHITE_HORIZONTAL_RGB.svg/1024px-EAFC26_SEASONAL_SOLID_CHALK_WHITE_HORIZONTAL_RGB.svg.png", # 예시 로고
    },

}

st.markdown("""
    <style>
    /* 1. 이미지 설정: 자르지 않고(contain) 높이를 제한 */
    div[data-testid="stImage"] img {
        height: 120px; /* 높이를 더 줄여서 한 화면에 많이 보이게 함 */
        object-fit: contain; /* 핵심: 이미지를 자르지 않고 비율 유지하며 전체 노출 */
        padding: 5px;
    }
    
    /* 2. 카드 컨테이너 설정: 전체적인 높이를 슬림하게 조절 */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        min-height: 280px; /* 카드의 최소 높이를 줄임 */
        padding: 10px !important;
    }

    /* 3. 제목 크기 조절: 화면 공간 확보 */
    h3 {
        font-size: 1.1rem !important;
        margin-bottom: 5px !important;
    }
    
    /* 4. 버튼 상단 여백 조절 */
    .stButton button {
        margin-top: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

def go_to_page(name):
    st.session_state.page = name
    st.rerun()

# =========================
# 2. 메인 화면 (게임 아이콘 선택)
# =========================
if st.session_state.page == 'Home':
    st.markdown("<h1 style='text-align: center;'>🎮 GAME DATA HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>데이터로 분석하는 최적의 게이밍 환경</p>", unsafe_allow_html=True)
    st.divider()

    # 4열 그리드로 배치
    cols = st.columns(4)
    
    for i, (game_name, info) in enumerate(GAMES_CONFIG.items()):
        with cols[i % 4]:
            # 카드 형태의 컨테이너
            with st.container(border=True):
                st.image(info["img"], width='stretch')
                st.subheader(game_name)
                if st.button("분석 시작", key=f"btn_{game_name}", width='stretch'):
                    go_to_page(game_name)



# =========================
# 3. 개별 페이지: Apex Legends
# =========================
elif st.session_state.page == "Apex Legends":
    if st.sidebar.button("⬅️ 메인으로 돌아가기"):
        go_to_page('Home')

    st.title("🎯 Apex Legends 실시간 환경 분석")
    
    # 데이터 로드
    df_full = al.load_full_dataframe()
    latest_timestamp = df_full['timestamp'].max()
    
    # 최근 6시간 데이터 필터링
    six_hours_ago = latest_timestamp - pd.Timedelta(hours=6)
    recent_6h_df = df_full[df_full['timestamp'] >= six_hours_ago].copy()

    # 사이드바 설정 (서버/티어/파티)
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ 분석 설정")
    server = st.sidebar.selectbox("접속 서버", list(al.SERVER_DISTRIBUTION.keys()))
    tier = st.sidebar.selectbox("현재 티어", al.TIER_ORDER, index=16)
    party = st.sidebar.radio("파티 구성", [1, 2, 3], format_func=lambda x: f"{x}인큐")

    # 지표 계산
    target_idx = df_full.index[-1] 
    ccu_at_time = int(df_full.iloc[target_idx]["player_count"])
    ccu_60_avg = int(df_full.iloc[max(0, target_idx-11):target_idx+1]["player_count"].mean())
    ccu_global_avg = int(df_full["player_count"].mean())

    q_min, q_lab, m_score, m_lab, h_risk, h_lab, c_score, c_lab, p_now = al.calculate_metrics(
        tier, server, party, ccu_at_time, ccu_60_avg, ccu_global_avg
    )

    # =========================
    # [추가] 쾌적도 상태별 색상 신호등 로직
    # =========================
    if c_lab == "쾌적":
        status_color = "#28A745" # 초록색
        status_emoji = "🟢"
    elif c_lab == "보통":
        status_color = "#FFC107" # 노란색
        status_emoji = "🟡"
    else: # "혼잡" (나쁨)
        status_color = "#DC3545" # 빨간색
        status_emoji = "🔴"

    # 결과 대시보드 출력 (색상 표시 포함)
    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 15px; border-left: 10px solid {status_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="margin: 0; color: #1E293B;">{status_emoji} 현재 상태: <span style="color: {status_color};">{c_lab}</span></h2>
            <p style="margin: 5px 0 0 0; color: #64748B;">업데이트 시각: {latest_timestamp.strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # 간격 조절
    st.progress(c_score / 100)

    m1, m2, m3 = st.columns(3)
    m1.metric("⏱️ 예상 큐 대기", f"{q_min}분", q_lab)
    m2.metric("🎯 매칭 품질", f"{m_score}점", m_lab)
    m3.metric("🛡️ 페어플레이", f"{100 - h_risk:.1f}점", h_lab)

    st.divider()
    
    st.subheader("📈 실시간 동접자 추이 (드래그하여 과거 데이터 탐색)")

            # 1. Plotly 선 그래프 생성
    fig = px.line(df_full, x='timestamp', y='player_count', 
                labels={'timestamp': '시간', 'player_count': '동접자 수'},
                template="plotly_white")

    # 2. 초기 보여줄 범위 설정 (최근 6시간)
    latest_time = df_full['timestamp'].max()
    six_hours_ago = latest_time - timedelta(hours=6)

    fig.update_xaxes(
        range=[six_hours_ago, latest_time], # 처음에 보여줄 X축 범위
        rangeslider_visible=True,           # 하단에 전체 범위를 보여주는 슬라이더 추가
        type="date"
    )

    # 3. 레이아웃 최적화 (여백 줄이기 등)
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=450,
        hovermode="x unified" # 마우스 올렸을 때 수치 표시 방식
    )

    # 4. 차트 출력
    st.plotly_chart(fig, width='stretch')
    

elif st.session_state.page == "PUBG":
    # 배그 내부 서브 페이지 상태 초기화
    if 'pubg_sub' not in st.session_state:
        st.session_state.pubg_sub = 'MapGrid'
    if 'selected_map' not in st.session_state:
        st.session_state.selected_map = None

    # 사이드바 공통 메뉴
    if st.sidebar.button("⬅️ 메인 홈으로"):
        go_to_page('Home')
    st.markdown("""
    <style>

    /* 2. 카드 설정: 이미지가 커졌으므로 전체 높이도 늘림 */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        background-color: #FFFFFF !important; 
        border: 2px solid #CBD5E1 !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important;
        min-height: 400px; /* [수정] 300px -> 400px로 증가 */
        padding: 20px !important;
        transition: transform 0.2s ease;
    }

    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"]:hover {
        transform: translateY(-5px);
        border: 2px solid #4A90E2 !important;
    }

    /* 3. 이미지 설정: 높이를 대폭 키워 사진을 강조 */
    div[data-testid="stImage"] img {
        height: 450px; /* [수정] 120px -> 250px로 대폭 증가 */
        object-fit: contain; /* 정사각형 맵 이미지가 잘리지 않고 꽉 차게 보임 */
        padding: 5px;
        background-color: #0e1117;
        border-radius: 10px;
        margin-bottom: 15px; /* 이미지 아래 여백 추가 */
    }
    
    }
    </style>
    """, unsafe_allow_html=True)
    if st.session_state.pubg_sub == 'MapDetail':
        if st.sidebar.button("🗺️ 다른 맵 선택하기"):
            st.session_state.pubg_sub = 'MapGrid'
            st.rerun()

    # ---------------------------------------------------------
    # 1단계: 맵 선택 그리드 (Map Grid View)
    # ---------------------------------------------------------
    if st.session_state.pubg_sub == 'MapGrid':
        st.title("🗺️ PUBG 전장 선택")
        st.write("분석 리포트를 확인할 맵을 선택하세요.")
        st.divider()

        cols = st.columns(3) # 3열 그리드
        with cols[0]:
            with st.container(border=True):
            # 통합 분석용 아이콘 이미지 (원하시는 URL로 교체 가능)
                st.image("https://logodownload.org/wp-content/uploads/2019/12/pubg-logo-0.png", width='stretch')
                st.subheader("🌐 전체 통합 분석")
                if st.button("통합 리포트 보기", key="btn_all_maps", width='stretch'):
                    st.session_state.selected_map = "All" # 전체 통합용 키값
                    st.session_state.pubg_sub = 'MapDetail'
                    st.rerun()

    # --- 기존 맵 카드들 (두 번째 칸부터 순차적으로 배치) ---
        for i, (m_id, m_info) in enumerate(pl.ACTIVE_MAPS.items()):
        # i+1 을 하여 통합 카드 다음 칸부터 배치함
            with cols[(i + 1) % 3]:
                with st.container(border=True):
                    st.image(m_info['img'], width='stretch')
                    st.subheader(m_info['name'])
                    if st.button(f"{m_info['name']} 리포트 보기", key=f"btn_{m_id}", width='stretch'):
                        st.session_state.selected_map = m_id
                        st.session_state.pubg_sub = 'MapDetail'
                        st.rerun()

    elif st.session_state.pubg_sub == 'MapDetail':
        m_id = st.session_state.selected_map
        
        # 상단 제목 설정
        if m_id == "All":
            m_name = "글로벌 통합"
            st.title(f"📊 PUBG 전 서버 통합 데이터 보고서")
        else:
            m_name = pl.ACTIVE_MAPS[m_id]['name']
            st.title(f"📊 {m_name} 구역 정밀 분석")

        # 데이터 로드
        ccu_df = pl.load_ccu_data()
        match_df = pl.load_match_data()

        # 사이드바 필터 (모드 및 팀 구성)
        st.sidebar.subheader("⚙️ 분석 필터")
        play_mode = st.sidebar.radio("모드 선택", ["일반전", "경쟁전"])
        team_type = st.sidebar.selectbox("팀 구성", ["솔로 (Solo)", "듀오 (Duo)", "스쿼드 (Squad)"])
        team_filter = team_type.split(" (")[1].replace(")", "").lower()

        # [로직] 선택된 맵 및 사이드바 필터에 따른 데이터 필터링
        filtered_df = match_df.copy()

        # 1. 맵 필터링 (통합 분석이 아닐 경우에만)
        if m_id != "All":
            filtered_df = filtered_df[filtered_df['map_name'] == m_id]

        # 2. 팀 구성 및 모드 필터링
        if not filtered_df.empty:
            filtered_df = filtered_df[filtered_df['game_mode'].str.contains(team_filter, case=False, na=False)]
            if play_mode == "경쟁전":
                filtered_df = filtered_df[filtered_df['game_mode'].str.contains("competitive", case=False, na=False)]
            else:
                filtered_df = filtered_df[~filtered_df['game_mode'].str.contains("competitive", case=False, na=False)]

        # 3. 필터링 적용 후 맵 전용 통계 계산
        m_stats = pl.get_map_detailed_stats(filtered_df, map_id="All" if m_id=="All" else m_id)

        # A. 서버 상태 (신호등)
        c_lab, c_score = pl.calculate_pubg_status(ccu_df)
        if c_lab == "쾌적":
            status_color = "#28A745" # 초록색DB_PATH = os.path.join(os.path.dirname(__file__), "db", "steam.duckdb")
            status_emoji = "🟢"
        elif c_lab == "보통":
            status_color = "#FFC107" # 노란색
            status_emoji = "🟡"
        else: # "혼잡" (나쁨)
            status_color = "#DC3545" # 빨간색
            status_emoji = "🔴"
        
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 15px; border-left: 10px solid {status_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h2 style="margin: 0; color: #1E293B;">{status_emoji}현시각 {m_name} 매칭 상태: <span style="color: {status_color};">{c_lab}</span></h2>
                <p style="margin: 5px 0 0 0; color: #64748B;">글로벌 동접자 기반 혼잡도 분석 결과입니다.</p>
            </div>
        """, unsafe_allow_html=True)
        # B. 맵 전용 메트릭
        st.write("")
        m1, m2, m3 = st.columns(3)
        if m_stats:
            m1.metric("🤖 봇 비중", f"{m_stats['bot_pct']:.1f}%")
            m2.metric("⚔️ 평균 킬", f"{m_stats['avg_kills']:.2f}")
            m3.metric("⏱️ 평균 생존", f"{m_stats['survival_avg']:.1f}분")
        
        st.divider()

        # C. 동접자 추이 그래프
        if not ccu_df.empty:
            st.subheader("📈 실시간 동접자 추이 (드래그하여 과거 데이터 탐색)")

            # 1. Plotly 선 그래프 생성
            fig = px.line(ccu_df, x='timestamp', y='player_count', 
                        labels={'timestamp': '시간', 'player_count': '동접자 수'},
                        template="plotly_white")

            # 2. 초기 보여줄 범위 설정 (최근 6시간)
            latest_time = ccu_df['timestamp'].max()
            six_hours_ago = latest_time - timedelta(hours=6)

            fig.update_xaxes(
                range=[six_hours_ago, latest_time], # 처음에 보여줄 X축 범위
                rangeslider_visible=True,           # 하단에 전체 범위를 보여주는 슬라이더 추가
                type="date"
            )

            # 3. 레이아웃 최적화 (여백 줄이기 등)
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=450,
                hovermode="x unified" # 마우스 올렸을 때 수치 표시 방식
            )

            # 4. 차트 출력
            st.plotly_chart(fig, width='stretch')

# =========================
# 4. 스팀기반게임들
# =========================

steam_games = ["Counter-Strike 2", "Tekken 8", "Dota 2", "FC 26", "GTA 5"]

if st.session_state.page in steam_games:
    game_name = st.session_state.page 
    
    if st.sidebar.button("⬅️ 메인으로 돌아가기"):
        go_to_page('Home')

    # 1. 데이터 로드 (클릭된 게임 이름 전달)
    df_ccu = sl.load_ccu_data(game_name)
    
    # 데이터가 비어있는지 확인하는 방어 코드 추가
    if df_ccu.empty:
        st.error(f"❌ {game_name}의 데이터를 DB에서 찾을 수 없습니다. (DB명 확인 필요)")
    else:
        # 데이터가 있을 때만 계산 및 출력
        status_lab, status_score, status_desc, ccu_now = sl.calculate_steam_status(df_ccu)

    # 3. UI 출력 (에이펙스/배그 디자인과 동일)
    if status_lab == "쾌적":
        status_color, status_emoji = "#28A745", "🟢"
    elif status_lab == "보통":
        status_color, status_emoji = "#FFC107", "🟡"
    else:
        status_color, status_emoji = "#DC3545", "🔴"

    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 15px; border-left: 10px solid {status_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="margin: 0; color: #1E293B;">{status_emoji} {game_name} 상태: <span style="color: {status_color};">{status_lab}</span></h2>
            <p style="margin: 5px 0 0 0; color: #64748B;">현재 {ccu_now:,}명이 플레이 중입니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.progress(status_score / 100)

    m1, m2, m3 = st.columns(3)
    m1.metric("👥 현재 접속자", f"{ccu_now:,}명")
    m2.metric("📊 쾌적도 점수", f"{status_score}점")
    m3.metric("📢 안내", status_lab, status_desc)

    st.divider()

    # 4. 차트 출력
    if not df_ccu.empty:
        st.subheader("📈 실시간 동접자 추이 (드래그하여 과거 데이터 탐색)")

        # 1. Plotly 선 그래프 생성
        fig = px.line(df_ccu, x='timestamp', y='player_count', 
                    labels={'timestamp': '시간', 'player_count': '동접자 수'},
                    template="plotly_white")

        # 2. 초기 보여줄 범위 설정 (최근 6시간)
        latest_time = df_ccu['timestamp'].max()
        six_hours_ago = latest_time - timedelta(hours=6)

        fig.update_xaxes(
            range=[six_hours_ago, latest_time], # 처음에 보여줄 X축 범위
            rangeslider_visible=True,           # 하단에 전체 범위를 보여주는 슬라이더 추가
            type="date"
        )

        # 3. 레이아웃 최적화 (여백 줄이기 등)
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=450,
            hovermode="x unified" # 마우스 올렸을 때 수치 표시 방식
        )

        # 4. 차트 출력
        st.plotly_chart(fig, width='stretch')
