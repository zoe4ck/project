# main.py

import io
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. 기본 설정
# ============================================================

st.set_page_config(
    page_title="전국 고령화 지도",
    page_icon="👵",
    layout="wide"
)

st.title("🇰🇷 전국 고령화 지도")
st.caption("시군구별 65세 이상 인구 비율 · 최신 연도 기준")


# ============================================================
# 2. 데이터 주소
# ============================================================

POPULATION_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/population_yearly.csv.gz"
)

GEOJSON_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/boundaries/sigungu_kr.geojson"
)


# ============================================================
# 3. 데이터 불러오기
# ============================================================

@st.cache_data
def load_population_data():
    """인구 데이터를 내려받아 판다스 데이터프레임으로 읽습니다."""

    response = requests.get(POPULATION_URL, timeout=60)
    response.raise_for_status()

    # CSV가 gzip으로 압축되어 있으므로 pandas가 압축을 풀어서 읽습니다.
    df = pd.read_csv(
        io.BytesIO(response.content),
        compression="gzip",
        dtype={"코드": "string"}
    )

    return df


@st.cache_data
def load_geojson():
    """시군구 경계 GeoJSON을 불러옵니다."""

    response = requests.get(GEOJSON_URL, timeout=60)
    response.raise_for_status()

    return response.json()


# ============================================================
# 4. 고령화율 계산
# ============================================================

