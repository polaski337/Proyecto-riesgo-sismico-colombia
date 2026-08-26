from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
GEOJSON_DIR = BASE_DIR / "Publicacion_Web" / "GeoJSON"
CSV_DIR = BASE_DIR / "Publicacion_Web" / "CSV_Dashboard"


DEPT_FIXES = {
    "ATL�NTICO": "ATLÁNTICO",
    "BOGOT�, D.C.": "BOGOTÁ, D.C.",
    "BOL�VAR": "BOLÍVAR",
    "BOYAC�": "BOYACÁ",
    "CAQUET�": "CAQUETÁ",
    "CHOC�": "CHOCÓ",
    "C�RDOBA": "CÓRDOBA",
    "GUAIN�A": "GUAINÍA",
    "NARI�O": "NARIÑO",
    "QUIND�O": "QUINDÍO",
    "SAN ANDR�S": "SAN ANDRÉS",
    "VAUP�S": "VAUPÉS",
}

MAG_ORDER = ["3.0 - 3.9", "4.0 - 4.9", "5.0 - 5.9", "6.0 - 6.9", ">= 7.0"]
THREAT_ORDER = ["Alta", "Intermedia", "Baja", "Sin dato"]
THREAT_COLORS = {
    "Alta": [196, 60, 57, 118],
    "Intermedia": [230, 162, 60, 105],
    "Baja": [115, 169, 66, 100],
    "Sin dato": [184, 184, 184, 90],
}


st.set_page_config(
    page_title="Riesgo y exposición sísmica en Colombia",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_geojson(name: str) -> dict:
    with (GEOJSON_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(CSV_DIR / name)


def fix_text(value):
    if pd.isna(value):
        return value
    return DEPT_FIXES.get(str(value), str(value))


def features_to_points(data: dict) -> pd.DataFrame:
    rows = []
    for feature in data["features"]:
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or [None, None]
        props = feature.get("properties") or {}
        if geometry.get("type") == "Point" and coords[0] is not None and coords[1] is not None:
            row = props.copy()
            row["lon"] = coords[0]
            row["lat"] = coords[1]
            rows.append(row)
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_dashboard_data():
    sismos = features_to_points(load_geojson("web_sismos.geojson"))
    sismos["anio"] = pd.to_numeric(sismos["anio"], errors="coerce").astype("Int64")
    sismos["magnitud"] = pd.to_numeric(sismos["magnitud"], errors="coerce")
    sismos["profundidad_km"] = pd.to_numeric(sismos["profundidad_km"], errors="coerce")
    sismos["depto_codigo"] = sismos["depto_codigo"].astype(str).str.zfill(2)

    deptos = load_csv("f4_eventos_por_departamento.csv")
    deptos["depto_codigo"] = deptos["depto_codigo_1"].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    deptos["depto_nombre"] = deptos["depto_nombre"].map(fix_text)

    depto_lookup = deptos[["depto_codigo", "depto_nombre"]].drop_duplicates()
    sismos = sismos.merge(depto_lookup, on="depto_codigo", how="left")
    sismos["depto_nombre"] = sismos["depto_nombre"].fillna("Sin departamento asignado")

    anio = load_csv("f4_eventos_por_anio.csv")
    magnitud = load_csv("f4_eventos_por_magnitud_clase.csv")
    amenaza = load_csv("f4_municipios_por_nivel_amenaza.csv")
    ips = load_csv("f4_ips_por_amenaza_depto.csv")
    sedes = load_csv("f4_sedes_educativas_por_amenaza_depto.csv")
    red = load_csv("f4_red_vial_km_por_amenaza_depto.csv")
    kpis = load_csv("dashboard_kpis_fase7.csv")

    for frame in [ips, sedes, red]:
        if "depto_nombre" in frame:
            frame["depto_nombre"] = frame["depto_nombre"].map(fix_text)
        if "amenaza_cat" in frame:
            frame["amenaza_cat"] = frame["amenaza_cat"].fillna("Sin dato")

    return sismos, deptos, anio, magnitud, amenaza, ips, sedes, red, kpis


def filter_geojson_by_threat(data: dict, threats: list[str]) -> dict:
    allowed = set(threats)
    features = [
        feature
        for feature in data["features"]
        if (feature.get("properties") or {}).get("amenaza_cat", "Sin dato") in allowed
    ]
    return {"type": "FeatureCollection", "features": features}


def threat_color_expression():
    return [
        "match",
        ["get", "amenaza_cat"],
        "Alta",
        THREAT_COLORS["Alta"],
        "Intermedia",
        THREAT_COLORS["Intermedia"],
        "Baja",
        THREAT_COLORS["Baja"],
        "Sin dato",
        THREAT_COLORS["Sin dato"],
        [184, 184, 184, 80],
    ]


def quake_color_expression():
    return [
        "case",
        [">=", ["get", "magnitud"], 7],
        [122, 30, 30, 210],
        [">=", ["get", "magnitud"], 6],
        [196, 60, 57, 205],
        [">=", ["get", "magnitud"], 5],
        [230, 118, 46, 190],
        [">=", ["get", "magnitud"], 4],
        [230, 162, 60, 175],
        [107, 114, 128, 150],
    ]


def build_map(municipios_geojson: dict, sismos_df: pd.DataFrame, show_points: bool):
    layers = [
        pdk.Layer(
            "GeoJsonLayer",
            municipios_geojson,
            stroked=True,
            filled=True,
            get_fill_color=threat_color_expression(),
            get_line_color=[76, 86, 96, 90],
            line_width_min_pixels=0.4,
            pickable=True,
            auto_highlight=True,
        )
    ]

    if show_points and not sismos_df.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                sismos_df,
                get_position="[lon, lat]",
                get_radius="magnitud * 2100",
                radius_min_pixels=2,
                radius_max_pixels=18,
                get_fill_color=quake_color_expression(),
                get_line_color=[255, 255, 255, 180],
                line_width_min_pixels=0.5,
                pickable=True,
                auto_highlight=True,
            )
        )

    return pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=4.6, longitude=-73.2, zoom=4.25, pitch=0),
        layers=layers,
        tooltip={
            "html": "<b>{mpio_nombre}{depto_nombre}</b><br/>Amenaza: {amenaza_cat}<br/>PGA475: {pga475}<br/>Evento: {evento_id}<br/>Magnitud: {magnitud}",
            "style": {"fontFamily": "Arial", "fontSize": "12px"},
        },
    )


