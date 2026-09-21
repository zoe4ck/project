import io
import json

import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="전국 고령화 지도 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# 2. 귀여운 핑크색 디자인
# =========================================================

st.markdown(
    """
    <style>

    /* 전체 배경 */
    .stApp {
        background: linear-gradient(
            180deg,
            #fff7fb 0%,
            #fffafd 45%,
            #fef4f8 100%
        );
    }

    /* 위쪽 여백 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* 제목 */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #8f4564;
        margin-bottom: 4px;
        letter-spacing: -2px;
    }

    .sub-title {
        text-align: center;
        color: #a8788e;
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* 먼작귀 친구 카드 */
    .friends {
        display: flex;
        justify-content: center;
        gap: 18px;
        margin: 10px 0 30px 0;
    }

    .friend-card {
        width: 210px;
        min-height: 115px;
        border-radius: 25px;
        padding: 17px;
        text-align: center;
        box-shadow: 0 7px 20px rgba(170, 95, 125, 0.12);
        border: 2px solid rgba(255,255,255,0.9);
    }

    .friend-card h3 {
        margin: 3px 0 3px 0;
        font-size: 20px;
        color: #75425a;
    }

    .friend-card p {
        margin: 0;
        font-size: 13px;
        color: #a16e83;
    }

    .chiikawa {
        background: #fff0f5;
    }

    .hachiware {
        background: #eef9ff;
    }

    .usagi {
        background: #fffbe8;
    }

    .friend-emoji {
        font-size: 36px;
    }

    /* 설명 박스 */
    .info-box {
        background: #ffffff;
        border: 2px solid #ffd7e5;
        border-radius: 20px;
        padding: 18px 22px;
        margin: 15px 0 25px 0;
        box-shadow: 0 5px 18px rgba(190, 105, 140, 0.08);
    }

    .info-box-title {
        color: #b34f76;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .info-box-text {
        color: #765867;
        font-size: 14px;
        line-height: 1.7;
    }

    /* 섹션 제목 */
    .section-title {
        color: #914664;
        font-size: 25px;
        font-weight: 800;
        margin: 25px 0 12px 0;
    }

    /* 통계 카드 */
    .metric-box {
        background: white;
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        border: 2px solid #ffe0ea;
        box-shadow: 0 5px 18px rgba(190, 105, 140, 0.08);
    }

    .metric-title {
        color: #aa7188;
        font-size: 13px;
        margin-bottom: 6px;
    }

    .metric-value {
        color: #9a4166;
        font-size: 25px;
        font-weight: 800;
    }

    /* 표 제목 */
    .table-title {
        background: #fff0f5;
        color: #984565;
        border-radius: 15px;
        padding: 12px 16px;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* 수식 */
    .formula {
        background: #fff;
        border: 2px dashed #f2b7ca;
        border-radius: 18px;
        padding: 17px;
        text-align: center;
        color: #795668;
        margin-top: 25px;
        font-size: 15px;
    }

    /* Streamlit dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }

    /* 버튼 */
    .stButton button {
        border-radius: 15px;
        border: 1px solid #f2b6cb;
        background: #fff1f6;
        color: #914664;
    }

    /* 모바일 대응 */
    @media (max-width: 700px) {
        .main-title {
            font-size: 31px;
        }

        .friends {
            flex-direction: column;
            align-items: center;
        }

        .friend-card {
            width: 90%;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. 제목
# =========================================================

st.markdown(
    '<div class="main-title">🌸 전국 고령화 지도 🌸</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-title">우리나라 시군구별 65세 이상 인구 비율을 한눈에 살펴봐요 ♡</div>',
    unsafe_allow_html=True,
)


# =========================================================
# 4. 먼작귀 친구들 장식
# =========================================================

st.markdown(
    """
    <div class="friends">

        <div class="friend-card chiikawa">
            <div class="friend-emoji">🥺</div>
            <h3>치이카와</h3>
            <p>오늘도 함께 알아봐요 ♡</p>
        </div>

        <div class="friend-card hachiware">
            <div class="friend-emoji">🩵</div>
            <h3>하치와레</h3>
            <p>우리나라의 고령화 현황!</p>
        </div>

        <div class="friend-card usagi">
            <div class="friend-emoji">🐰</div>
            <h3>우사기</h3>
            <p>꼼꼼하게 확인해보자!</p>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. 데이터 주소
# =========================================================

POPULATION_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/"
    "data/population_yearly.csv.gz"
)

GEOJSON_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/"
    "data/boundaries/sigungu_kr.geojson"
)


# =========================================================
# 6. 인구 데이터 불러오기
# =========================================================

