# ============================================================
# 전국 고령화 지도 🌸
# Streamlit + Leaflet
# ============================================================

import io
import json
import requests
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="전국 고령화 지도 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 2. 전체 디자인
# ============================================================

st.markdown(
    """
    <style>

    /* -----------------------------------------------------
       전체 화면
    ----------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                #ffe5ef 0%,
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 15%,
                #ffd9e8 0%,
                transparent 25%
            ),
            #fff7fa;
    }


    /* 기본 여백 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* -----------------------------------------------------
       제목
    ----------------------------------------------------- */

    .main-title {
        background:
            linear-gradient(
                135deg,
                #ff8fb7,
                #ffb6cf
            );

        border-radius: 30px;

        padding: 28px 35px;

        color: white;

        box-shadow:
            0 10px 30px rgba(255, 126, 170, 0.20);

        position: relative;

        overflow: hidden;
    }


    .main-title:after {
        content: "♡  ˚₊‧  ✧  ♡  ˚₊‧  ✧";

        position: absolute;

        right: 25px;
        top: 20px;

        font-size: 25px;

        opacity: 0.7;

        letter-spacing: 8px;
    }


    .main-title h1 {
        margin: 0;

        font-size: 38px;

        font-weight: 800;

        letter-spacing: -1px;
    }


    .main-title p {
        margin:
            8px
            0
            0
            2px;

        font-size: 15px;

        opacity: 0.95;
    }


    /* -----------------------------------------------------
       캐릭터 카드
    ----------------------------------------------------- */

    .friends-title {
        margin-top: 24px;

        margin-bottom: 12px;

        color: #d75b88;

        font-size: 17px;

        font-weight: 800;
    }


    .friends {
        display: flex;

        gap: 14px;

        width: 100%;
    }


    .friend-card {
        flex: 1;

        min-height: 110px;

        border-radius: 24px;

        padding: 15px 18px;

        display: flex;

        align-items: center;

        gap: 14px;

        border: 2px solid rgba(
            255,
            255,
            255,
            0.9
        );

        box-shadow:
            0 7px 20px rgba(
                224,
                109,
                148,
                0.12
            );

        transition:
            transform 0.2s ease;
    }


    .friend-card:hover {
        transform:
            translateY(-4px);
    }


    .friend-chiikawa {
        background: #fff0f5;
    }


    .friend-hachi {
        background: #eaf7ff;
    }


    .friend-usagi {
        background: #fff7dc;
    }


    .friend-face {
        width: 65px;

        height: 65px;

        min-width: 65px;

        border-radius: 50%;

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 34px;

        background: white;

        box-shadow:
            0 4px 10px
            rgba(0,0,0,0.08);

        border: 3px solid white;
    }


    .friend-name {
        font-size: 17px;

        font-weight: 800;

        color: #555;

        margin-bottom: 3px;
    }


    .friend-text {
        font-size: 12px;

        color: #888;

        line-height: 1.4;
    }


    /* -----------------------------------------------------
       설명 카드
    ----------------------------------------------------- */

    .info-box {
        margin-top: 20px;

        background: white;

        border-radius: 22px;

        padding: 18px 22px;

        border:
            1px solid #ffd9e6;

        box-shadow:
            0 5px 18px
            rgba(230, 110, 150, 0.08);

        color: #777;

        font-size: 13px;

        line-height: 1.7;
    }


    .info-box strong {
        color: #df668f;
    }


    /* -----------------------------------------------------
       섹션 제목
    ----------------------------------------------------- */

    .section-title {
        margin-top: 30px;

        margin-bottom: 12px;

        font-size: 22px;

        font-weight: 800;

        color: #c94e7b;
    }


    /* -----------------------------------------------------
       Streamlit metric 카드
    ----------------------------------------------------- */

    [data-testid="stMetric"] {
        background: white;

        border-radius: 22px;

        padding: 18px;

        border: 1px solid #ffdce8;

        box-shadow:
            0 5px 18px
            rgba(230, 110, 150, 0.08);
    }


    [data-testid="stMetricLabel"] {
        color: #b46b86 !important;
    }


    [data-testid="stMetricValue"] {
        color: #dc5f8b !important;
    }


    /* -----------------------------------------------------
       표
    ----------------------------------------------------- */

    .table-title {
        background: #ffe4ee;

        border-radius: 18px 18px 0 0;

        padding: 13px 18px;

        color: #cf527f;

        font-weight: 800;

        margin-top: 10px;
    }


    /* -----------------------------------------------------
       Streamlit dataframe
    ----------------------------------------------------- */

    [data-testid="stDataFrame"] {
        border-radius: 0 0 18px 18px;

        overflow: hidden;

        border: 1px solid #ffdce8;
    }


    /* -----------------------------------------------------
       안내문
    ----------------------------------------------------- */

    .formula {
        margin-top: 25px;

        padding: 18px;

        border-radius: 20px;

        background:
            linear-gradient(
                135deg,
                #fff0f6,
                #fff8fb
            );

        border:
            1px solid #ffd8e7;

        text-align: center;

        color: #9c6076;

        font-size: 13px;
    }


    /* 모바일 */
    @media (max-width: 700px) {

        .main-title h1 {
            font-size: 27px;
        }

        .friends {
            flex-direction: column;
        }

        .friend-card {
            min-height: 80px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. 제목
# ============================================================

st.markdown(
    """
    <div class="main-title">

        <h1>🌸 전국 고령화 지도</h1>

        <p>
            우리나라 시군구별 65세 이상 인구 비율을
            한눈에 살펴보아요 ♡
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. 먼작귀 친구들 영역
# ============================================================

st.markdown(
    '<div class="friends-title">♡ 오늘의 지도 친구들</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="friends">

        <div class="friend-card friend-chiikawa">

            <div class="friend-face">
                🥺
            </div>

            <div>
                <div class="friend-name">
                    치이카와
                </div>

                <div class="friend-text">
                    조심조심 전국 지도를<br>
                    같이 살펴봐요!
                </div>
            </div>

        </div>


        <div class="friend-card friend-hachi">

            <div class="friend-face">
                🩵
            </div>

            <div>
                <div class="friend-name">
                    하치와레
                </div>

                <div class="friend-text">
                    하나씩 차근차근<br>
                    지역을 확인해봐요!
                </div>
            </div>

        </div>


        <div class="friend-card friend-usagi">

            <div class="friend-face">
                🐰
            </div>

            <div>
                <div class="friend-name">
                    우사기
                </div>

                <div class="friend-text">
                    고령화율 높은 곳은<br>
                    어디일까? 야하!
                </div>
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. 데이터 주소
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
# 6. 데이터 불러오기
# ============================================================

@st.cache_data
def load_population():

    response = requests.get(
        POPULATION_URL,
        timeout=60
    )

    response.raise_for_status()

    return pd.read_csv(
        io.BytesIO(response.content),
        compression="gzip",
        dtype={
            "코드": "string"
        }
    )


@st.cache_data
def load_geojson():

    response = requests.get(
        GEOJSON_URL,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# 7. 고령화율 계산
# ============================================================

@st.cache_data
def calculate_aging_rate(df):

    data = df.copy()

    # 코드 = 계산할 숫자가 아니라 행정구역 이름표
    data["코드"] = (
        data["코드"]
        .astype("string")
        .str.strip()
    )

    # 앞 5자리가 시군구 코드
    data["시군구코드"] = (
        data["코드"]
        .str[:5]
    )

    # 최신 연도 찾기
    data["연도_숫자"] = pd.to_numeric(
        data["연도"],
        errors="coerce"
    )

    latest_year = int(
        data["연도_숫자"].max()
    )

    data = data[
        data["연도_숫자"] == latest_year
    ].copy()


    # --------------------------------------------------------
    # 전체 인구
    # --------------------------------------------------------

    total_columns = [
        col
        for col in data.columns
        if str(col).startswith("계_")
    ]


    # --------------------------------------------------------
    # 65세 이상 인구
    # --------------------------------------------------------

    elderly_columns = []

    for age in range(65, 100):

        col = f"계_{age}세"

        if col in data.columns:
            elderly_columns.append(col)


    if "계_100세 이상" in data.columns:
        elderly_columns.append(
            "계_100세 이상"
        )


    if len(total_columns) == 0:
        raise ValueError(
            "계_로 시작하는 인구 열을 찾지 못했습니다."
        )


    if len(elderly_columns) == 0:
        raise ValueError(
            "65세 이상 인구 열을 찾지 못했습니다."
        )


    # 숫자로 변환
    for col in total_columns:

        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        ).fillna(0)


    for col in elderly_columns:

        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        ).fillna(0)


    # 전체 인구
    data["전체인구"] = (
        data[total_columns]
        .sum(axis=1)
    )


    # 65세 이상
    data["65세이상인구"] = (
        data[elderly_columns]
        .sum(axis=1)
    )


    # --------------------------------------------------------
    # 시군구 단위로 합치기
    # --------------------------------------------------------

    result = (
        data
        .groupby(
            "시군구코드",
            as_index=False
        )[
            [
                "전체인구",
                "65세이상인구"
            ]
        ]
        .sum()
    )


    # 시군구 이름 / 시도
    info = (
        data[
            [
                "시군구코드",
                "시군구",
                "시도"
            ]
        ]
        .drop_duplicates(
            "시군구코드"
        )
    )


    result = result.merge(
        info,
        on="시군구코드",
        how="left"
    )


    # --------------------------------------------------------
    # 고령화율
    # --------------------------------------------------------

    result["고령화율"] = np.where(

        result["전체인구"] > 0,

        result["65세이상인구"]
        / result["전체인구"]
        * 100,

        np.nan
    )


    result["연도"] = latest_year

    return result


# ============================================================
# 8. 5단계 색상
# ============================================================

COLORS = [
    "#FFF0F6",
    "#FFD4E4",
    "#FFB0CD",
    "#F47FA9",
    "#D84D80"
]


LABELS = [
    "19% 미만",
    "19% 이상 ~ 23% 미만",
    "23% 이상 ~ 28% 미만",
    "28% 이상 ~ 38% 미만",
    "38% 이상"
]


def get_grade(rate):

    if pd.isna(rate):
        return None

    if rate < 19:
        return 0

    if rate < 23:
        return 1

    if rate < 28:
        return 2

    if rate < 38:
        return 3

    return 4


# ============================================================
# 9. 지도용 GeoJSON
# ============================================================

def make_map_geojson(
    geojson,
    population
):

    data_dict = {}

    for _, row in population.iterrows():

        code = (
            str(row["시군구코드"])
            .strip()
            .zfill(5)
        )

        data_dict[code] = {

            "시군구":
                str(row["시군구"]),

            "시도":
                str(row["시도"]),

            "고령화율":
                None
                if pd.isna(row["고령화율"])
                else float(row["고령화율"])
        }


    result = json.loads(
        json.dumps(
            geojson,
            ensure_ascii=False
        )
    )


    for feature in result["features"]:

        props = feature.get(
            "properties",
            {}
        )

        code = (
            str(
                props.get(
                    "코드",
                    ""
                )
            )
            .strip()
            .zfill(5)
        )


        info = data_dict.get(code)


        if info:

            props["시군구"] = info[
                "시군구"
            ]

            props["시도"] = info[
                "시도"
            ]

            props["고령화율"] = info[
                "고령화율"
            ]

            props["등급"] = get_grade(
                info["고령화율"]
            )

        else:

            props["고령화율"] = None

            props["등급"] = None


    return result


# ============================================================
# 10. Leaflet 지도
# ============================================================

def create_map_html(
    map_geojson
):

    geojson_text = json.dumps(
        map_geojson,
        ensure_ascii=False
    )

    colors_text = json.dumps(
        COLORS
    )

    labels_text = json.dumps(
        LABELS,
        ensure_ascii=False
    )


    html = f"""
<!DOCTYPE html>

<html lang="ko">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,
      initial-scale=1.0">


<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>


<script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
</script>


<style>

html,
body {{
    margin: 0;
    padding: 0;
    background: #fff7fa;
}}


#map {{
    width: 100%;
    height: 700px;

    background:
        radial-gradient(
            circle at 50% 40%,
            #fff4f8,
            #fffafb
        );

    border-radius: 26px;

    overflow: hidden;
}}


/* 범례 */

.legend {{
    background: rgba(
        255,
        255,
        255,
        0.96
    );

    padding: 14px 16px;

    border-radius: 18px;

    box-shadow:
        0 5px 18px
        rgba(205, 82, 124, 0.18);

    border:
        1px solid #ffd9e7;

    font-family:
        Arial,
        "Malgun Gothic",
        sans-serif;

    color: #777;

    font-size: 12px;
}}


.legend-title {{
    color: #ce5a84;

    font-weight: 800;

    font-size: 14px;

    margin-bottom: 7px;
}}


.legend-item {{
    display: flex;

    align-items: center;

    margin: 4px 0;

    white-space: nowrap;
}}


.legend-color {{
    width: 18px;

    height: 18px;

    border-radius: 6px;

    margin-right: 7px;

    border:
        1px solid
        rgba(190,100,130,0.15);
}}


/* 마우스오버 */

.leaflet-tooltip {{
    background: white;

    border:
        1px solid #ffbfd4;

    border-radius: 13px;

    box-shadow:
        0 5px 15px
        rgba(205,82,124,0.18);

    color: #666;

    padding:
        8px 11px;

    font-family:
        Arial,
        "Malgun Gothic",
        sans-serif;
}}


.leaflet-tooltip-top:before {{
    border-top-color: #ffbfd4;
}}


</style>

</head>


<body>


<div id="map"></div>


<script>


const mapData = {geojson_text};

const colors = {colors_text};

const labels = {labels_text};


const map = L.map(
    "map",
    {{
        zoomControl: true,
        attributionControl: false
    }}
);


/* 색상 */

function getColor(grade) {{

    if (
        grade === null ||
        grade === undefined ||
        grade === ""
    ) {{
        return "#eeeeee";
    }}

    return colors[
        Number(grade)
    ];
}}


/* 마우스를 올렸을 때 */

function highlightFeature(e) {{

    const layer = e.target;

    layer.setStyle({{
        weight: 2.2,
        color: "#b83f6c",
        fillOpacity: 1
    }});

    layer.bringToFront();
}}


/* 마우스가 빠졌을 때 */

function resetHighlight(e) {{

    geojsonLayer.resetStyle(
        e.target
    );
}}


/* 지역 정보 */

function onEachFeature(
    feature,
    layer
) {{

    const p =
        feature.properties || {{}};


    const sigungu =
        p["시군구"]
        || "정보 없음";


    const sido =
        p["시도"]
        || "정보 없음";


    const rate =
        p["고령화율"];


    let rateText =
        "자료 없음";


    if (
        rate !== null &&
        rate !== undefined &&
        !isNaN(rate)
    ) {{

        rateText =
            Number(rate)
            .toFixed(2)
            + "%";

    }}


    layer.bindTooltip(

        "<b>♡ "
        + sigungu
        + "</b>"
        + "<br>"
        + sido
        + "<br>"
        + "고령화율 : "
        + rateText,

        {{
            sticky: true,
            direction: "top"
        }}

    );


    layer.on({{

        mouseover:
            highlightFeature,

        mouseout:
            resetHighlight

    }});

}}


/* 지도 */

const geojsonLayer =
    L.geoJSON(

        mapData,

        {{

            style:
                function(feature) {{

                    const grade =
                        feature
                        .properties
                        ["등급"];


                    return {{

                        fillColor:
                            getColor(
                                grade
                            ),

                        weight:
                            0.7,

                        color:
                            "#FFFFFF",

                        fillOpacity:
                            0.92

                    }};

                }},


            onEachFeature:
                onEachFeature

        }}

    ).addTo(map);


/* 대한민국 전체가 보이게 */

const bounds =
    geojsonLayer.getBounds();


if (bounds.isValid()) {{

    map.fitBounds(
        bounds,
        {{
            padding:
                [15, 15]
        }}
    );

}}


/* 범례 */

const legend =
    L.control({{
        position:
            "bottomright"
    }});


legend.onAdd =
    function() {{

        const div =
            L.DomUtil.create(
                "div",
                "legend"
            );


        let html =
            '<div class="legend-title">'
            + '♡ 고령화율'
            + '</div>';


        for (
            let i = 0;
            i < labels.length;
            i++
        ) {{

            html +=

                '<div class="legend-item">'

                + '<span '
                + 'class="legend-color" '
                + 'style="background:'
                + colors[i]
                + '"></span>'

                + labels[i]

                + '</div>';
        }}


        html +=

            '<div class="legend-item">'

            + '<span '
            + 'class="legend-color" '
            + 'style="background:#eeeeee">'
            + '</span>'

            + '자료 없음'

            + '</div>';


        div.innerHTML =
            html;


        return div;
    }};


legend.addTo(map);


</script>


</body>

</html>
"""

    return html


# ============================================================
# 11. 데이터 실행
# ============================================================

try:

    with st.spinner(
        "🌸 전국 데이터를 가져오는 중..."
    ):

        population_df =
            load_population()

        geojson =
            load_geojson()

        sigungu_df =
            calculate_aging_rate(
                population_df
            )

        map_geojson =
            make_map_geojson(
                geojson,
                sigungu_df
            )

except Exception as e:

    st.error(
        "앗! 데이터를 불러오는 중 문제가 생겼어요 🥺"
    )

    st.code(
        f"{type(e).__name__}: {e}"
    )

    st.stop()


# ============================================================
# 12. 최신 연도
# ============================================================

latest_year = int(
    sigungu_df["연도"].iloc[0]
)


st.markdown(
    f"""
    <div class="info-box">

    🌷 <strong>{latest_year}년 최신 자료</strong>를
    기준으로 계산했어요.<br>

    읍·면·동 인구를 시군구별로 합친 뒤
    <strong>65세 이상 인구 ÷ 전체 인구 × 100</strong>
    으로 고령화율을 계산했습니다.<br>

    지도는 지역 이름이 아니라
    <strong>시군구 코드 앞 5자리</strong>를 이용해 연결했습니다.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 13. 숫자 요약
# ============================================================

st.markdown(
    '<div class="section-title">🌷 한눈에 보기</div>',
    unsafe_allow_html=True
)


total_regions = len(
    geojson.get(
        "features",
        []
    )
)


valid_regions = (
    sigungu_df[
        sigungu_df["고령화율"].notna()
    ]
    .shape[0]
)


highest_rate = (
    sigungu_df["고령화율"]
    .max()
)


lowest_rate = (
    sigungu_df["고령화율"]
    .min()
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "🗺️ 지도 시군구",
        f"{total_regions}개"
    )


with c2:

    st.metric(
        "💗 분석 지역",
        f"{valid_regions}개"
    )


with c3:

    st.metric(
        "🎀 가장 높은 고령화율",
        f"{highest_rate:.1f}%"
    )


with c4:

    st.metric(
        "🌸 가장 낮은 고령화율",
        f"{lowest_rate:.1f}%"
    )


# ============================================================
# 14. 지도
# ============================================================

st.markdown(
    '<div class="section-title">🗺️ 전국 시군구 고령화율</div>',
    unsafe_allow_html=True
)


map_html = create_map_html(
    map_geojson
)


components.html(
    map_html,
    height=720,
    scrolling=False
)


# ============================================================
# 15. 순위 계산
# ============================================================

ranking = (
    sigungu_df[
        sigungu_df["고령화율"].notna()
    ]
    .copy()
)


# 높은 곳

top10 = (
    ranking
    .sort_values(
        "고령화율",
        ascending=False
    )
    .head(10)
    .copy()
)


top10["순위"] = range(
    1,
    len(top10) + 1
)


top10["고령화율"] = (
    top10["고령화율"]
    .map(
        lambda x:
            f"{x:.2f}%"
    )
)


top10 = top10[
    [
        "순위",
        "시도",
        "시군구",
        "고령화율"
    ]
]


# 낮은 곳

bottom10 = (
    ranking
    .sort_values(
        "고령화율",
        ascending=True
    )
    .head(10)
    .copy()
)


bottom10["순위"] = range(
    1,
    len(bottom10) + 1
)


bottom10["고령화율"] = (
    bottom10["고령화율"]
    .map(
        lambda x:
            f"{x:.2f}%"
    )
)


bottom10 = bottom10[
    [
        "순위",
        "시도",
        "시군구",
        "고령화율"
    ]
]


# ============================================================
# 16. 순위 표
# ============================================================

st.markdown(
    '<div class="section-title">💗 고령화율 랭킹</div>',
    unsafe_allow_html=True
)


left, right = st.columns(2)


with left:

    st.markdown(
        """
        <div class="table-title">
            🌸 고령화율 높은 곳 TOP 10
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True
    )


with right:

    st.markdown(
        """
        <div class="table-title">
            🩷 고령화율 낮은 곳 TOP 10
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        bottom10,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 17. 하단 설명
# ============================================================

st.markdown(
    f"""
    <div class="formula">

        ♡ <strong>고령화율</strong>
        =
        65세 이상 인구 ÷ 전체 인구 × 100

        <br><br>

        🌷 색상 기준 :
        <strong>
        19% · 23% · 28% · 38%
        </strong>

        <br>

        ✨ 낮은 지역은 연하게,
        높은 지역은 진하게 표시됩니다.

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:25px;
        color:#d59aae;
        font-size:12px;
    ">
        made with ♡ · 전국 고령화 지도
    </div>
    """,
    unsafe_allow_html=True
)
