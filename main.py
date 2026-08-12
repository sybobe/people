import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# 1. 페이지 기본 설정 (웹 브라우저 탭 제목, 레이아웃)
# ---------------------------------------------------------
st.set_page_config(
    page_title="동네별 총인구 분포 확인하기", page_icon="📊", layout="wide"
)

# 메인 화면 제목 및 설명
st.title("📊 우리 동네 인구 분포(퍼짐) 살펴보기")
st.write(
    "주민등록 인구통계 데이터를 활용하여 전국 읍·면·동별 총인구수의 퍼짐 정도(분포)를 살펴봅니다."
)


# ---------------------------------------------------------
# 2. 데이터 불러오기 및 전처리 함수 (st.cache_data로 캐싱 적용)
# ---------------------------------------------------------
@st.cache_data
def load_and_preprocess_data():
    # 데이터 출처 URL (.csv.gz 압축 파일이지만 판다스가 자동으로 압축을 풀어서 읽습니다)
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/population_yearly.csv.gz"

    # 판다스로 CSV 읽어오기 (EUC-KR/CP949 또는 UTF-8 자동 대응)
    try:
        df = pd.read_csv(url, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding="cp949")

    # '연도' 열에서 가장 최신 연도 데이터만 선택
    if "연도" in df.columns:
        latest_year = df["연도"].max()
        df = df[df["연도"] == latest_year].copy()

    # '남_' 및 '여_'로 시작하는 나이별 인구 열 찾기
    male_cols = [c for c in df.columns if str(c).startswith("남_")]
    female_cols = [c for c in df.columns if str(c).startswith("여_")]

    # 동네(행)별로 남/여 인구를 모두 더해서 '총인구' 열 생성
    df["총인구"] = df[male_cols + female_cols].sum(axis=1)

    return df


# 데이터 불러오기 실행
with st.spinner("데이터를 불러오고 처리하는 중입니다..."):
    df = load_and_preprocess_data()

st.success("데이터를 성공적으로 불러왔습니다!")

st.markdown("---")

# ---------------------------------------------------------
# 3. 화면 구성 1: 총인구 describe() 결과 표
# ---------------------------------------------------------
st.subheader("1. 총인구 요약 통계량 (describe)")
st.write(
    "전국 읍·면·동 총인구수의 평균, 중앙값, 최솟값, 최댓값 등의 대표적인 요약 통계입니다."
)

# describe() 수행 및 데이터프레임 정리
stats_df = df[["총인구"]].describe().reset_index()
stats_df.columns = ["통계 항목", "총인구(명)"]

# 통계 항목 이름 초보자용 한국어로 매핑
korean_stats = {
    "count": "동네 개수 (count)",
    "mean": "평균 인구수 (mean)",
    "std": "표준편차 (std)",
    "min": "최소 인구수 (min)",
    "25%": "1분위수 (하위 25%)",
    "50%": "중앙값 (50%)",
    "75%": "3분위수 (상위 25%)",
    "max": "최대 인구수 (max)",
}
stats_df["통계 항목"] = stats_df["통계 항목"].map(
    lambda x: korean_stats.get(x, x)
)

# Streamlit 표 형태로 출력
st.dataframe(stats_df, use_container_width=True)

st.markdown("---")

# 따뜻한 톤 스타일링 색상 (메인: 코랄 오렌지 / 배경: 따뜻한 크림)
warm_color_main = "#E07A5F"
warm_color_bg = "#FAF8F5"

# ---------------------------------------------------------
# 4. 화면 구성 2: 총인구 히스토그램 (Plotly)
# ---------------------------------------------------------
st.subheader("2. 총인구 히스토그램")
st.write(
    "인구 구간별로 몇 개의 동네(읍·면·동)가 속해 있는지 전체적인 모양과 퍼짐을 보여줍니다."
)

fig_hist = px.histogram(
    df,
    x="총인구",
    nbins=50,
    title="전국 읍·면·동 총인구수 분포 (히스토그램)",
    labels={"총인구": "총인구수 (명)", "count": "동네 수"},
    color_discrete_sequence=[warm_color_main],
)

# 그래프 레이아웃 및 따뜻한 톤 커스텀
fig_hist.update_layout(
    plot_bgcolor=warm_color_bg,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    xaxis_title="총인구수 (명)",
    yaxis_title="동네 수 (개)",
    hovermode="x unified",
)

st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 5. 화면 구성 3: 총인구 상자그림 (Box Plot) (Plotly)
# ---------------------------------------------------------
st.subheader("3. 총인구 상자그림 (Box Plot)")
st.write(
    "중앙값, 사분위 범위, 그리고 인구수가 유독 많거나 적은 이상치 지역을 한눈에 구별할 수 있습니다."
)

fig_box = px.box(
    df,
    y="총인구",
    title="전국 읍·면·동 총인구수 상자그림",
    labels={"총인구": "총인구수 (명)"},
    color_discrete_sequence=[warm_color_main],
    points="outliers",  # 이상치 데이터 점으로 표시
)

# 그래프 레이아웃 및 따뜻한 톤 커스텀
fig_box.update_layout(
    plot_bgcolor=warm_color_bg,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    yaxis_title="총인구수 (명)",
)

st.plotly_chart(fig_box, use_container_width=True)
