import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard de Reviews",
    layout="wide",
    page_icon="⭐"
)

# =========================
# LOAD DOS DADOS
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("booking-reviews-20102025_final.csv")
    df.columns = df.columns.str.strip()
    
    # Conversões de datas
    date_cols = ["checkInDate", "checkOutDate", "reviewDate"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    
    return df

df = load_data()

# =========================
# TÍTULO
# =========================
st.title("📊 Análise de Reviews de Hospedagens")
st.markdown("Dashboard interativo para análise de avaliações, perfil de viajantes e comportamento dos reviews.")

# =========================
# SIDEBAR - FILTROS
# =========================
st.sidebar.header("🔍 Filtros")

# Filtro por município
municipios = sorted(df["municipio"].dropna().unique())
municipio_sel = st.sidebar.multiselect(
    "Município",
    options=municipios
)

# Filtro por tipo de viajante
traveler_types = sorted(df["travelerType"].dropna().unique())
traveler_sel = st.sidebar.multiselect(
    "Tipo de Viajante",
    options=traveler_types
)

# Filtro por nota
rating_min, rating_max = st.sidebar.slider(
    "Nota da Avaliação",
    float(df["rating"].min()),
    float(df["rating"].max()),
    (float(df["rating"].min()), float(df["rating"].max()))
)

# Aplicação dos filtros
if municipio_sel:
    df = df[df["municipio"].isin(municipio_sel)]

if traveler_sel:
    df = df[df["travelerType"].isin(traveler_sel)]

df = df[df["rating"].between(rating_min, rating_max)]

# =========================
# KPIs
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Reviews", len(df))
col2.metric("Nota Média", round(df["rating"].mean(), 2))
col3.metric("Municípios", df["municipio"].nunique())
col4.metric("Tipos de Viajante", df["travelerType"].nunique())

# =========================
# GRÁFICOS
# =========================
st.markdown("---")
col1, col2 = st.columns(2)

# Distribuição das notas
fig_rating = px.histogram(
    df,
    x="rating",
    nbins=10,
    title="Distribuição das Avaliações"
)
col1.plotly_chart(fig_rating, use_container_width=True)

# Reviews ao longo do tempo
reviews_time = (
    df.groupby(df["reviewDate"].dt.to_period("M"))
    .size()
    .reset_index(name="total_reviews")
)
reviews_time["reviewDate"] = reviews_time["reviewDate"].astype(str)

fig_time = px.line(
    reviews_time,
    x="reviewDate",
    y="total_reviews",
    markers=True,
    title="Volume de Reviews ao Longo do Tempo"
)
col2.plotly_chart(fig_time, use_container_width=True)

# =========================
# ANÁLISES ADICIONAIS
# =========================
st.markdown("---")
col1, col2 = st.columns(2)

# Nota média por tipo de viajante
rating_traveler = (
    df.groupby("travelerType")["rating"]
    .mean()
    .reset_index()
    .sort_values("rating", ascending=False)
)

fig_traveler = px.bar(
    rating_traveler,
    x="travelerType",
    y="rating",
    title="Nota Média por Tipo de Viajante"
)
col1.plotly_chart(fig_traveler, use_container_width=True)

# Número médio de noites por nota
nights_rating = (
    df.groupby("rating")["numberOfNights"]
    .mean()
    .reset_index()
)

fig_nights = px.line(
    nights_rating,
    x="rating",
    y="numberOfNights",
    markers=True,
    title="Média de Noites por Nota"
)
col2.plotly_chart(fig_nights, use_container_width=True)

# =========================
# TEXTOS DE REVIEWS
# =========================
st.markdown("---")
st.subheader("📝 Análise Textual dos Reviews")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Comentários Positivos (likedText)**")
    st.dataframe(
        df[["userName", "municipio", "rating", "likedText"]]
        .dropna(subset=["likedText"])
        .head(20),
        use_container_width=True
    )

with col2:
    st.markdown("**Comentários Negativos (dislikedText)**")
    st.dataframe(
        df[["userName", "municipio", "rating", "dislikedText"]]
        .dropna(subset=["dislikedText"])
        .head(20),
        use_container_width=True
    )

# =========================
# BASE COMPLETA
# =========================
st.markdown("---")
st.subheader("📄 Base de Dados Filtrada")
st.dataframe(df, use_container_width=True)
