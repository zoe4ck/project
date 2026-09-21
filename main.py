# main.py

import io
import json
import requests
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# 1. 페이지 기본 설정
# ============================================================

st.set_page_config(
    page_title="전국 고령화 지도",
    page_icon="🇰🇷",
    layout="wide"
)

st.title("🇰🇷 전국 고령화 지도")
st.caption("시군구별 65세 이상 인구 비율을 나타낸 단계구분도")


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
def load_population():
    """전국 읍·면·동 인구 데이터를 불러옵니다."""

    response = requests.get(POPULATION_URL, timeout=60)
    response.raise_for_status()

    # gzip으로 압축된 CSV 파일을 읽습니다.
    df = pd.read_csv(
        io.BytesIO(response.content),
        compression="gzip",
        dtype={"코드": "string"}
    )

    return df


@st.cache_data
def load_geojson():
    """전국 시군구 경계 GeoJSON을 불러옵니다."""

    response = requests.get(GEOJSON_URL, timeout=60)
    response.raise_for_status()

    return response.json()


# ============================================================
# 4. 시군구별 고령화율 계산
# ============================================================

@st.cache_data
def calculate_aging_rate(df):
    """
    읍·면·동 인구를 시군구 단위로 합친 뒤
    65세 이상 인구 비율을 계산합니다.
    """

    data = df.copy()

    # --------------------------------------------------------
    # 행정동 코드는 계산할 숫자가 아니라 '이름표'입니다.
    # 따라서 반드시 문자열로 처리합니다.
    # --------------------------------------------------------
    data["코드"] = (
        data["코드"]
        .astype("string")
        .str.strip()
    )

    # 행정동 코드 앞 5자리가 시군구 코드입니다.
    data["시군구코드"] = data["코드"].str[:5]

    # --------------------------------------------------------
    # 연도를 숫자로 바꾼 뒤 가장 최신 연도만 사용합니다.
    # --------------------------------------------------------
    data["연도_숫자"] = pd.to_numeric(
        data["연도"],
        errors="coerce"
    )

    latest_year = int(data["연도_숫자"].max())

    data = data[
        data["연도_숫자"] == latest_year
    ].copy()

    # --------------------------------------------------------
    # '계_'로 시작하는 열은 남녀 합계 인구입니다.
    # --------------------------------------------------------
    total_columns = [
        col
        for col in data.columns
        if str(col).startswith("계_")
    ]

    if len(total_columns) == 0:
        raise ValueError(
            "'계_0세'와 같은 나이별 인구 열을 찾지 못했습니다."
        )

    # --------------------------------------------------------
    # 65세 이상 열 찾기
    # --------------------------------------------------------

    elderly_columns = []

    for age in range(65, 100):
        col = f"계_{age}세"

        if col in data.columns:
            elderly_columns.append(col)

    if "계_100세 이상" in data.columns:
        elderly_columns.append("계_100세 이상")

    if len(elderly_columns) == 0:
        raise ValueError(
            "65세 이상 인구 열을 찾지 못했습니다."
        )

    # --------------------------------------------------------
    # 각 읍·면·동의 전체 인구
    # --------------------------------------------------------

    for col in total_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        ).fillna(0)

    data["전체인구"] = data[total_columns].sum(axis=1)

    # --------------------------------------------------------
    # 각 읍·면·동의 65세 이상 인구
    # --------------------------------------------------------

    for col in elderly_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        ).fillna(0)

    data["65세이상인구"] = data[elderly_columns].sum(axis=1)

    # --------------------------------------------------------
    # 시군구별로 여러 읍·면·동을 합칩니다.
    #
    # 중요한 점:
    # 이름이 아니라 '시군구코드'를 기준으로 합칩니다.
    # --------------------------------------------------------

    population_by_code = (
        data.groupby("시군구코드", as_index=False)[
            ["전체인구", "65세이상인구"]
        ]
        .sum()
    )

    # 시군구 코드별 이름과 시도를 가져옵니다.
    info = (
        data[
            ["시군구코드", "시군구", "시도"]
        ]
        .drop_duplicates("시군구코드")
    )

    population_by_code = population_by_code.merge(
        info,
        on="시군구코드",
        how="left"
    )

    # --------------------------------------------------------
    # 고령화율 계산
    #
    # 고령화율 =
    # 65세 이상 인구 / 전체 인구 × 100
    # --------------------------------------------------------

    population_by_code["고령화율"] = np.where(
        population_by_code["전체인구"] > 0,
        population_by_code["65세이상인구"]
        / population_by_code["전체인구"] * 100,
        np.nan
    )

    population_by_code["연도"] = latest_year

    return population_by_code


