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
    page_title="전국 고령화 지도",
    page_icon="🩷",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# 2. 핑크핑크한 디자인
# =========================================================

st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(180deg, #fff8fb 0%, #fffafd 50%, #fff4f8 100%);
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

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

.section-title {
    color: #914664;
    font-size: 25px;
    font-weight: 800;
    margin: 25px 0 12px 0;
}

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

.table-title {
    background: #fff0f5;
    color: #984565;
    border-radius: 15px;
    padding: 12px 16px;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
}

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

.pyramid-box {
    background: #ffffff;
    border: 2px solid #ffd7e5;
    border-radius: 22px;
    padding: 18px 20px 22px 20px;
    box-shadow: 0 5px 18px rgba(190, 105, 140, 0.08);
}

.pyramid-header {
    display: grid;
    grid-template-columns: 1fr 90px 1fr;
    align-items: center;
    margin-bottom: 10px;
    font-weight: 700;
    font-size: 13px;
}

.pyramid-header .male-title {
    text-align: right;
    color: #7e9bc7;
    padding-right: 15px;
}

.pyramid-header .age-title {
    text-align: center;
    color: #927082;
}

.pyramid-header .female-title {
    text-align: left;
    color: #d9779b;
    padding-left: 15px;
}

.pyramid-row {
    display: grid;
    grid-template-columns: 1fr 90px 1fr;
    align-items: center;
    min-height: 34px;
}

.pyramid-side {
    height: 24px;
    display: flex;
    align-items: center;
}

.male-side {
    justify-content: flex-end;
}

.female-side {
    justify-content: flex-start;
}

.male-bar {
    height: 24px;
    background: #c7d8f0;
    border-radius: 7px 0 0 7px;
}

.female-bar {
    height: 24px;
    background: #f4bfd2;
    border-radius: 0 7px 7px 0;
}

.pyramid-age {
    text-align: center;
    color: #765b69;
    font-size: 12px;
    font-weight: 700;
}

.pyramid-number {
    font-size: 10px;
    color: #9b8290;
    margin: 0 5px;
    white-space: nowrap;
}

.pyramid-footer {
    text-align: center;
    color: #a27d8d;
    font-size: 12px;
    margin-top: 14px;
}

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

    .pyramid-header,
    .pyramid-row {
        grid-template-columns: 1fr 65px 1fr;
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
    """<div class="main-title">🩷 전국 고령화 지도 🩷</div>""",
    unsafe_allow_html=True,
)

st.markdown(
    """<div class="sub-title">우리나라 시군구별 65세 이상 인구 비율을 한눈에 살펴봐요 ♡</div>""",
    unsafe_allow_html=True,
)


# =========================================================
# 4. 먼작귀 친구들 장식
# =========================================================

st.markdown(
    """
<div class="friends">

<div class="friend-card chiikawa">
<div class="friend-emoji">🐱</div>
<h3>치이카와</h3>
<p>오늘도 함께 알아봐요 ♡</p>
</div>

<div class="friend-card hachiware">
<div class="friend-emoji">♡</div>
<h3>하치와레</h3>
<p>우리나라의 고령화 현황!</p>
</div>

<div class="friend-card usagi">
<div class="friend-emoji">🐱</div>
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

    return pd.read_csv(
        io.BytesIO(response.content),
        compression="gzip",
        dtype={"코드": "string"},
    )


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
# 10. 행정구역 코드 정리
# =========================================================

population_df["코드"] = (
    population_df["코드"]
    .astype("string")
    .str.strip()
)

# 읍면동 코드의 앞 5자리가 시군구 코드입니다.
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
# 12. 전체 연령 인구 계산
# =========================================================

total_age_columns = [
    column
    for column in latest_df.columns
    if column.startswith("계_")
]

for column in total_age_columns:
    latest_df[column] = pd.to_numeric(
        latest_df[column],
        errors="coerce",
    ).fillna(0)

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

if "계_100세 이상" in latest_df.columns:
    elderly_columns.append(
        "계_100세 이상"
    )

latest_df["65세이상인구"] = latest_df[
    elderly_columns
].sum(axis=1)


# =========================================================
# 14. 시군구별 합산
# =========================================================

grouped = (
    latest_df
    .groupby(
        "시군구코드",
        as_index=False,
    )
    .agg(
        전체인구=("전체인구", "sum"),
        고령인구=("65세이상인구", "sum"),
    )
)


# =========================================================
# 15. 시군구 이름과 시도 연결
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

grouped = grouped[
    grouped["고령화율"].notna()
].copy()

grouped["시군구코드"] = (
    grouped["시군구코드"]
    .astype(str)
    .str.strip()
    .str.zfill(5)
)


# =========================================================
# 17. 고령화율 등급
# =========================================================

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


grouped["등급"] = grouped[
    "고령화율"
].apply(get_grade)


# =========================================================
# 18. 지도용 GeoJSON 만들기
# =========================================================

def make_map_geojson(
    original_geojson,
    region_data,
):

    result = {
        "type": "FeatureCollection",
        "features": [],
    }

    data_dict = {}

    for _, row in region_data.iterrows():

        code = (
            str(row["시군구코드"])
            .strip()
            .zfill(5)
        )

        data_dict[code] = {
            "시군구": str(row["시군구"]),
            "시도": str(row["시도"]),
            "고령화율": float(
                row["고령화율"]
            ),
            "등급": int(
                row["등급"]
            ),
        }

    for feature in original_geojson[
        "features"
    ]:

        properties = feature.get(
            "properties",
            {},
        )

        code = properties.get(
            "코드"
        )

        if code is None:
            code = properties.get(
                "code"
            )

        if code is None:
            continue

        code = (
            str(code)
            .strip()
            .zfill(5)
        )

        if code not in data_dict:
            continue

        result["features"].append(
            {
                "type": feature["type"],
                "geometry": feature[
                    "geometry"
                ],
                "properties": {
                    "코드": code,
                    "시군구": data_dict[
                        code
                    ]["시군구"],
                    "시도": data_dict[
                        code
                    ]["시도"],
                    "고령화율": data_dict[
                        code
                    ]["고령화율"],
                    "등급": data_dict[
                        code
                    ]["등급"],
                },
            }
        )

    return result


map_geojson = make_map_geojson(
    geojson,
    grouped,
)


# =========================================================
# 19. 지도 색상
# =========================================================

MAP_COLORS = [
    "#FFF0F6",
    "#FFD4E4",
    "#FFB0CD",
    "#F47FA9",
    "#D84D80",
]


# =========================================================
# 20. 지도 HTML
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


map.setView(
    [36.2, 127.8],
    7
);


const geojsonData =
    {geojson_text};


const colors =
    {json.dumps(MAP_COLORS)};


const labels = [
    "19% 미만",
    "19% 이상 ~ 23% 미만",
    "23% 이상 ~ 28% 미만",
    "28% 이상 ~ 38% 미만",
    "38% 이상"
];


function getColor(grade) {{

    return (
        colors[grade]
        || "#eeeeee"
    );

}}


function style(feature) {{

    return {{

        fillColor:
            getColor(
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

    const p =
        feature.properties;


    const tooltipText =

        "<b>♡ "
        + p.시군구
        + "</b><br>"
        + p.시도
        + "<br>"
        + "고령화율 : "
        + Number(
            p.고령화율
        ).toFixed(2)
        + "%";


    layer.bindTooltip(
        tooltipText,
        {{
            sticky: true,
            direction: "top"
        }}
    );


    layer.on({{

        mouseover:
            function(e) {{

                e.target.setStyle({{

                    weight: 3,

                    color: "#a63e68",

                    fillOpacity: 1

                }});

                e.target.bringToFront();

            }},


        mouseout:
            function(e) {{

                e.target.setStyle({{

                    weight: 1,

                    color: "#ffffff",

                    fillOpacity: 0.82

                }});

            }}

    }});

}}


const geoLayer =
    L.geoJSON(
        geojsonData,
        {{
            style: style,
            onEachFeature:
                onEachFeature
        }}
    ).addTo(map);


if (
    geoLayer
        .getBounds()
        .isValid()
) {{

    map.fitBounds(
        geoLayer.getBounds(),
        {{
            padding: [
                15,
                15
            ]
        }}
    );

}}


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


        div.innerHTML =
            '<div class="legend-title">고령화율</div>';


        for (
            let i = 0;
            i < colors.length;
            i++
        ) {{

            div.innerHTML +=

                '<div class="legend-item">'
                + '<div class="legend-color" '
                + 'style="background:'
                + colors[i]
                + '"></div>'
                + labels[i]
                + '</div>';

        }}


        return div;

    };


legend.addTo(map);

</script>

</body>

</html>
"""


# =========================================================
# 21. 지도 표시
# =========================================================

st.markdown(
    '<div class="section-title">🗺️ 시군구별 고령화율 지도</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="info-box">
<div class="info-box-title">♡ {latest_year}년 기준</div>
<div class="info-box-text">
각 시군구의 전체 인구 중
<b>65세 이상 인구가 차지하는 비율</b>을
색으로 나타낸 지도예요.
<br>
지역을 마우스로 올리면
시군구 이름과 고령화율을 확인할 수 있어요 ♡
</div>
</div>
""",
    unsafe_allow_html=True,
)

components.html(
    map_html,
    height=700,
    scrolling=False,
)


# =========================================================
# 22. 전체 현황
# =========================================================

st.markdown(
    '<div class="section-title">📊 전체 현황</div>',
    unsafe_allow_html=True,
)

total_regions = len(
    map_geojson["features"]
)

valid_regions = len(grouped)

max_rate = grouped[
    "고령화율"
].max()

min_rate = grouped[
    "고령화율"
].min()


col1, col2, col3, col4 = st.columns(4)


metric_items = [
    (
        col1,
        "지도에 표시된 시군구",
        f"{total_regions}개",
    ),
    (
        col2,
        "분석 가능한 시군구",
        f"{valid_regions}개",
    ),
    (
        col3,
        "가장 높은 고령화율",
        f"{max_rate:.2f}%",
    ),
    (
        col4,
        "가장 낮은 고령화율",
        f"{min_rate:.2f}%",
    ),
]


for column, title, value in metric_items:

    with column:

        st.markdown(
            f"""
<div class="metric-box">
<div class="metric-title">{title}</div>
<div class="metric-value">{value}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# =========================================================
# 23. 인구 피라미드
# =========================================================

st.markdown(
    '<div class="section-title">🐱 지역별 인구 피라미드</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="info-box">
<div class="info-box-title">♡ 연령별·성별 인구 구조를 확인해보세요</div>
<div class="info-box-text">
아래에서 지역을 선택하면
남성과 여성의 연령대별 인구를 한눈에 비교할 수 있어요.
가운데 나이대를 기준으로
왼쪽은 남성, 오른쪽은 여성을 나타냅니다.
</div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 24. 지역 선택
# =========================================================

region_options = [
    "전국"
]

region_to_code = {}


region_list = (
    grouped[
        [
            "시군구코드",
            "시군구",
            "시도",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "시도",
            "시군구",
        ]
    )
)


for _, row in region_list.iterrows():

    label = (
        f"{row['시도']} | "
        f"{row['시군구']}"
    )

    region_options.append(
        label
    )

    region_to_code[label] = str(
        row["시군구코드"]
    )


selected_region = st.selectbox(
    "지역 선택",
    region_options,
    index=0,
)


if selected_region == "전국":

    pyramid_source = latest_df

else:

    selected_code = (
        region_to_code[
            selected_region
        ]
    )

    pyramid_source = latest_df[
        latest_df["시군구코드"]
        == selected_code
    ]


# =========================================================
# 25. 연령대 설정
# =========================================================

age_groups = [

    (
        "0~9세",
        list(range(0, 10)),
    ),

    (
        "10~19세",
        list(range(10, 20)),
    ),

    (
        "20~29세",
        list(range(20, 30)),
    ),

    (
        "30~39세",
        list(range(30, 40)),
    ),

    (
        "40~49세",
        list(range(40, 50)),
    ),

    (
        "50~59세",
        list(range(50, 60)),
    ),

    (
        "60~69세",
        list(range(60, 70)),
    ),

    (
        "70~79세",
        list(range(70, 80)),
    ),

    (
        "80세 이상",
        list(range(80, 100)),
    ),

]


# =========================================================
# 26. 남녀 연령별 인구 계산
# =========================================================

def sum_age_columns(
    source,
    prefix,
    ages,
):

    columns = []

    for age in ages:

        column = (
            f"{prefix}_{age}세"
        )

        if column in source.columns:

            columns.append(
                column
            )


    if (
        prefix == "남"
        and "남_100세 이상"
        in source.columns
        and ages[-1] >= 80
    ):

        columns.append(
            "남_100세 이상"
        )


    if (
        prefix == "여"
        and "여_100세 이상"
        in source.columns
        and ages[-1] >= 80
    ):

        columns.append(
            "여_100세 이상"
        )


    if not columns:
        return 0


    values = (
        source[columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .fillna(0)
    )


    return int(
        values
        .sum()
        .sum()
    )


pyramid_rows = []


for age_label, ages in age_groups:

    male = sum_age_columns(
        pyramid_source,
        "남",
        ages,
    )

    female = sum_age_columns(
        pyramid_source,
        "여",
        ages,
    )

    pyramid_rows.append(
        (
            age_label,
            male,
            female,
        )
    )


max_population = max(
    [
        max(
            male,
            female,
        )
        for _, male, female
        in pyramid_rows
    ] + [1]
)


# =========================================================
# 27. 인구 피라미드 HTML 만들기
# =========================================================

pyramid_html = """
<div class="pyramid-box">

<div class="pyramid-header">
<div class="male-title">남성</div>
<div class="age-title">연령</div>
<div class="female-title">여성</div>
</div>
"""


for (
    age_label,
    male,
    female,
) in pyramid_rows:

    male_width = (
        male
        / max_population
        * 100
    )

    female_width = (
        female
        / max_population
        * 100
    )

    pyramid_html += f"""
<div class="pyramid-row">

<div class="pyramid-side male-side">

<div class="pyramid-number">
{male:,}명
</div>

<div
    class="male-bar"
    style="width:{male_width:.1f}%"
></div>

</div>


<div class="pyramid-age">
{age_label}
</div>


<div class="pyramid-side female-side">

<div
    class="female-bar"
    style="width:{female_width:.1f}%"
></div>

<div class="pyramid-number">
{female:,}명
</div>

</div>

</div>
"""


pyramid_html += """
<div class="pyramid-footer">
※ 막대가 길수록 해당 연령대의 인구가 많습니다.
</div>

</div>
"""


st.markdown(
    pyramid_html,
    unsafe_allow_html=True,
)


# =========================================================
# 28. 선택 지역의 추가 지표
# =========================================================

selected_total = int(
    pyramid_source["전체인구"]
    .sum()
)

selected_elderly = int(
    pyramid_source[
        "65세이상인구"
    ]
    .sum()
)


# 15~64세 생산연령인구
working_columns = []

for age in range(15, 65):

    column = f"계_{age}세"

    if column in pyramid_source.columns:

        working_columns.append(
            column
        )


if working_columns:

    selected_working = int(
        pyramid_source[
            working_columns
        ]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .fillna(0)
        .sum()
        .sum()
    )

else:

    selected_working = 0


selected_aging_rate = (

    selected_elderly
    / selected_total
    * 100

    if selected_total > 0
    else 0
)


selected_dependency = (

    selected_elderly
    / selected_working
    * 100

    if selected_working > 0
    else 0
)


st.markdown(
    "<br>",
    unsafe_allow_html=True,
)


pcol1, pcol2, pcol3 = st.columns(3)


selected_metrics = [

    (
        pcol1,
        "선택 지역 총인구",
        f"{selected_total:,}명",
    ),

    (
        pcol2,
        "고령화율",
        f"{selected_aging_rate:.2f}%",
    ),

    (
        pcol3,
        "노년부양비",
        f"{selected_dependency:.2f}",
    ),

]


for column, title, value in selected_metrics:

    with column:

        st.markdown(
            f"""
<div class="metric-box">
<div class="metric-title">{title}</div>
<div class="metric-value">{value}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# =========================================================
# 29. 지역별 비교표
# =========================================================

st.markdown(
    '<div class="section-title">🔎 지역별 고령화율 비교</div>',
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


top10_table[
    "고령화율(%)"
] = top10_table[
    "고령화율(%)"
].round(2)


bottom10_table[
    "고령화율(%)"
] = bottom10_table[
    "고령화율(%)"
].round(2)


left, right = st.columns(2)


with left:

    st.markdown(
        '<div class="table-title">♡ 고령화율이 높은 지역 TOP 10</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        top10_table,
        use_container_width=True,
        hide_index=True,
    )


with right:

    st.markdown(
        '<div class="table-title">🐱 고령화율이 낮은 지역 TOP 10</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        bottom10_table,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 30. 계산 방법
# =========================================================

st.markdown(
    """
<div class="formula">

<b>♡ 고령화율 계산 방법</b>

<br><br>

고령화율(%)
=
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
# 31. 하단 문구
# =========================================================

st.markdown(
    """
<div style="
text-align:center;
color:#b08094;
margin-top:28px;
font-size:13px;
">

🐱 ♡ 우리나라의 인구 구조를 재미있게 살펴봐요 ♡ 🐱

</div>
""",
    unsafe_allow_html=True,
)