@st.cache_data
def make_sigungu_data(df):
    """
    읍·면·동 단위 인구를 시군구 단위로 합칩니다.

    시군구 코드는 행정동 코드의 앞 5자리입니다.
    """

    # --------------------------------------------------------
    # 코드가 혹시 숫자로 들어왔더라도 문자열로 변환합니다.
    # 행정구역 코드는 계산할 숫자가 아니라 '이름표'이기 때문입니다.
    # --------------------------------------------------------
    df = df.copy()
    df["코드"] = df["코드"].astype("string").str.strip()

    # 코드 앞 5자리가 시군구 코드입니다.
    df["시군구코드"] = df["코드"].str[:5]

    # --------------------------------------------------------
    # 최신 연도만 사용합니다.
    # 연도가 숫자/문자 중 어떤 형태로 들어와도 비교할 수 있도록
    # 숫자로 변환합니다.
    # --------------------------------------------------------
    df["연도_숫자"] = pd.to_numeric(df["연도"], errors="coerce")

    latest_year = int(df["연도_숫자"].max())
    df = df[df["연도_숫자"] == latest_year].copy()

    # --------------------------------------------------------
    # '계_'로 시작하는 열만 사용합니다.
    #
    # 예:
    # 계_0세
    # 계_1세
    # ...
    # 계_65세
    # ...
    # 계_100세 이상
    #
    # 계_는 남녀를 합친 인구입니다.
    # --------------------------------------------------------
    total_age_columns = [
        col for col in df.columns
        if str(col).startswith("계_")
    ]

    # 65세 이상 열만 골라냅니다.
    elderly_columns = []

    for age in range(65, 100):
        column_name = f"계_{age}세"

        if column_name in df.columns:
            elderly_columns.append(column_name)

    # 100세 이상도 포함합니다.
    if "계_100세 이상" in df.columns:
        elderly_columns.append("계_100세 이상")

    # 필요한 열이 없는 경우 오류를 알려줍니다.
    if not total_age_columns:
        raise ValueError(
            "나이별 '계_' 인구 열을 찾을 수 없습니다."
        )

    if not elderly_columns:
        raise ValueError(
            "65세 이상 인구 열을 찾을 수 없습니다."
        )

    # --------------------------------------------------------
    # 각 읍·면·동의 전체 인구와 65세 이상 인구를 계산합니다.
    # --------------------------------------------------------
    df["전체인구"] = (
        df[total_age_columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .sum(axis=1)
    )

    df["65세이상인구"] = (
        df[elderly_columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .sum(axis=1)
    )

    # --------------------------------------------------------
    # 같은 시군구에 속한 여러 읍·면·동을 합칩니다.
    # --------------------------------------------------------
    group_columns = ["시군구코드", "시군구", "시도"]

    sigungu = (
        df.groupby(group_columns, as_index=False)[
            ["전체인구", "65세이상인구"]
        ]
        .sum()
    )

    # --------------------------------------------------------
    # 고령화율 = 65세 이상 인구 / 전체 인구 × 100
    # --------------------------------------------------------
    sigungu["고령화율"] = np.where(
        sigungu["전체인구"] > 0,
        sigungu["65세이상인구"] / sigungu["전체인구"] * 100,
        np.nan
    )

    sigungu["연도"] = latest_year

    return sigungu


# ============================================================
# 5. 고령화율을 5단계로 분류
# ============================================================

def make_grade(rate):
    """
    고령화율을 다음 5단계로 나눕니다.

    1단계: 19% 미만
    2단계: 19% 이상 ~ 23% 미만
    3단계: 23% 이상 ~ 28% 미만
    4단계: 28% 이상 ~ 38% 미만
    5단계: 38% 이상
    """

    if pd.isna(rate):
        return np.nan

    if rate < 19:
        return 0
    elif rate < 23:
        return 1
    elif rate < 28:
        return 2
    elif rate < 38:
        return 3
    else:
        return 4


# ============================================================
# 6. 데이터 불러오기
# ============================================================

try:
    with st.spinner("전국 인구 및 행정구역 데이터를 불러오는 중입니다..."):
        population_df = load_population_data()
        geojson = load_geojson()
        sigungu_df = make_sigungu_data(population_df)

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(e))
    st.stop()


# ============================================================
# 7. GeoJSON의 코드도 문자열로 정리
# ============================================================

# 지도 경계의 '코드' 역시 문자열로 맞춥니다.
for feature in geojson["features"]:
    properties = feature.get("properties", {})

    if "코드" in properties:
        properties["코드"] = str(properties["코드"]).strip().zfill(5)


# 인구 데이터의 시군구 코드도 5자리 문자열로 맞춥니다.
sigungu_df["시군구코드"] = (
    sigungu_df["시군구코드"]
    .astype("string")
    .str.strip()
    .str.zfill(5)
)


# ============================================================
# 8. GeoJSON과 인구 데이터를 코드로 연결
# ============================================================

# 지도에 표시할 시군구의 정보가 코드에 따라 정확히 연결되도록
# GeoJSON의 feature마다 인구 데이터를 찾아 넣습니다.

rate_dict = (
    sigungu_df
    .set_index("시군구코드")["고령화율"]
    .to_dict()
)

name_dict = (
    sigungu_df
    .set_index("시군구코드")["시군구"]
    .to_dict()
)

province_dict = (
    sigungu_df
    .set_index("시군구코드")["시도"]
    .to_dict()
)


# GeoJSON에 지도용 속성을 추가합니다.
for feature in geojson["features"]:

    properties = feature["properties"]
    code = str(properties.get("코드", "")).strip().zfill(5)

    rate = rate_dict.get(code, np.nan)

    properties["고령화율"] = rate

    # 원래 GeoJSON의 이름을 우선 사용하고,
    # 없으면 인구 데이터에서 가져옵니다.
    if not properties.get("시군구"):
        properties["시군구"] = name_dict.get(code, "정보 없음")

    if not properties.get("시도"):
        properties["시도"] = province_dict.get(code, "정보 없음")


# ============================================================
# 9. 5단계 구간 만들기
# ============================================================

sigungu_df["등급"] = sigungu_df["고령화율"].apply(make_grade)


# ============================================================
# 10. 지도용 데이터 준비
# ============================================================

# 지도에서 사용할 색상 단계입니다.
# 낮은 고령화율은 옅게, 높은 고령화율은 진하게 표시합니다.
colors = [
    "#EAF3F8",
    "#BFDCEB",
    "#83BBD1",
    "#468EAF",
    "#1F5875"
]

labels = [
    "19% 미만",
    "19% 이상 ~ 23% 미만",
    "23% 이상 ~ 28% 미만",
    "28% 이상 ~ 38% 미만",
    "38% 이상"
]


# ============================================================
# 11. 단계구분도 그리기
# ============================================================

fig = go.Figure()


# ------------------------------------------------------------
# 지도 영역
#
# 실제 고령화율 자체가 아니라 0~4의 등급을 색칠합니다.
# 따라서 색상이 연속적으로 변하지 않고 5단계로 딱 끊어집니다.
# ------------------------------------------------------------

fig.add_trace(
    go.Choropleth(
        geojson=geojson,
        featureidkey="properties.코드",

        locations=sigungu_df["시군구코드"],
        z=sigungu_df["등급"],

        # 5개 색상을 단계적으로 사용합니다.
        colorscale=[
            [0.00, colors[0]],
            [0.20, colors[0]],

            [0.20, colors[1]],
            [0.40, colors[1]],

            [0.40, colors[2]],
            [0.60, colors[2]],

            [0.60, colors[3]],
            [0.80, colors[3]],

            [0.80, colors[4]],
            [1.00, colors[4]],
        ],

        zmin=0,
        zmax=4,

        marker_line_color="white",
        marker_line_width=0.5,

        # 마우스를 올렸을 때 보여줄 내용
        customdata=np.column_stack(
            [
                sigungu_df["시군구"],
                sigungu_df["시도"],
                sigungu_df["고령화율"]
            ]
        ),

        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "시도: %{customdata[1]}<br>"
            "고령화율: %{customdata[2]:.2f}%"
            "<extra></extra>"
        ),

        colorbar=dict(
            title=dict(
                text="고령화율",
                side="top"
            ),

            tickmode="array",
            tickvals=[0, 1, 2, 3, 4],
            ticktext=labels,

            len=0.75,
            thickness=18,

            outlinewidth=0
        )
    )
)


