import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 페이지 기본 설정 (웹 브라우저 탭 제목, 아이콘, 넓은 레이아웃)
st.set_page_config(
    page_title="동네별 총인구 분포 확인하기", page_icon="📊", layout="wide"
)

# 앱 메인 타이틀 및 간단한 설명
st.title("📊 우리 동네 인구 분포(퍼짐) 살펴보기")
st.write(
    "주민등록 인구통계 데이터를 활용하여 전국 읍·면·동별 총인구수 분포와 데이터의 '퍼짐'을 시각화합니다."
)


# 2. 데이터 불러오기 및 전처리 함수 (캐싱 적용으로 매번 다시 읽지 않고 속도 향상)
@st.cache_data
def load_and_preprocess_data():
    # 데이터 URL (gzip 압축된 CSV 파일이지만 판다스가 자동으로 압축 해제 후 로드함)
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/population_yearly.csv.gz"

    # CSV 파일 읽기 (한글 인코딩 예외 처리)
    try:
        df = pd.read_csv(url, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding="cp949")

    # '연도' 열에서 가장 최신 연도 데이터만 필터링하여 남김
    if "연도" in df.columns:
        latest_year = df["연도"].max()
        df = df[df["연도"] == latest_year].copy()

    # '남_'으로 시작하는 열과 '여_'로 시작하는 열의 이름 목록 추출
    male_cols = [c for c in df.columns if str(c).startswith("남_")]
    female_cols = [c for c in df.columns if str(c).startswith("여_")]

    # 동네별(행별) 총 남인구 및 총 여인구 계산
    df["남인구"] = df[male_cols].sum(axis=1)
    df["여인구"] = df[female_cols].sum(axis=1)

    # 행(동네)마다 남/여 나이별 인구를 모두 더해 '총인구' 열 생성
    df["총인구"] = df["남인구"] + df["여인구"]

    return df


# 데이터 읽어오기 실행 및 안내 메시지
with st.spinner("데이터를 불러오는 중입니다... 잠시만 기다려주세요."):
    df = load_and_preprocess_data()

st.success("데이터를 성공적으로 불러왔습니다!")
st.markdown("---")

# 따뜻한 톤 스타일 색상 설정 (주요 색상: 코랄/오렌지, 배경: 소프트 크림)
warm_main_color = "#E07A5F"
warm_bg_color = "#F4F1DE"

# ---------------------------------------------------------
# 1. 총인구 기술통계량 (describe) 결과 표
# ---------------------------------------------------------
st.subheader("1. 총인구 요약 통계량 (describe)")
st.write(
    "전국 읍·면·동 총인구수의 평균, 중앙값, 최솟값, 최댓값 등 데이터의 대표적인 요약 통계 수치입니다."
)

# describe() 수행 후 보기 좋게 변환
stats_df = df[["총인구"]].describe().reset_index()
stats_df.columns = ["통계 항목", "총인구(명)"]

# 통계 항목 용어를 한국어로 알기 쉽게 변경
korean_stats_map = {
    "count": "동네 개수 (count)",
    "mean": "평균 인구수 (mean)",
    "std": "표준편차 (std)",
    "min": "최소 인구수 (min)",
    "25%": "1분위수 (25%)",
    "50%": "중앙값 (50%)",
    "75%": "3분위수 (75%)",
    "max": "최대 인구수 (max)",
}
stats_df["통계 항목"] = stats_df["통계 항목"].map(
    lambda x: korean_stats_map.get(x, x)
)