# ============================================================
# 5. 색상 단계
# ============================================================

COLORS = [
    "#EAF4F8",  # 19% 미만
    "#C5DFE9",  # 19~23%
    "#8FC0D0",  # 23~28%
    "#5597AE",  # 28~38%
    "#24617C",  # 38% 이상
]

LABELS = [
    "19% 미만",
    "19% 이상 ~ 23% 미만",
    "23% 이상 ~ 28% 미만",
    "28% 이상 ~ 38% 미만",
    "38% 이상",
]


def get_grade(rate):
    """고령화율을 5개 단계 중 하나로 분류합니다."""

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
# 6. 지도용 GeoJSON 만들기
# ============================================================

def make_map_geojson(geojson, population):
    """
    GeoJSON의 각 시군구에 고령화율 정보를 붙입니다.

    연결 기준은 반드시 5자리 시군구 코드입니다.
    """

    # 코드 -> 정보 형태로 사전을 만듭니다.
    data_dict = {}

    for _, row in population.iterrows():

        code = str(row["시군구코드"]).strip().zfill(5)

        data_dict[code] = {
            "시군구": str(row["시군구"]),
            "시도": str(row["시도"]),
            "고령화율": (
                None
                if pd.isna(row["고령화율"])
                else float(row["고령화율"])
            )
        }

    # 원본을 직접 수정하지 않도록 복사합니다.
    result = json.loads(json.dumps(geojson, ensure_ascii=False))

    for feature in result.get("features", []):

        properties = feature.get("properties", {})

        # GeoJSON의 코드도 문자열로 처리합니다.
        code = str(
            properties.get("코드", "")
        ).strip().zfill(5)

        info = data_dict.get(code)

        if info is not None:

            properties["시군구"] = info["시군구"]
            properties["시도"] = info["시도"]
            properties["고령화율"] = info["고령화율"]

            properties["등급"] = get_grade(
                info["고령화율"]
            )

        else:

            # 인구 데이터와 연결되지 않은 지역
            properties["고령화율"] = None
            properties["등급"] = None

    return result


# ============================================================
# 7. Leaflet 지도 HTML 만들기
# ============================================================

def create_map_html(map_geojson):

    geojson_text = json.dumps(
        map_geojson,
        ensure_ascii=False
    )

    colors_text = json.dumps(
        COLORS,
        ensure_ascii=False
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
      content="width=device-width, initial-scale=1.0">

<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
</script>

<style>

    html, body {{
        margin: 0;
        padding: 0;
        background: white;
    }}

    #map {{
        width: 100%;
        height: 700px;
        background: white;
    }}

    .legend {{
        background: white;
        padding: 12px 14px;
        border-radius: 8px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.2);
        line-height: 22px;
        font-family:
            Arial,
            "Malgun Gothic",
            "Apple SD Gothic Neo",
            sans-serif;
        font-size: 13px;
    }}

    .legend-title {{
        font-weight: bold;
        margin-bottom: 6px;
    }}

    .legend-item {{
        display: flex;
        align-items: center;
        margin: 2px 0;
        white-space: nowrap;
    }}

    .legend-color {{
        width: 18px;
        height: 18px;
        margin-right: 7px;
        border: 1px solid #cccccc;
        box-sizing: border-box;
    }}

    .leaflet-tooltip {{
        font-family:
            Arial,
            "Malgun Gothic",
            "Apple SD Gothic Neo",
            sans-serif;
        font-size: 13px;
        line-height: 1.6;
    }}