def metric_card(label: str, value: str, help_text: str | None = None):
    st.metric(label, value, help=help_text)


def main():
    sismos, deptos, anio, magnitud, amenaza, ips, sedes, red, kpis = load_dashboard_data()
    municipios_geojson = load_geojson("web_municipios_amenaza.geojson")

    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 1rem;}
        [data-testid="stMetric"] {
            background: #171C26;
            border: 1px solid #334155;
            padding: 12px 14px;
            min-height: 86px;
        }
        [data-testid="stMetricLabel"] {
            color: #DDE6F3;
            font-weight: 600;
        }
        [data-testid="stMetricValue"] {
            color: #FFFFFF;
            font-weight: 700;
        }
        [data-testid="stMetricDelta"] {
            color: #CBD5E1;
        }
        h1, h2, h3 {letter-spacing: 0;}
        .small-note {
            color: #F1F5F9;
            font-size: 0.98rem;
            font-weight: 500;
            margin-top: -0.4rem;
            margin-bottom: 0.35rem;
        }
        .method-note {
            background: #171C26;
            border-left: 4px solid #C43C39;
            padding: 0.75rem 1rem;
            color: #E5E7EB;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Análisis espacial del riesgo y la exposición sísmica en Colombia")
    st.markdown(
        "<div class='small-note'>Amenaza sísmica, sismicidad histórica e infraestructura potencialmente expuesta · Catálogo descargado 1610-2020</div>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Filtros")
        years = sorted([int(x) for x in sismos["anio"].dropna().unique()])
        year_range = st.slider("Año", min_value=min(years), max_value=max(years), value=(min(years), max(years)))

        departments = sorted([d for d in deptos["depto_nombre"].dropna().unique()])
        selected_departments = st.multiselect("Departamento", departments, default=departments)

        selected_mags = st.multiselect("Rango de magnitud", MAG_ORDER, default=MAG_ORDER)
        selected_threats = st.multiselect("Nivel de amenaza", THREAT_ORDER, default=THREAT_ORDER)
        show_points = st.toggle("Mostrar sismos en el mapa", value=True)

        st.divider()
        st.caption("Los filtros se aplican al análisis del dashboard. Los eventos sin departamento asignado se conservan para transparencia metodológica.")

    filtered = sismos[
        (sismos["anio"].between(year_range[0], year_range[1]))
        & (sismos["depto_nombre"].isin(selected_departments + ["Sin departamento asignado"]))
        & (sismos["magnitud_clase"].isin(selected_mags))
    ].copy()
    filtered_map_points = filtered[filtered["depto_nombre"] != "Sin departamento asignado"].copy()

    municipios_filtered = filter_geojson_by_threat(municipios_geojson, selected_threats)
    deptos_filtered = deptos[deptos["depto_nombre"].isin(selected_departments)].copy()

    max_mag = filtered["magnitud"].max()
    max_mag_text = "Sin dato" if pd.isna(max_mag) else f"{max_mag:.2f}"
    dept_count = filtered.loc[filtered["depto_nombre"] != "Sin departamento asignado", "depto_nombre"].nunique()
    high_threat_mpios = int(amenaza.loc[amenaza["amenaza_cat"] == "Alta", "COUNT_mpio_dane"].sum())
    ips_high = int(ips.loc[ips["amenaza_cat"] == "Alta", "COUNT_codigo_habilitacion"].sum())
    sedes_high = int(sedes.loc[sedes["amenaza_cat"] == "Alta", "COUNT_cod_dane"].sum())

    kpi_cols = st.columns(6)
    with kpi_cols[0]:
        metric_card("Eventos filtrados", f"{len(filtered):,}".replace(",", "."))
    with kpi_cols[1]:
        metric_card("Magnitud máxima", max_mag_text)
    with kpi_cols[2]:
        metric_card("Departamentos", f"{dept_count}")
    with kpi_cols[3]:
        metric_card("Municipios amenaza alta", f"{high_threat_mpios:,}".replace(",", "."))
    with kpi_cols[4]:
        metric_card("IPS amenaza alta", f"{ips_high:,}".replace(",", "."))
    with kpi_cols[5]:
        metric_card("Sedes amenaza alta", f"{sedes_high:,}".replace(",", "."))

    map_col, side_col = st.columns([1.65, 1], gap="large")
    with map_col:
        st.subheader("Mapa interactivo")
        st.pydeck_chart(build_map(municipios_filtered, filtered_map_points, show_points), use_container_width=True)

    with side_col:
        st.subheader("Eventos por año")
        yearly = filtered.dropna(subset=["anio"]).groupby("anio", as_index=False).agg(eventos=("evento_id", "count"))
        fig_year = px.line(yearly, x="anio", y="eventos", markers=False, color_discrete_sequence=["#C43C39"])
        fig_year.update_layout(height=245, margin=dict(l=8, r=8, t=8, b=8), xaxis_title="", yaxis_title="Eventos")
        st.plotly_chart(fig_year, use_container_width=True)

        st.subheader("Top departamentos")
        top_dept = (
            filtered[filtered["depto_nombre"] != "Sin departamento asignado"]
            .groupby("depto_nombre", as_index=False)
            .agg(eventos=("evento_id", "count"), magnitud_max=("magnitud", "max"))
            .sort_values("eventos", ascending=False)
            .head(10)
        )
        fig_top = px.bar(top_dept, x="eventos", y="depto_nombre", orientation="h", color_discrete_sequence=["#174A63"])
        fig_top.update_layout(height=310, margin=dict(l=8, r=8, t=8, b=8), xaxis_title="Eventos", yaxis_title="", yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top, use_container_width=True)

    bottom_left, bottom_mid, bottom_right = st.columns([1, 1, 1], gap="large")
    with bottom_left:
        st.subheader("Distribución por magnitud")
        mag_df = filtered.groupby("magnitud_clase", as_index=False).agg(eventos=("evento_id", "count"))
        mag_df["magnitud_clase"] = pd.Categorical(mag_df["magnitud_clase"], categories=MAG_ORDER, ordered=True)
        mag_df = mag_df.sort_values("magnitud_clase")
        fig_mag = px.bar(mag_df, x="magnitud_clase", y="eventos", color="magnitud_clase", color_discrete_sequence=["#6B7280", "#E6A23C", "#E6762E", "#C43C39", "#7A1E1E"])
        fig_mag.update_layout(height=290, showlegend=False, margin=dict(l=8, r=8, t=8, b=8), xaxis_title="", yaxis_title="Eventos")
        st.plotly_chart(fig_mag, use_container_width=True)

    with bottom_mid:
        st.subheader("Municipios por amenaza")
        threat_df = amenaza.copy()
        threat_df["amenaza_cat"] = pd.Categorical(threat_df["amenaza_cat"], categories=THREAT_ORDER, ordered=True)
        threat_df = threat_df.sort_values("amenaza_cat")
        fig_threat = px.bar(
            threat_df,
            x="amenaza_cat",
            y="COUNT_mpio_dane",
            color="amenaza_cat",
            color_discrete_map={"Alta": "#C43C39", "Intermedia": "#E6A23C", "Baja": "#73A942", "Sin dato": "#B8B8B8"},
        )
        fig_threat.update_layout(height=290, showlegend=False, margin=dict(l=8, r=8, t=8, b=8), xaxis_title="", yaxis_title="Municipios")
        st.plotly_chart(fig_threat, use_container_width=True)

    with bottom_right:
        st.subheader("Infraestructura en amenaza alta")
        infra_rows = []
        for _, row in ips[ips["amenaza_cat"].eq("Alta")].iterrows():
            infra_rows.append({"departamento": row["depto_nombre"], "tipo": "IPS", "valor": row["COUNT_codigo_habilitacion"]})
        for _, row in sedes[sedes["amenaza_cat"].eq("Alta")].iterrows():
            infra_rows.append({"departamento": row["depto_nombre"], "tipo": "Sedes educativas", "valor": row["COUNT_cod_dane"]})
        infra = pd.DataFrame(infra_rows)
        infra = infra[infra["departamento"].isin(selected_departments)]
        infra_top = infra.groupby(["departamento", "tipo"], as_index=False)["valor"].sum().sort_values("valor", ascending=False).head(12)
        fig_infra = px.bar(infra_top, x="valor", y="departamento", color="tipo", orientation="h", color_discrete_map={"IPS": "#1D4ED8", "Sedes educativas": "#7C3AED"})
        fig_infra.update_layout(height=290, margin=dict(l=8, r=8, t=8, b=8), xaxis_title="Elementos", yaxis_title="", yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_infra, use_container_width=True)

    st.subheader("Ranking territorial")
    ranking = deptos_filtered[["depto_nombre", "COUNT_evento_id", "MAX_magnitud", "MEAN_magnitud", "MEAN_profundidad_km"]].copy()
    ranking = ranking.rename(
        columns={
            "depto_nombre": "Departamento",
            "COUNT_evento_id": "Eventos",
            "MAX_magnitud": "Magnitud máxima",
            "MEAN_magnitud": "Magnitud media",
            "MEAN_profundidad_km": "Profundidad media km",
        }
    ).sort_values("Eventos", ascending=False)
    st.dataframe(ranking, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="method-note">
        <strong>Nota metodológica.</strong> El dashboard representa amenaza y exposición potencial. No estima vulnerabilidad estructural, pérdidas ni riesgo sísmico oficial. Los sismos fuera de límites departamentales DANE se conservan como no asignados y no se redistribuyen manualmente.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