@st.cache_data
def load_population():
    """전국 읍면동별 연령별 인구 데이터를 불러옵니다."""

    response = requests.get(
        POPULATION_URL,
        timeout=60,
    )

    response.raise_for_status()

    data = pd.read_csv(
        io.BytesIO(response.content),
        compression="gzip",
        dtype={"코드": "string"},
    )

    return data


# =========================================================
# 7. 지도 경계 데이터 불러오기
# =========================================================

@st.cache_data
def load_geojson():
    """전국 시군구 경계 GeoJSON을 불러옵니다."""

    response = requests.get(
        GEOJSON_URL,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# 8. 데이터 불러오기
# =========================================================

try:
    population_df = load_population()
    geojson = load_geojson()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# 9. 최신 연도 찾기
# =========================================================

population_df["연도"] = pd.to_numeric(
    population_df["연도"],
    errors="coerce",
)

latest_year = int(
    population_df["연도"].dropna().max()
)


# =========================================================
# 10. 코드 정리
# =========================================================

population_df["코드"] = (
    population_df["코드"]
    .astype("string")
    .str.strip()
)

# 읍면동 코드는 앞의 5자리가 시군구 코드입니다.
population_df["시군구코드"] = (
    population_df["코드"]
    .str[:5]
)


# =========================================================
# 11. 최신 연도 데이터만 사용
# =========================================================

latest_df = population_df[
    population_df["연도"] == latest_year
].copy()


# =========================================================
# 12. 전체 인구 계산
# =========================================================

# "계_0세", "계_1세" ... 형태의 열을 찾습니다.
total_age_columns = [
    column
    for column in latest_df.columns
    if column.startswith("계_")
]


# 숫자로 변환
for column in total_age_columns:
    latest_df[column] = pd.to_numeric(
        latest_df[column],
        errors="coerce",
    ).fillna(0)


# 전체 연령 인구
latest_df["전체인구"] = latest_df[
    total_age_columns
].sum(axis=1)


# =========================================================
# 13. 65세 이상 인구 계산
# =========================================================

elderly_columns = []

for age in range(65, 100):
    column_name = f"계_{age}세"

    if column_name in latest_df.columns:
        elderly_columns.append(column_name)


# 100세 이상
if "계_100세 이상" in latest_df.columns:
    elderly_columns.append("계_100세 이상")


# 65세 이상 인구
latest_df["65세이상인구"] = latest_df[
    elderly_columns
].sum(axis=1)


# =========================================================
# 14. 시군구별로 합치기
# =========================================================

grouped = (
    latest_df
    .groupby("시군구코드", as_index=False)
    .agg(
        전체인구=("전체인구", "sum"),
        고령인구=("65세이상인구", "sum"),
    )
)


# =========================================================
# 15. 시군구 이름과 시도 정보 가져오기
# =========================================================

region_info = (
    latest_df[
        [
            "시군구코드",
            "시군구",
            "시도",
        ]
    ]
    .drop_duplicates(
        subset=["시군구코드"]
    )
)


grouped = grouped.merge(
    region_info,
    on="시군구코드",
    how="left",
)


# =========================================================
# 16. 고령화율 계산
# =========================================================

grouped["고령화율"] = np.where(
    grouped["전체인구"] > 0,
    grouped["고령인구"]
    / grouped["전체인구"]
    * 100,
    np.nan,
)


# 숫자가 이상한 행 제거
grouped = grouped[
    grouped["고령화율"].notna()
].copy()


# =========================================================
# 17. 지도용 코드 정리
# =========================================================

grouped["시군구코드"] = (
    grouped["시군구코드"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)


# =========================================================
# 18. 고령화율 등급
# =========================================================

# 기준
# 19% 미만
# 19% 이상 ~ 23% 미만
# 23% 이상 ~ 28% 미만
# 28% 이상 ~ 38% 미만
# 38% 이상

def get_grade(rate):
    if pd.isna(rate):
        return 0

    if rate < 19:
        return 0

    if rate < 23:
        return 1

    if rate < 28:
        return 2

    if rate < 38:
        return 3

    return 4


grouped["등급"] = grouped["고령화율"].apply(
    get_grade
)


# =========================================================
# 19. 지도에 넣을 GeoJSON 만들기
# =========================================================

def make_map_geojson(original_geojson, region_data):
    """시군구 코드로 인구 데이터를 지도 경계와 연결합니다."""

    result = {
        "type": "FeatureCollection",
        "features": [],
    }

    # 빠른 검색을 위해 딕셔너리 생성
    data_dict = {}

    for _, row in region_data.iterrows():

        code = str(
            row["시군구코드"]
        ).strip().zfill(5)

        data_dict[code] = {
            "시군구": str(row["시군구"]),
            "시도": str(row["시도"]),
            "고령화율": float(row["고령화율"]),
            "등급": int(row["등급"]),
        }

    # GeoJSON 각각의 지역에 데이터 붙이기
    for feature in original_geojson["features"]:

        properties = feature.get(
            "properties",
            {},
        )

        code = properties.get("코드")

        if code is None:
            code = properties.get("code")

        if code is None:
            continue

        code = str(code).strip().zfill(5)

        if code not in data_dict:
            continue

        new_feature = {
            "type": feature["type"],
            "geometry": feature["geometry"],
            "properties": {
                "코드": code,
                "시군구": data_dict[code]["시군구"],
                "시도": data_dict[code]["시도"],
                "고령화율": data_dict[code]["고령화율"],
                "등급": data_dict[code]["등급"],
            },
        }

        result["features"].append(
            new_feature
        )

    return result


map_geojson = make_map_geojson(
    geojson,
    grouped,
)


# =========================================================
# 20. 지도 색상
# =========================================================

MAP_COLORS = [
    "#FFF0F6",
    "#FFD4E4",
    "#FFB0CD",
    "#F47FA9",
    "#D84D80",
]


# =========================================================
# 21. 지도 HTML 만들기
# =========================================================

geojson_text = json.dumps(
    map_geojson,
    ensure_ascii=False,
)


map_html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<style>

html,
body {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}}

#map {{
    width: 100%;
    height: 670px;
    border-radius: 22px;
    border: 3px solid #ffd8e6;
    box-shadow: 0 6px 20px rgba(180, 90, 125, 0.12);
}}