</style>

</head>


<body>

<div id="map"></div>


<script>

    // --------------------------------------------------------
    // Python에서 넘겨받은 지도 데이터
    // --------------------------------------------------------

    const mapData = {geojson_text};

    const colors = {colors_text};

    const labels = {labels_text};


    // --------------------------------------------------------
    // 대한민국 지도 만들기
    //
    // 타일을 추가하지 않기 때문에
    // 실제 지도 배경은 나오지 않고 행정구역 경계만 나옵니다.
    // --------------------------------------------------------

    const map = L.map("map", {{
        zoomControl: true,
        attributionControl: false
    }});


    // --------------------------------------------------------
    // 고령화율에 따라 색을 정하는 함수
    // --------------------------------------------------------

    function getColor(grade) {{

        if (
            grade === null ||
            grade === undefined ||
            grade === ""
        ) {{
            return "#EEEEEE";
        }}

        return colors[Number(grade)];
    }}


    // --------------------------------------------------------
    // 마우스를 올렸을 때 지역이 조금 진해지도록 합니다.
    // --------------------------------------------------------

    function highlightFeature(e) {{

        const layer = e.target;

        layer.setStyle({{
            weight: 2,
            color: "#333333",
            fillOpacity: 0.9
        }});

        layer.bringToFront();
    }}


    // --------------------------------------------------------
    // 마우스가 지역 밖으로 나가면 원래 모습으로 돌아갑니다.
    // --------------------------------------------------------

    function resetHighlight(e) {{

        geojsonLayer.resetStyle(e.target);
    }}


    // --------------------------------------------------------
    // 각 지역에 마우스오버 정보를 연결합니다.
    // --------------------------------------------------------

    function onEachFeature(feature, layer) {{

        const p = feature.properties || {{}};

        const sigungu =
            p["시군구"] || "정보 없음";

        const sido =
            p["시도"] || "정보 없음";

        const rate =
            p["고령화율"];


        let rateText = "자료 없음";

        if (
            rate !== null &&
            rate !== undefined &&
            !isNaN(rate)
        ) {{
            rateText =
                Number(rate).toFixed(2) + "%";
        }}


        layer.bindTooltip(
            "<b>" + sigungu + "</b>" +
            "<br>시도: " + sido +
            "<br>고령화율: " + rateText,
            {{
                sticky: true,
                direction: "top"
            }}
        );


        layer.on({{
            mouseover: highlightFeature,
            mouseout: resetHighlight
        }});
    }}


    // --------------------------------------------------------
    // GeoJSON을 지도에 올립니다.
    // --------------------------------------------------------

    const geojsonLayer = L.geoJSON(
        mapData,
        {{
            style: function(feature) {{

                const grade =
                    feature.properties["등급"];

                return {{
                    fillColor: getColor(grade),
                    weight: 0.7,
                    color: "#FFFFFF",
                    fillOpacity: 0.9
                }};
            }},

            onEachFeature: onEachFeature
        }}
    ).addTo(map);


    // --------------------------------------------------------
    // 우리나라 전체가 화면 안에 들어오도록 자동 확대합니다.
    // --------------------------------------------------------

    const bounds = geojsonLayer.getBounds();

    if (bounds.isValid()) {{
        map.fitBounds(
            bounds,
            {{
                padding: [10, 10]
            }}
        );
    }}


    // --------------------------------------------------------
    // 범례
    // --------------------------------------------------------

    const legend = L.control({{
        position: "bottomright"
    }});


    legend.onAdd = function() {{

        const div =
            L.DomUtil.create(
                "div",
                "legend"
            );

        let html =
            '<div class="legend-title">' +
            '고령화율' +
            '</div>';


        for (let i = 0; i < labels.length; i++) {{

            html +=
                '<div class="legend-item">' +
                '<span class="legend-color" ' +
                'style="background:' +
                colors[i] +
                '"></span>' +
                labels[i] +
                '</div>';
        }}


        // 자료가 연결되지 않은 지역 표시
        html +=
            '<div class="legend-item">' +
            '<span class="legend-color" ' +
            'style="background:#EEEEEE"></span>' +
            '자료 없음' +
            '</div>';


        div.innerHTML = html;

        return div;
    }};


    legend.addTo(map);