# 스트림릿 표 출력
st.dataframe(stats_df, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 2. 총인구 히스토그램 (Plotly 인터랙티브 그래프)
# ---------------------------------------------------------
st.subheader("2. 총인구 히스토그램")
st.write(
    "인구수 구간별로 몇 개의 동네(읍·면·동)가 속해 있는지 데이터의 퍼짐 상태를 분포 형태(기둥)로 보여줍니다."
)

# Plotly 히스토그램 생성
fig_hist = px.histogram(
    df,
    x="총인구",
    nbins=50,
    title="전국 읍·면·동 총인구수 분포 (히스토그램)",
    labels={"총인구": "총인구수 (명)", "count": "동네 수"},
    color_discrete_sequence=[warm_main_color],
)

# 따뜻한 톤 레이아웃 및 한글 라벨 설정
fig_hist.update_layout(
    plot_bgcolor=warm_bg_color,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    xaxis_title="총인구수 (명)",
    yaxis_title="동네 수 (개)",
    hovermode="x unified",
)

# 스트림릿 화면에 그래프 출력
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 3. 총인구 상자그림 (Box Plot) (Plotly 인터랙티브 그래프)
# ---------------------------------------------------------
st.subheader("3. 총인구 상자그림 (Box Plot)")
st.write(
    "데이터의 중앙값, 분위수 범위(상자) 및 인구수가 매우 많거나 적은 이상치(점) 지역을 한눈에 볼 수 있습니다."
)

# Plotly 상자그림 생성
fig_box = px.box(
    df,
    y="총인구",
    title="전국 읍·면·동 총인구수 상자그림",
    labels={"총인구": "총인구수 (명)"},
    color_discrete_sequence=[warm_main_color],
    points="outliers",  # 이상치 점만 강조 표시
)

# 따뜻한 톤 레이아웃 설정
fig_box.update_layout(
    plot_bgcolor=warm_bg_color,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    yaxis_title="총인구수 (명)",
)

# 스트림릿 화면에 그래프 출력
st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 4. 시도별 총인구 합산 막대그래프 (Plotly)
# ---------------------------------------------------------
st.subheader("4. 시도별 총인구 합산 막대그래프")
st.write(
    "행정구역(시도)별로 전체 인구를 합산하여 어디에 인구가 집중되어 있는지 비교합니다. 수도권(경기·서울)과 지방 간의 극심한 인구 규모 격차를 한눈에 확인할 수 있습니다."
)

# 시도별 총인구 합산 후 내림차순 정렬
sido_df = (
    df.groupby("시도", as_index=False)["총인구"]
    .sum()
    .sort_values(by="총인구", ascending=False)
)

fig_bar = px.bar(
    sido_df,
    x="시도",
    y="총인구",
    title="시도별 총인구수 비교 (큰 순서대로 나열)",
    labels={"시도": "시·도 구분", "총인구": "총인구수 (명)"},
    color_discrete_sequence=[warm_main_color],
    text_auto=".2s",  # 막대 상단에 간략한 숫자 표시 (예: 13M, 9.4M)
)

fig_bar.update_layout(
    plot_bgcolor=warm_bg_color,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    xaxis_title="시·도 구분",
    yaxis_title="총인구수 (명)",
)

st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 5. 동네별 남인구 vs 여인구 산점도 (Scatter Plot) (Plotly)
# ---------------------------------------------------------
st.subheader("5. 동네별 남인구 vs 여인구 산점도")
st.write(
    "각 동네의 남성 인구와 여성 인구를 1:1 대응 좌표로 나타내어 지역별 성비 균형을 살펴봅니다. 기준선(대각선)에서 멀어진 지역일수록 남성 또는 여성 인구 쏠림 현상이 심하다는 것을 시각적으로 파악할 수 있습니다."
)

# 동네(시군구 + 동) 정보 조합하여 툴팁 호버 정보 작성
hover_data_cols = (
    ["시도", "시군구", "동"]
    if all(c in df.columns for c in ["시도", "시군구", "동"])
    else None
)

fig_scatter = px.scatter(
    df,
    x="남인구",
    y="여인구",
    title="동네별 남인구 vs 여인구 관계 (성비 편차 확인)",
    labels={"남인구": "남성 인구수 (명)", "여인구": "여성 인구수 (명)"},
    hover_data=hover_data_cols,
    color_discrete_sequence=["#2A9D8F"],  # 구분감을 위해 청록색(Teal) 사용
    opacity=0.6,  # 점들이 겹쳤을 때 밀도를 볼 수 있도록 투명도 조절
)

# 1:1 성비 기준 대각선(y = x) 추가 (남/여 비율이 완벽히 같은 상태)
max_val = max(df["남인구"].max(), df["여인구"].max())
fig_scatter.add_shape(
    type="line",
    x0=0,
    y0=0,
    x1=max_val,
    y1=max_val,
    line=dict(color="#E76F51", width=2, dash="dash"),
)

fig_scatter.update_layout(
    plot_bgcolor=warm_bg_color,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    xaxis_title="남성 인구수 (명)",
    yaxis_title="여성 인구수 (명)",
)

st.plotly_chart(fig_scatter, use_container_width=True)
