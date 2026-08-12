import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 페이지 기본 설정 (제목, 레이아웃)
st.set_page_config(
    page_title="동네별 총인구 분포 확인하기", page_icon="📊", layout="wide"
)

st.title("📊 우리 동네 인구 분포(퍼짐) 살펴보기")
st.write(
    "주민등록 인구통계 데이터를 활용하여 전국 읍·면·동별 총인구수 분포를 시각화합니다."
)


# 2. 데이터 불러오기 및 전처리 함수
@st.cache_data
def load_and_preprocess_data():
    # ⚠️ 아래 URL 부분을 실제 데이터 파일의 주소(URL)로 변경해주세요.
    url = "https://example.com/202607_202607.csv"

    # 판다스로 CSV 파일 읽기 (인코딩 예외 처리)
    try:
        df = pd.read_csv(url, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding="cp949")
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

    # '연도' 열이 존재할 경우 가장 최신 연도 데이터만 필터링
    if "연도" in df.columns:
        latest_year = df["연도"].max()
        df = df[df["연도"] == latest_year]

    # '남_' 및 '여_'로 시작하는 나이별 인구 열 찾기
    male_cols = [c for c in df.columns if str(c).startswith("남_")]
    female_cols = [c for c in df.columns if str(c).startswith("여_")]

    # 남/여 나이별 인구를 모두 합산하여 '총인구' 열 생성
    df["총인구"] = df[male_cols + female_cols].sum(axis=1)

    return df


# 데이터 불러오기 실행
with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_and_preprocess_data()

# 데이터 로드 검증
if df.empty or "총인구" not in df.columns:
    st.warning(
        "데이터를 정상적으로 불러오지 못했거나 '총인구' 열을 생성할 수 없습니다. 데이터 URL을 확인해 주세요."
    )
    st.stop()

st.success("데이터를 성공적으로 불러왔습니다!")

st.markdown("---")

# ---------------------------------------------------------
# 1. 총인구 기술통계량 (describe) 표 출력
# ---------------------------------------------------------
st.subheader("1. 총인구 요약 통계량 (describe)")
st.write(
    "전국 읍·면·동 총인구수의 평균, 중앙값, 최솟값, 최댓값 등의 요약 통계입니다."
)

stats_df = df[["총인구"]].describe().reset_index()
stats_df.columns = ["통계 항목", "총인구(명)"]

# 통계 항목 용어 한글화
korean_stats = {
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
    lambda x: korean_stats.get(x, x)
)

st.dataframe(stats_df, use_container_width=True)

st.markdown("---")

# 따뜻한 톤 컬러 설정
warm_color_main = "#E07A5F"
warm_color_alt = "#F4F1DE"

# ---------------------------------------------------------
# 2. 총인구 히스토그램 (Plotly)
# ---------------------------------------------------------
st.subheader("2. 총인구 히스토그램")
st.write(
    "인구 구간별로 몇 개의 동네(읍·면·동)가 속해 있는지 분포를 보여줍니다."
)

fig_hist = px.histogram(
    df,
    x="총인구",
    nbins=50,
    title="전국 읍·면·동 총인구수 분포 (히스토그램)",
    labels={"총인구": "총인구수 (명)", "count": "동네 수"},
    color_discrete_sequence=[warm_color_main],
)

fig_hist.update_layout(
    plot_bgcolor=warm_color_alt,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    xaxis_title="총인구수 (명)",
    yaxis_title="동네 수 (개)",
    hovermode="x unified",
)

st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 3. 총인구 상자그림 (Box Plot) (Plotly)
# ---------------------------------------------------------
st.subheader("3. 총인구 상자그림 (Box Plot)")
st.write(
    "인구수 데이터의 중앙값, 분위수, 이상치(인구가 매우 많거나 적은 지역)를 한눈에 확인할 수 있습니다."
)

fig_box = px.box(
    df,
    y="총인구",
    title="전국 읍·면·동 총인구수 상자그림",
    labels={"총인구": "총인구수 (명)"},
    color_discrete_sequence=[warm_color_main],
    points="outliers",
)

fig_box.update_layout(
    plot_bgcolor=warm_color_alt,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=13),
    yaxis_title="총인구수 (명)",
)

st.plotly_chart(fig_box, use_container_width=True)