</script>

</body>
</html>
"""

    return html


# ============================================================
# 8. 실제 실행
# ============================================================

try:

    with st.spinner(
        "전국 인구 및 시군구 경계 데이터를 불러오는 중입니다..."
    ):

        population_df = load_population()

        geojson = load_geojson()

        sigungu_df = calculate_aging_rate(
            population_df
        )

        map_geojson = make_map_geojson(
            geojson,
            sigungu_df
        )

except Exception as e:

    st.error("데이터를 불러오거나 계산하는 과정에서 오류가 발생했습니다.")

    st.code(
        f"{type(e).__name__}: {e}"
    )

    st.stop()


# ============================================================
# 9. 최신 연도 표시
# ============================================================

latest_year = int(
    sigungu_df["연도"].iloc[0]
)

st.info(
    f"📅 현재 표시된 자료: {latest_year}년"
)


# ============================================================
# 10. 연결된 시군구 개수 확인
# ============================================================

total_regions = len(geojson.get("features", []))

valid_regions = sigungu_df[
    sigungu_df["고령화율"].notna()
].shape[0]


col_a, col_b = st.columns(2)

with col_a:
    st.metric(
        "지도 경계 시군구",
        f"{total_regions}개"
    )

with col_b:
    st.metric(
        "인구 데이터가 연결된 시군구",
        f"{valid_regions}개"
    )


# ============================================================
# 11. 지도 표시
# ============================================================

st.subheader("🗺️ 시군구별 고령화율")

map_html = create_map_html(
    map_geojson
)

components.html(
    map_html,
    height=720,
    scrolling=False
)


# ============================================================
# 12. 고령화율 상·하위 지역 계산
# ============================================================

ranking = sigungu_df[
    sigungu_df["고령화율"].notna()
].copy()


# ------------------------------------------------------------
# 고령화율이 높은 지역 10개
# ------------------------------------------------------------

top10 = (
    ranking
    .sort_values(
        "고령화율",
        ascending=False
    )
    .head(10)
    .copy()
)

top10["순위"] = range(1, len(top10) + 1)

top10["고령화율"] = top10[
    "고령화율"
].map(
    lambda x: f"{x:.2f}%"
)

top10 = top10[
    ["순위", "시도", "시군구", "고령화율"]
]


# ------------------------------------------------------------
# 고령화율이 낮은 지역 10개
# ------------------------------------------------------------

bottom10 = (
    ranking
    .sort_values(
        "고령화율",
        ascending=True
    )
    .head(10)
    .copy()
)

bottom10["순위"] = range(1, len(bottom10) + 1)

bottom10["고령화율"] = bottom10[
    "고령화율"
].map(
    lambda x: f"{x:.2f}%"
)

bottom10 = bottom10[
    ["순위", "시도", "시군구", "고령화율"]
]


# ============================================================
# 13. 두 표를 나란히 표시
# ============================================================

st.subheader("📊 고령화율 상·하위 지역")

left, right = st.columns(2)


with left:

    st.markdown("### 고령화율 높은 곳 10개")

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True
    )


with right:

    st.markdown("### 고령화율 낮은 곳 10개")

    st.dataframe(
        bottom10,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 14. 계산 방법 안내
# ============================================================

st.divider()

st.caption(
    "고령화율 = 65세 이상 인구 ÷ 전체 인구 × 100"
)

st.caption(
    "지도 색상 기준: 19% / 23% / 28% / 38%"
)

st.caption(
    "행정동 코드의 앞 5자리를 시군구 코드로 사용하여 "
    "시군구 경계 데이터와 연결했습니다."
)
