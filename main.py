import pandas as pd
import streamlit as st
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="데이터의 퍼짐을 눈으로 보기",
    page_icon="📊",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/"
    "data/population_yearly.csv.gz"
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    # .csv.gz 파일도 pandas가 압축을 자동으로 해제해서 읽어줍니다.
    df = pd.read_csv(DATA_URL)

    # 가장 최신 연도만 사용합니다.
    latest_year = df["연도"].max()
    df = df[df["연도"] == latest_year].copy()

    # 남성 인구와 여성 인구 열을 모두 찾아 더합니다.
    male_cols = [col for col in df.columns if col.startswith("남_")]
    female_cols = [col for col in df.columns if col.startswith("여_")]

    df["총인구"] = df[male_cols + female_cols].sum(axis=1)

    return df, latest_year


df, latest_year = load_data()


# --------------------------------------------------
# 화면
# --------------------------------------------------
st.title("📊 데이터의 퍼짐을 눈으로 보기")

st.write(
    f"**{latest_year}년 읍·면·동별 인구 데이터**를 이용해 "
    "총인구가 얼마나 다양하게 퍼져 있는지 살펴봅니다."
)

st.info(
    "💡 **퍼짐**이란 데이터가 어느 정도 넓게 흩어져 있는지를 뜻합니다. "
    "아래의 히스토그램과 상자그림을 함께 보면 데이터의 전체적인 모습을 "
    "쉽게 확인할 수 있습니다."
)


# --------------------------------------------------
# 1. describe()
# --------------------------------------------------
st.subheader("1️⃣ 총인구의 기본 통계")

st.write(
    "각 읍·면·동의 **총인구**를 대상으로 평균, 최솟값, 최댓값 등을 계산했습니다."
)

describe_df = df["총인구"].describe().to_frame().T
describe_df.index = ["총인구"]

st.dataframe(
    describe_df,
    use_container_width=True,
)

st.caption(
    "💡 평균(mean)은 전체 데이터의 대표적인 크기를 보여주고, "
    "25%·50%·75%는 데이터를 크기순으로 놓았을 때의 위치를 보여줍니다."
)


# --------------------------------------------------
# 2. 히스토그램
# --------------------------------------------------
st.subheader("2️⃣ 총인구 히스토그램")

st.write(
    "가로축은 **총인구**, 세로축은 **해당 인구 구간에 속하는 읍·면·동의 수**입니다."
)

fig_hist = px.histogram(
    df,
    x="총인구",
    nbins=40,
    labels={
        "총인구": "총인구",
        "count": "읍·면·동 수",
    },
    title=f"{latest_year}년 읍·면·동별 총인구 분포",
)

fig_hist.update_layout(
    hovermode="x unified",
    xaxis_title="총인구",
    yaxis_title="읍·면·동 수",
)

st.plotly_chart(
    fig_hist,
    use_container_width=True,
)

st.caption(
    "💡 막대가 많이 모여 있는 곳을 보면 어떤 인구 규모의 동네가 "
    "많은지 알 수 있습니다. 그래프 위에서 마우스를 움직이면 값을 확인할 수 있고, "
    "드래그하면 확대할 수 있습니다."
)


# --------------------------------------------------
# 3. 상자그림
# --------------------------------------------------
st.subheader("3️⃣ 총인구 상자그림")

st.write(
    "상자그림은 데이터의 **중앙값, 가운데 50%가 모여 있는 범위, "
    "상대적으로 멀리 떨어진 값** 등을 한눈에 보여줍니다."
)

fig_box = px.box(
    df,
    y="총인구",
    points="outliers",
    labels={
        "총인구": "총인구",
    },
    title=f"{latest_year}년 읍·면·동별 총인구 상자그림",
)

fig_box.update_layout(
    yaxis_title="총인구",
)

st.plotly_chart(
    fig_box,
    use_container_width=True,
)

st.caption(
    "💡 상자 가운데 선은 중앙값을 나타냅니다. "
    "상자에서 멀리 떨어진 점은 다른 동네에 비해 총인구가 특히 크거나 작은 곳입니다."
)


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
with st.expander("📋 사용한 데이터 일부 보기"):
    st.dataframe(
        df[["연도", "시도", "시군구", "동", "코드", "총인구"]].head(20),
        use_container_width=True,
    )