.leaflet-container {{
    font-family: Arial, sans-serif;
    background: #fffafd;
}}

.info {{
    background: white;
    padding: 12px 15px;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(150, 80, 110, 0.18);
    border: 1px solid #ffd5e4;
    color: #70485a;
    line-height: 1.6;
}}

.info-title {{
    font-weight: bold;
    color: #9b4567;
    margin-bottom: 4px;
}}

.legend {{
    background: white;
    padding: 12px 14px;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(150, 80, 110, 0.18);
    border: 1px solid #ffd5e4;
    color: #70485a;
}}

.legend-title {{
    font-weight: bold;
    margin-bottom: 8px;
    color: #9b4567;
}}

.legend-item {{
    display: flex;
    align-items: center;
    margin: 5px 0;
    font-size: 12px;
}}

.legend-color {{
    width: 19px;
    height: 19px;
    border-radius: 5px;
    margin-right: 7px;
    border: 1px solid rgba(100,100,100,0.15);
}}

</style>

</head>


<body>

<div id="map"></div>


<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>


<script>

const map = L.map("map", {{
    zoomControl: true,
    scrollWheelZoom: true
}});


// 우리나라 중심 부근
map.setView([36.2, 127.8], 7);


const geojsonData = {geojson_text};


const colors = [
    "#FFF0F6",
    "#FFD4E4",
    "#FFB0CD",
    "#F47FA9",
    "#D84D80"
];


const labels = [
    "19% 미만",
    "19% 이상 ~ 23% 미만",
    "23% 이상 ~ 28% 미만",
    "28% 이상 ~ 38% 미만",
    "38% 이상"
];


function getColor(grade) {{
    return colors[grade] || "#eeeeee";
}}


function style(feature) {{

    return {{
        fillColor: getColor(
            feature.properties.등급
        ),

        weight: 1,

        opacity: 1,

        color: "#ffffff",

        fillOpacity: 0.82
    }};
}}


function onEachFeature(
    feature,
    layer
) {{

    const p = feature.properties;


    const tooltipText =
        "<b>♡ " +
        p.시군구 +
        "</b><br>" +

        p.시도 +
        "<br>" +

        "고령화율 : " +
        Number(p.고령화율).toFixed(2) +
        "%";


    layer.bindTooltip(
        tooltipText,
        {{
            sticky: true,
            direction: "top"
        }}
    );


    layer.on({{

        mouseover: function(e) {{

            e.target.setStyle({{
                weight: 3,
                color: "#a63e68",
                fillOpacity: 1
            }});

            e.target.bringToFront();
        }},


        mouseout: function(e) {{

            e.target.setStyle({{
                weight: 1,
                color: "#ffffff",
                fillOpacity: 0.82
            }});

        }}

    }});

}}


const geoLayer = L.geoJSON(
    geojsonData,
    {{
        style: style,
        onEachFeature: onEachFeature
    }}
).addTo(map);


// 지도에 데이터가 잘 들어갔다면
// 모든 지역이 보이도록 화면을 맞춥니다.
if (geoLayer.getBounds().isValid()) {{
    map.fitBounds(
        geoLayer.getBounds(),
        {{
            padding: [15, 15]
        }}
    );
}}


// =====================================================
// 범례
// =====================================================

const legend = L.control({{
    position: "bottomright"
}});


