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
    layout="wide"
)


# =========================================================
# 2. 화면 디자인
# =========================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff8fb, #fffafd, #fff4f8);
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
}

.main-title {
    text-align: center;
    color: #914664;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #a8788e;
    margin-bottom: 30px;
}

.info-box {
    background: white;
    border: 2px solid #ffd7e5;
    border-radius: 20px;
    padding: 18px 22px;
    margin: 15px 0 25px 0;
    box-shadow: 0 5px 18px rgba(190,105,140,.08);
}

.info-title {
    color: #b34f76;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 7px;
}

.info-text {
    color: #765867;
    line-height: 1.7;
}

.section-title {
    color: #914664;
    font-size: 25px;
    font-weight: 800;
    margin: 28px 0 12px 0;
}

.metric-box {
    background: white;
    border: 2px solid #ffe0ea;
    border-radius: 20px;
    padding: 18px;
    text-align: center;
}

.metric-title {
    color: #aa7188;
    font-size: 13px;
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

.pyramid-box {
    background: white;
    border: 2px solid #ffd7e5;
    border-radius: 22px;
    padding: 20px;
}

.pyramid-row {
    display: grid;
    grid-template-columns: 1fr 80px 1fr;
    align-items: center;
    min-height: 38px;
}

.pyramid-label {
    text-align: center;
    color: #765b69;
    font-size: 12px;
    font-weight: 700;
}

.left-side {
    display: flex;
    justify-content: flex-end;
    align-items: center;
}

.right-side {
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

.male-bar {
    height: 25px;
    background: #c7d8f0;
    border-radius: 7px 0 0 7px;
}

.female-bar {
    height: 25px;
    background: #f4bfd2;
    border-radius: 0 7px 7px 0;
}

.pyramid-number {
    color: #9b8290;
    font-size: 10px;
    margin: 0 5px;
    white-space: nowrap;
}

.formula {
    background: white;
    border: 2px dashed #f2b7ca;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    color: #795668;
    margin-top: 25px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. 제목
# =========================================================

st.markdown(
    '<div class="main-title">🩷 전국 고령화 지도 🩷</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">우리나라 시군구별 65세 이상 인구 비율을 한눈에 살펴봐요 ♡</div>',
    unsafe_allow_html=True
)


# =========================================================
# 4. 데이터 주소
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
# 5. 데이터 불러오기
# =========================================================

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
        dtype={"코드": "string"}
    )


@st.cache_data
def load_geojson():
    response = requests.get(
        GEOJSON_URL,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


try:
    population = load_population()
    geojson = load_geojson()

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# 6. 기본 데이터 정리
# =========================================================

population["연도"] = pd.to_numeric(
    population["연도"],
    errors="coerce"
)

latest_year = int(
    population["연도"]
    .dropna()
    .max()
)

population["코드"] = (
    population["코드"]
    .astype("string")
    .str.strip()
)

population["시군구코드"] = (
    population["코드"]
    .str[:5]
)

data = population[
    population["연도"] == latest_year
].copy()


# =========================================================
# 7. 전체 인구 계산
# =========================================================

total_cols = [
    c for c in data.columns
    if c.startswith("계_")
]

for c in total_cols:
    data[c] = pd.to_numeric(
        data[c],
        errors="coerce"
    ).fillna(0)

data["전체인구"] = data[
    total_cols
].sum(axis=1)


# =========================================================
# 8. 65세 이상 인구 계산
# =========================================================

elderly_cols = []

for age in range(65, 100):

    c = "계_" + str(age) + "세"

    if c in data.columns:
        elderly_cols.append(c)


if "계_100세 이상" in data.columns:
    elderly_cols.append(
        "계_100세 이상"
    )


data["고령인구"] = data[
    elderly_cols
].sum(axis=1)


# =========================================================
# 9. 시군구별 집계
# =========================================================

grouped = (
    data
    .groupby(
        "시군구코드",
        as_index=False
    )
    .agg(
        전체인구=("전체인구", "sum"),
        고령인구=("고령인구", "sum")
    )
)


names = (
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


grouped = grouped.merge(
    names,
    on="시군구코드",
    how="left"
)


# =========================================================
# 10. 고령화율 계산
# =========================================================

grouped["고령화율"] = np.where(
    grouped["전체인구"] > 0,
    grouped["고령인구"]
    / grouped["전체인구"]
    * 100,
    np.nan
)


grouped = grouped.dropna(
    subset=["고령화율"]
).copy()


grouped["시군구코드"] = (
    grouped["시군구코드"]
    .astype(str)
    .str.zfill(5)
)


# =========================================================
# 11. 고령화율 등급
# =========================================================

def grade(rate):

    if rate < 19:
        return 0

    if rate < 23:
        return 1

    if rate < 28:
        return 2

    if rate < 38:
        return 3

    return 4


grouped["등급"] = (
    grouped["고령화율"]
    .apply(grade)
)


# =========================================================
# 12. 지도 데이터 만들기
# =========================================================

lookup = {}


for _, row in grouped.iterrows():

    code = (
        str(row["시군구코드"])
        .zfill(5)
    )

    lookup[code] = {
        "시군구": str(row["시군구"]),
        "시도": str(row["시도"]),
        "고령화율": float(
            row["고령화율"]
        ),
        "등급": int(
            row["등급"]
        )
    }


features = []


for feature in geojson.get(
    "features",
    []
):

    props = feature.get(
        "properties",
        {}
    )

    code = props.get("코드")

    if code is None:
        code = props.get("code")

    if code is None:
        continue

    code = str(code).zfill(5)

    if code not in lookup:
        continue

    features.append(
        {
            "type": feature.get(
                "type",
                "Feature"
            ),

            "geometry": feature.get(
                "geometry"
            ),

            "properties": {
                "코드": code,

                "시군구": lookup[
                    code
                ]["시군구"],

                "시도": lookup[
                    code
                ]["시도"],

                "고령화율": lookup[
                    code
                ]["고령화율"],

                "등급": lookup[
                    code
                ]["등급"]
            }
        }
    )


map_data = {
    "type": "FeatureCollection",
    "features": features
}


# =========================================================
# 13. 지도 색상
# =========================================================

colors = [
    "#FFF0F6",
    "#FFD4E4",
    "#FFB0CD",
    "#F47FA9",
    "#D84D80"
]


geojson_text = json.dumps(
    map_data,
    ensure_ascii=False
)

colors_text = json.dumps(
    colors,
    ensure_ascii=False
)


# =========================================================
# 14. 지도 HTML
# =========================================================
# 여기서는 f-string을 사용하지 않습니다.
# 그래서 JavaScript의 { } 때문에 생기는 오류가 없습니다.

map_html = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
>

<style>

html,
body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}

#map {
    width: 100%;
    height: 650px;
    border: 3px solid #ffd8e6;
    border-radius: 22px;
}

.legend {
    background: white;
    padding: 12px;
    border-radius: 12px;
}

.item {
    margin: 5px 0;
    font-size: 12px;
}

.box {
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 6px;
    vertical-align: middle;
    border-radius: 4px;
}

</style>

</head>


<body>

<div id="map"></div>


<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>


<script>

const map = L.map("map");

const data = __DATA__;

const colors = __COLORS__;


map.setView(
    [36.2, 127.8],
    7
);


function getColor(n) {

    return colors[n]
        || "#eeeeee";

}


function style(feature) {

    return {

        fillColor:
            getColor(
                feature.properties.등급
            ),

        weight: 1,

        color: "#ffffff",

        fillOpacity: 0.82

    };

}


function onEachFeature(
    feature,
    layer
) {

    const p =
        feature.properties;


    const text =
        "<b>♡ "
        + p.시군구
        + "</b><br>"
        + p.시도
        + "<br>"
        + "고령화율: "
        + Number(
            p.고령화율
        ).toFixed(2)
        + "%";


    layer.bindTooltip(
        text,
        {
            sticky: true
        }
    );


    layer.on({

        mouseover:
            function(e) {

                e.target.setStyle({

                    weight: 3,

                    color: "#a63e68",

                    fillOpacity: 1

                });

            },


        mouseout:
            function(e) {

                e.target.setStyle({

                    weight: 1,

                    color: "#ffffff",

                    fillOpacity: 0.82

                });

            }

    });

}


const layer =
    L.geoJSON(
        data,
        {
            style: style,
            onEachFeature:
                onEachFeature
        }
    ).addTo(map);


if (
    layer
    .getBounds()
    .isValid()
) {

    map.fitBounds(
        layer.getBounds(),
        {
            padding: [
                10,
                10
            ]
        }
    );

}


const legend =
    L.control({
        position:
            "bottomright"
    });


legend.onAdd =
    function() {

        const div =
            L.DomUtil.create(
                "div",
                "legend"
            );


        const labels = [

            "19% 미만",

            "19% 이상 ~ 23% 미만",

            "23% 이상 ~ 28% 미만",

            "28% 이상 ~ 38% 미만",

            "38% 이상"

        ];


        div.innerHTML =
            "<b>고령화율</b>";


        for (
            let i = 0;
            i < colors.length;
            i++
        ) {

            div.innerHTML +=

                '<div class="item">'
                + '<span class="box" '
                + 'style="background:'
                + colors[i]
                + '"></span>'
                + labels[i]
                + '</div>';

        }


        return div;

    };


legend.addTo(map);

</script>

</body>

</html>
"""


map_html = map_html.replace(
    "__DATA__",
    geojson_text
)

map_html = map_html.replace(
    "__COLORS__",
    colors_text
)


# =========================================================
# 15. 지도 표시
# =========================================================

st.markdown(
    '<div class="section-title">🗺️ 시군구별 고령화율 지도</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="info-box">'
    '<div class="info-title">♡ '
    + str(latest_year)
    + '년 기준</div>'
    '<div class="info-text">'
    '각 시군구의 전체 인구 중 '
    '<b>65세 이상 인구가 차지하는 비율</b>을 '
    '색으로 나타낸 지도입니다.<br>'
    '지도 위 지역에 마우스를 올리면 '
    '상세 정보를 볼 수 있어요.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


components.html(
    map_html,
    height=680,
    scrolling=False
)


# =========================================================
# 16. 전체 현황
# =========================================================

st.markdown(
    '<div class="section-title">📊 전체 현황</div>',
    unsafe_allow_html=True
)


metrics = [

    (
        "지도에 표시된 시군구",
        str(len(features)) + "개"
    ),

    (
        "분석 가능한 시군구",
        str(len(grouped)) + "개"
    ),

    (
        "가장 높은 고령화율",
        f"{grouped['고령화율'].max():.2f}%"
    ),

    (
        "가장 낮은 고령화율",
        f"{grouped['고령화율'].min():.2f}%"
    )

]


cols = st.columns(4)


for i in range(4):

    with cols[i]:

        st.markdown(
            '<div class="metric-box">'
            '<div class="metric-title">'
            + metrics[i][0]
            + '</div>'
            '<div class="metric-value">'
            + metrics[i][1]
            + '</div>'
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# 17. 인구 피라미드
# =========================================================

st.markdown(
    '<div class="section-title">📈 지역별 인구 피라미드</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="info-box">'
    '<div class="info-title">♡ 연령별·성별 인구 구조</div>'
    '<div class="info-text">'
    '지역을 선택하면 남성과 여성의 연령대별 인구를 '
    '비교할 수 있습니다.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 18. 지역 선택
# =========================================================

region_options = [
    "전국"
]

region_code = {}


region_list = (
    grouped[
        [
            "시군구코드",
            "시군구",
            "시도"
        ]
    ]
    .drop_duplicates()
    .sort_values(
        [
            "시도",
            "시군구"
        ]
    )
)


for _, row in region_list.iterrows():

    label = (
        str(row["시도"])
        + " | "
        + str(row["시군구"])
    )

    region_options.append(
        label
    )

    region_code[label] = (
        str(
            row["시군구코드"]
        ).zfill(5)
    )


selected = st.selectbox(
    "지역 선택",
    region_options
)


if selected == "전국":

    source = data.copy()

else:

    source = data[
        data["시군구코드"]
        == region_code[selected]
    ].copy()


# =========================================================
# 19. 연령대 계산 함수
# =========================================================

def age_sum(
    source_df,
    gender,
    ages
):

    columns = []


    for age in ages:

        if age == 100:

            name = (
                gender
                + "_100세 이상"
            )

        else:

            name = (
                gender
                + "_"
                + str(age)
                + "세"
            )


        if name in source_df.columns:

            columns.append(
                name
            )


    if not columns:

        return 0


    values = (
        source_df[columns]
        .apply(
            pd.to_numeric,
            errors="coerce"
        )
        .fillna(0)
    )


    return int(
        values.sum().sum()
    )


# =========================================================
# 20. 연령대 설정
# =========================================================

age_groups = [

    (
        "0~9세",
        list(range(0, 10))
    ),

    (
        "10~19세",
        list(range(10, 20))
    ),

    (
        "20~29세",
        list(range(20, 30))
    ),

    (
        "30~39세",
        list(range(30, 40))
    ),

    (
        "40~49세",
        list(range(40, 50))
    ),

    (
        "50~59세",
        list(range(50, 60))
    ),

    (
        "60~69세",
        list(range(60, 70))
    ),

    (
        "70~79세",
        list(range(70, 80))
    ),

    (
        "80세 이상",
        list(range(80, 101))
    )

]


pyramid = []


for label, ages in age_groups:

    male = age_sum(
        source,
        "남",
        ages
    )

    female = age_sum(
        source,
        "여",
        ages
    )

    pyramid.append(
        (
            label,
            male,
            female
        )
    )


maximum = max(
    [
        max(
            item[1],
            item[2]
        )
        for item in pyramid
    ]
    + [1]
)


# =========================================================
# 21. 인구 피라미드 표시
# =========================================================

html = """
<div class="pyramid-box">

<div class="pyramid-row">

<div class="pyramid-label">
남성
</div>

<div class="pyramid-label">
연령
</div>

<div class="pyramid-label">
여성
</div>

</div>
"""


for (
    label,
    male,
    female
) in pyramid:

    male_width = (
        male
        / maximum
        * 100
    )

    female_width = (
        female
        / maximum
        * 100
    )


    html += (

        '<div class="pyramid-row">'

        '<div class="left-side">'

        '<span class="pyramid-number">'
        + f"{male:,}"
        + '명</span>'

        '<div class="male-bar" '
        'style="width:'
        + f"{male_width:.1f}"
        + '%"></div>'

        '</div>'

        '<div class="pyramid-label">'
        + label
        + '</div>'

        '<div class="right-side">'

        '<div class="female-bar" '
        'style="width:'
        + f"{female_width:.1f}"
        + '%"></div>'

        '<span class="pyramid-number">'
        + f"{female:,}"
        + '명</span>'

        '</div>'

        '</div>'

    )


html += """

<div style="
text-align:center;
color:#a27d8d;
font-size:12px;
margin-top:15px;
">

막대가 길수록 해당 연령대의 인구가 많습니다.

</div>

</div>
"""


st.markdown(
    html,
    unsafe_allow_html=True
)


# =========================================================
# 22. 선택 지역 통계
# =========================================================

total = int(
    source[
        "전체인구"
    ].sum()
)


elderly = int(
    source[
        "고령인구"
    ].sum()
)


working_cols = []


for age in range(15, 65):

    c = (
        "계_"
        + str(age)
        + "세"
    )

    if c in source.columns:

        working_cols.append(c)


if working_cols:

    working = int(
        source[
            working_cols
        ]
        .apply(
            pd.to_numeric,
            errors="coerce"
        )
        .fillna(0)
        .sum()
        .sum()
    )

else:

    working = 0


if total > 0:

    aging_rate = (
        elderly
        / total
        * 100
    )

else:

    aging_rate = 0


if working > 0:

    dependency = (
        elderly
        / working
        * 100
    )

else:

    dependency = 0


cols = st.columns(3)


values = [

    (
        "선택 지역 총인구",
        f"{total:,}명"
    ),

    (
        "고령화율",
        f"{aging_rate:.2f}%"
    ),

    (
        "노년부양비",
        f"{dependency:.2f}"
    )

]


for i in range(3):

    with cols[i]:

        st.markdown(
            '<div class="metric-box">'
            '<div class="metric-title">'
            + values[i][0]
            + '</div>'
            '<div class="metric-value">'
            + values[i][1]
            + '</div>'
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# 23. 지역별 비교표
# =========================================================

st.markdown(
    '<div class="section-title">🔎 지역별 고령화율 비교</div>',
    unsafe_allow_html=True
)


top10 = (
    grouped
    .sort_values(
        "고령화율",
        ascending=False
    )
    .head(10)
    .copy()
)


bottom10 = (
    grouped
    .sort_values(
        "고령화율",
        ascending=True
    )
    .head(10)
    .copy()
)


def make_table(df):

    result = df[
        [
            "시도",
            "시군구",
            "전체인구",
            "고령인구",
            "고령화율"
        ]
    ].copy()


    result.columns = [

        "시도",

        "시군구",

        "전체 인구",

        "65세 이상 인구",

        "고령화율(%)"

    ]


    result[
        "고령화율(%)"
    ] = result[
        "고령화율(%)"
    ].round(2)


    return result


left, right = st.columns(2)


with left:

    st.markdown(
        '<div class="table-title">'
        '♡ 고령화율이 높은 지역 TOP 10'
        '</div>',
        unsafe_allow_html=True
    )


    st.dataframe(
        make_table(top10),
        use_container_width=True,
        hide_index=True
    )


with right:

    st.markdown(
        '<div class="table-title">'
        '♡ 고령화율이 낮은 지역 TOP 10'
        '</div>',
        unsafe_allow_html=True
    )


    st.dataframe(
        make_table(bottom10),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 24. 계산 방법
# =========================================================

st.markdown(
    '<div class="formula">'
    '<b>♡ 계산 방법</b>'
    '<br><br>'
    '고령화율 = 65세 이상 인구 ÷ 전체 인구 × 100'
    '<br><br>'
    '노년부양비 = 65세 이상 인구 ÷ 15~64세 인구 × 100'
    '<br><br>'
    '<span style="font-size:13px;">'
    '읍·면·동 단위 인구를 시군구 코드 기준으로 합산했습니다.'
    '</span>'
    '</div>',
    unsafe_allow_html=True
)