# ============================================================
# 12. 지도 모양 설정
# ============================================================

fig.update_geos(
    # 배경 지도 타일을 사용하지 않습니다.
    # 대한민국의 행정구역 경계만 표시합니다.
    visible=False,

    fitbounds="locations",

    projection_type="mercator",

    showland=False,
    showcountries=False,
    showcoastlines=False,
    showframe=False,

    bgcolor="white"
)


fig.update_layout(
    height=700,

    margin=dict(
        l=0,
        r=0,
        t=10,
        b=0
    ),

    paper_bgcolor="white",

    font=dict(
        family="Arial, Malgun Gothic, Apple SD Gothic Neo, sans-serif"
    )
)


# ============================================================
# 13. 지도 출력
# ============================================================

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": True
    }
)


# ============================================================
# 14. 상위 / 하위 10개 지역
# ============================================================

st.subheader("📊 고령화율 상·하위 지역")


# 고령화율이 없는 지역은 표에서 제외합니다.
ranking_df = sigungu_df.dropna(
    subset=["고령화율"]
).copy()


# ------------------------------------------------------------
# 상위 10개
# ------------------------------------------------------------

top10 = (
    ranking_df
    .sort_values("고령화율", ascending=False)
    .head(10)
    .copy()
)

top10["고령화율"] = top10["고령화율"].map(
    lambda x: f"{x:.2f}%"
)

top10 = top10[
    ["시도", "시군구", "고령화율"]
].reset_index(drop=True)

top10.index = top10.index + 1


# ------------------------------------------------------------
# 하위 10개
# ------------------------------------------------------------

bottom10 = (
    ranking_df
    .sort_values("고령화율", ascending=True)
    .head(10)
    .copy()
)

bottom10["고령화율"] = bottom10["고령화율"].map(
    lambda x: f"{x:.2f}%"
)

bottom10 = bottom10[
    ["시도", "시군구", "고령화율"]
].reset_index(drop=True)

bottom10.index = bottom10.index + 1


# ============================================================
# 15. 두 표를 나란히 표시
# ============================================================

col1, col2 = st.columns(2)


with col1:
    st.markdown("### 🔴 고령화율 높은 곳 10개")
    st.dataframe(
        top10,
        use_container_width=True
    )


with col2:
    st.markdown("### 🔵 고령화율 낮은 곳 10개")
    st.dataframe(
        bottom10,
        use_container_width=True
    )


# ============================================================
# 16. 데이터 기준 안내
# ============================================================

st.caption(
    f"※ 지도와 표는 인구 데이터에서 확인되는 최신 연도인 "
    f"{int(sigungu_df['연도'].iloc[0])}년을 기준으로 계산했습니다."
)

st.caption(
    "※ 고령화율 = 65세 이상 인구 ÷ 전체 인구 × 100"
)

st.caption(
    "※ 지도 색상 구간: 19% / 23% / 28% / 38%"
)
