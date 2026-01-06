import streamlit as st
import pandas as pd
import altair as alt

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
st.set_page_config(
    page_title="Dashboard de Reviews",
    layout="wide",
    page_icon="⭐"
)

alt.themes.enable("default")

# =========================
# LOAD DOS DADOS
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("booking-reviews-20102025_final.csv")
    df.columns = df.columns.str.strip()

    for col in ["checkInDate", "checkOutDate", "reviewDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

df = load_data()

# =========================
# TÍTULO
# =========================
st.title("📊 Análise de Reviews de Hospedagens")
st.markdown(
    "Dashboard interativo para análise de avaliações, perfil de viajantes "
    "e comportamento ao longo do tempo."
)

# =========================
# SIDEBAR - FILTROS
# =========================
st.sidebar.header("🔍 Filtros")

municipio_sel = st.sidebar.multiselect(
    "Município",
    sorted(df["municipio"].dropna().unique())
)

traveler_sel = st.sidebar.multiselect(
    "Tipo de Viajante",
    sorted(df["travelerType"].dropna().unique())
)

rating_min, rating_max = st.sidebar.slider(
    "Nota da Avaliação",
    float(df["rating"].min()),
    float(df["rating"].max()),
    (float(df["rating"].min()), float(df["rating"].max()))
)

df_f = df.copy()

if municipio_sel:
    df_f = df_f[df_f["municipio"].isin(municipio_sel)]

if traveler_sel:
    df_f = df_f[df_f["travelerType"].isin(traveler_sel)]

df_f = df_f[df_f["rating"].between(rating_min, rating_max)]

# =========================
# KPIs
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Reviews", len(df_f))
col2.metric("Nota Média", round(df_f["rating"].mean(), 2))
col3.metric("Municípios", df_f["municipio"].nunique())
col4.metric("Tipos de Viajante", df_f["travelerType"].nunique())

# =========================
# GRÁFICOS
# =========================
st.markdown("---")
col1, col2 = st.columns(2)

# ---- Distribuição das Avaliações
with col1:
    st.subheader("⭐ Distribuição das Avaliações")

    hist = (
        alt.Chart(df_f)
        .mark_bar()
        .encode(
            x=alt.X("rating:Q", bin=alt.Bin(maxbins=10), title="Nota"),
            y=alt.Y("count()", title="Quantidade de Reviews"),
            tooltip=["count()"]
        )
        .properties(height=300)
    )

    st.altair_chart(hist, use_container_width=True)

# ---- Volume de Reviews ao Longo do Tempo
with col2:
    st.subheader("📈 Volume de Reviews ao Longo do Tempo")

    reviews_time = (
        df_f.set_index("reviewDate")
            .resample("M")
            .size()
            .reset_index(name="total_reviews")
    )

    line_time = (
        alt.Chart(reviews_time)
        .mark_line(point=True)
        .encode(
            x=alt.X("reviewDate:T", title="Data"),
            y=alt.Y("total_reviews:Q", title="Total de Reviews"),
            tooltip=["reviewDate:T", "total_reviews:Q"]
        )
        .properties(height=300)
    )

    st.altair_chart(line_time, use_container_width=True)

# =========================
# ANÁLISES COMPLEMENTARES
# =========================
st.markdown("---")
col1, col2 = st.columns(2)

# ---- Nota média por tipo de viajante
with col1:
    st.subheader("🧍 Nota Média por Tipo de Viajante")

    rating_traveler = (
        df_f.groupby("travelerType", as_index=False)["rating"]
            .mean()
            .sort_values("rating", ascending=False)
    )

    bar_traveler = (
        alt.Chart(rating_traveler)
        .mark_bar()
        .encode(
            x=alt.X("travelerType:N", sort="-y", title="Tipo de Viajante"),
            y=alt.Y("rating:Q", title="Nota Média"),
            tooltip=["travelerType", "rating"]
        )
        .properties(height=300)
    )

    st.altair_chart(bar_traveler, use_container_width=True)

# ---- Média de noites por nota
with col2:
    st.subheader("🌙 Média de Noites por Nota")

    nights_rating = (
        df_f.groupby("rating", as_index=False)["numberOfNights"]
            .mean()
    )

    line_nights = (
        alt.Chart(nights_rating)
        .mark_line(point=True)
        .encode(
            x=alt.X("rating:Q", title="Nota"),
            y=alt.Y("numberOfNights:Q", title="Número Médio de Noites"),
            tooltip=["rating", "numberOfNights"]
        )
        .properties(height=300)
    )

    st.altair_chart(line_nights, use_container_width=True)

# =========================
# TEXTOS DE REVIEWS
# =========================
st.markdown("---")
st.subheader("📝 Amostra de Comentários")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Comentários Positivos**")
    st.dataframe(
        df_f[["userName", "municipio", "rating", "likedText"]]
        .dropna(subset=["likedText"])
        .head(20),
        use_container_width=True
    )

with col2:
    st.markdown("**Comentários Negativos**")
    st.dataframe(
        df_f[["userName", "municipio", "rating", "dislikedText"]]
        .dropna(subset=["dislikedText"])
        .head(20),
        use_container_width=True
    )

# =========================
# BASE FINAL
# =========================
st.markdown("---")
st.subheader("📄 Base de Dados (Filtrada)")
st.dataframe(df_f, use_container_width=True)