legend.onAdd = function() {{

    const div = L.DomUtil.create(
        "div",
        "legend"
    );


    div.innerHTML =
        '<div class="legend-title">고령화율</div>';


    for (
        let i = 0;
        i < colors.length;
        i++
    ) {{

        div.innerHTML +=
            '<div class="legend-item">' +

            '<div class="legend-color" ' +
            'style="background:' +
            colors[i] +
            '"></div>' +

            labels[i] +

            '</div>';
    }}


    return div;
}};


legend.addTo(map);

</script>

</body>

</html>
"""


# =========================================================
# 22. 지도 제목
# =========================================================

st.markdown(
    '<div class="section-title">🗺️ 시군구별 고령화율 지도</div>',
    unsafe_allow_html=True,
)


st.markdown(
    f"""
    <div class="info-box">

        <div class="info-box-title">
            🌷 {latest_year}년 기준
        </div>

        <div class="info-box-text">
            각 시군구의 전체 인구 중
            <b>65세 이상 인구가 차지하는 비율</b>을
            색으로 나타낸 지도예요.
            <br>
            지역을 마우스로 올리면 시군구 이름과
            고령화율을 확인할 수 있어요 ♡
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 23. 지도 표시
# =========================================================

components.html(
    map_html,
    height=700,
    scrolling=False,
)


# =========================================================
# 24. 주요 통계
# =========================================================

st.markdown(
    '<div class="section-title">📊 전체 현황</div>',
    unsafe_allow_html=True,
)


total_regions = len(map_geojson["features"])

valid_regions = len(grouped)

max_rate = grouped["고령화율"].max()

min_rate = grouped["고령화율"].min()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="metric-box">

            <div class="metric-title">
                지도에 표시된 시군구
            </div>

            <div class="metric-value">
                {total_regions}개
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        f"""
        <div class="metric-box">

            <div class="metric-title">
                분석 가능한 시군구
            </div>

            <div class="metric-value">
                {valid_regions}개
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        f"""
        <div class="metric-box">

            <div class="metric-title">
                가장 높은 고령화율
            </div>

            <div class="metric-value">
                {max_rate:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:

    st.markdown(
        f"""
        <div class="metric-box">

            <div class="metric-title">
                가장 낮은 고령화율
            </div>

            <div class="metric-value">
                {min_rate:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 25. 상위 / 하위 10개 지역
# =========================================================

st.markdown(
    '<div class="section-title">🔎 지역별 비교</div>',
    unsafe_allow_html=True,
)


top10 = (
    grouped
    .sort_values(
        "고령화율",
        ascending=False,
    )
    .head(10)
    .copy()
)


bottom10 = (
    grouped
    .sort_values(
        "고령화율",
        ascending=True,
    )
    .head(10)
    .copy()
)


# 보기 좋은 표 만들기
top10_table = top10[
    [
        "시도",
        "시군구",
        "전체인구",
        "고령인구",
        "고령화율",
    ]
].copy()


bottom10_table = bottom10[
    [
        "시도",
        "시군구",
        "전체인구",
        "고령인구",
        "고령화율",
    ]
].copy()


top10_table.columns = [
    "시도",
    "시군구",
    "전체 인구",
    "65세 이상 인구",
    "고령화율(%)",
]


bottom10_table.columns = [
    "시도",
    "시군구",
    "전체 인구",
    "65세 이상 인구",
    "고령화율(%)",
]


top10_table["고령화율(%)"] = (
    top10_table["고령화율(%)"]
    .round(2)
)


bottom10_table["고령화율(%)"] = (
    bottom10_table["고령화율(%)"]
    .round(2)
)


left, right = st.columns(2)


# ---------------------------------------------------------
# 고령화율 높은 지역
# ---------------------------------------------------------

with left:

    st.markdown(
        """
        <div class="table-title">
            🌸 고령화율이 높은 지역 TOP 10
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        top10_table,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# 고령화율 낮은 지역
# ---------------------------------------------------------

with right:

    st.markdown(
        """
        <div class="table-title">
            🩷 고령화율이 낮은 지역 TOP 10
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        bottom10_table,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 26. 계산 방법
# =========================================================

st.markdown(
    """
    <div class="formula">

        <b>🌷 고령화율 계산 방법</b>
        <br><br>

        고령화율(%) =
        <b>
        65세 이상 인구 ÷ 전체 인구 × 100
        </b>

        <br><br>

        <span style="font-size:13px;">
        ※ 인구 데이터는 읍·면·동 단위 자료를
        시군구 코드 기준으로 합산하여 계산했습니다.
        </span>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 27. 마지막 안내
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#b08094;
        margin-top:28px;
        font-size:13px;
    ">
        🌸 전국 고령화 현황을 귀엽게 살펴보는 데이터 지도 🌸
        <br>
        Chiikawa friends와 함께 알아봐요 ♡
    </div>
    """,
    unsafe_allow_html=True,
)
