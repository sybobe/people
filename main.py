import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 1. 페이지 기본 설정 (웹 브라우저 탭 제목, 아이콘, 넓은 레이아웃)
st.set_page_config(
    page_title="동네별 인구 피라미드", page_icon="🏛️", layout="wide"
)

# 메인 타이틀 및 간단한 안내
st.title("🏛️ 우리 동네 인구 피라미드 살펴보기")
st.write(
    "전국 읍·면·동을 선택하여 연령대별 남녀 인구 구조(인구 피라미드)를 시각적으로 확인해 보세요."
)


# 2. 데이터 로드 및 전처리 함수 (캐싱으로 로딩 속도 최적화)
@st.cache_data
def load_and_preprocess_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/population_yearly.csv.gz"

    # CSV 파일 읽기 (인코딩 예외 처리)
    try:
        df = pd.read_csv(url, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding="cp949")

    # 2015~2026년 데이터 중 가장 최신 연도만 추출
    if "연도" in df.columns:
        latest_year = df["연도"].max()
        df = df[df["연도"] == latest_year].copy()

    return df, latest_year


# 데이터 불러오기 실행
with st.spinner("최신 인구 데이터를 불러오는 중입니다..."):
    df, latest_year = load_and_preprocess_data()

st.success(f"데이터를 성공적으로 불러왔습니다! (기준 연도: {latest_year}년)")
st.markdown("---")


# 3. 나이 라벨 목록 생성 (0세부터 100세 이상까지 순서 고정)
# 열 이름 형태: '남_0세', '남_1세', ..., '남_99세', '남_100세 이상'
age_labels = [f"{i}세" for i in range(100)] + ["100세 이상"]

# 4. 시도 -> 시군구 -> 동 단계별 드롭다운 (상위 선택에 따라 하위 항목이 동적으로 변함)
st.subheader("📍 지역 선택하기")
col1, col2, col3 = st.columns(3)

with col1:
    sido_list = sorted(df["시도"].dropna().unique())
    selected_sido = st.selectbox("시·도 선택", sido_list)

# 선택된 시도에 해당하는 시군구 목록 추출
df_sido = df[df["시도"] == selected_sido]

with col2:
    sigungu_list = sorted(df_sido["시군구"].dropna().unique())
    selected_sigungu = st.selectbox("시·군·구 선택", sigungu_list)

# 선택된 시군구에 해당하는 동 목록 추출
df_sigungu = df_sido[df_sido["시군구"] == selected_sigungu]

with col3:
    dong_list = sorted(df_sigungu["동"].dropna().unique())
    selected_dong = st.selectbox("읍·면·동 선택", dong_list)


# 5. 최종 선택된 동네 데이터 1행(시리즈) 추출
selected_row = df_sigungu[df_sigungu["동"] == selected_dong].iloc[0]


# 6. 선택된 동네의 나이별 남녀 인구수 집계
male_pop = []
female_pop = []

for age in age_labels:
    male_col = f"남_{age}"
    female_col = f"여_{age}"

    # 컬럼이 존재하는지 확인하고 값 가져오기 (없는 경우 0 처리)
    m_val = selected_row[male_col] if male_col in selected_row else 0
    f_val = selected_row[female_col] if female_col in selected_row else 0

    male_pop.append(m_val)
    female_pop.append(f_val)

# 인구 피라미드 표현을 위해 남성 인구수는 음수로 전환 (좌측 배치)
male_pop_neg = [-x for x in male_pop]


# 7. Plotly 인구 피라미드 (가로 막대그래프) 작성
fig = go.Figure()

# 따뜻한 톤 칼라 설정 (남성: 따뜻한 네이비/블루 grey, 여성: 소프트 코랄/오렌지)
color_male = "#4A6FA5"
color_female = "#E07A5F"
bg_color = "#F4F1DE"

# 남성 인구 막대 (좌측 - 음수 값)
fig.add_trace(
    go.Bar(
        y=age_labels,
        x=male_pop_neg,
        name="남성",
        orientation="h",
        marker=dict(color=color_male),
        # 마우스 올려놓았을 때 실제 양수 인구수로 보이도록 설정
        hovertemplate="<b>%{y} 남성</b>: %{customdata:,}명<extra></extra>",
        customdata=male_pop,
    )
)

# 여성 인구 막대 (우측 - 양수 값)
fig.add_trace(
    go.Bar(
        y=age_labels,
        x=female_pop,
        name="여성",
        orientation="h",
        marker=dict(color=color_female),
        hovertemplate="<b>%{y} 여성</b>: %{x:,}명<extra></extra>",
    )
)


# 8. 축 레이아웃 및 디자인 설정 (나이 순서 고정 핵심)
# x축의 눈금 표시 시 음수를 양수로 바꾸어 보여줌
max_val = max(max(male_pop), max(female_pop)) if max(female_pop) > 0 else 100

fig.update_layout(
    title=f"<b>{selected_sido} {selected_sigungu} {selected_dong}</b> 인구 피라미드 ({latest_year}년)",
    title_font=dict(size=18, color="#3D405B"),
    barmode="overlay",  # 중앙 기준 좌우 배치
    bargap=0.1,  # 막대 간격
    plot_bgcolor=bg_color,
    paper_bgcolor="white",
    font=dict(color="#3D405B", size=12),
    legend=dict(x=0.85, y=1.05, orientation="h"),
    # x축 설정 (절댓값 기준 눈금 표시)
    xaxis=dict(
        title="인구수 (명)",
        range=[-max_val * 1.1, max_val * 1.1],
        tickmode="array",
        # 가로축 눈금값 (음수로 들어간 남성 축 값을 양수로 보기 쉽게 변환)
        tickvals=[-max_val, -max_val // 2, 0, max_val // 2, max_val],
        ticktext=[
            f"{max_val:,}",
            f"{max_val//2:,}",
            "0",
            f"{max_val//2:,}",
            f"{max_val:,}",
        ],
    ),
    # y축 설정 (CRITICAL: 0세가 맨 아래, 100세 이상이 맨 위로 고정)
    yaxis=dict(
        title="연령",
        type="category",
        categoryorder="array",
        categoryarray=age_labels,  # 0세부터 100세 이상 순서 고정
        dtick=5,  # 눈금을 5세 단위로 표시하여 깔끔하게 정렬
    ),
    height=800,  # 100개 연령대가 잘 보이도록 세로 길이를 충분히 설정
)

# 스트림릿에 그래프 출력
st.markdown("---")
st.plotly_chart(fig, use_container_width=True)
