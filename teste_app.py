import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# =========================
# CONFIGURAÇÃO VISUAL
# =========================
plt.style.use("seaborn-v0_8-whitegrid")
TEXT_COLOR = "#333333"

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

# Aplicação dos filtros
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

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(df_f["rating"], bins=10, edgecolor="white")

    ax.set_title("Distribuição das Avaliações", fontsize=12)
    ax.set_xlabel("Nota")
    ax.set_ylabel("Quantidade de Reviews")

    st.pyplot(fig)

# ---- Volume de Reviews ao Longo do Tempo
with col2:
    st.subheader("📈 Volume de Reviews ao Longo do Tempo")

    reviews_time = (
        df_f.set_index("reviewDate")
            .resample("M")
            .size()
            .reset_index(name="total_reviews")
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(
        reviews_time["reviewDate"],
        reviews_time["total_reviews"],
        marker="o"
    )

    ax.set_title("Volume de Reviews ao Longo do Tempo", fontsize=12)
    ax.set_xlabel("Data")
    ax.set_ylabel("Total de Reviews")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.tick_params(axis="x", rotation=45)

    st.pyplot(fig)

# =========================
# ANÁLISES COMPLEMENTARES
# =========================
st.markdown("---")
col1, col2 = st.columns(2)

# ---- Nota média por tipo de viajante
with col1:
    st.subheader("🧍 Nota Média por Tipo de Viajante")

    rating_traveler = (
        df_f.groupby("travelerType")["rating"]
            .mean()
            .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    rating_traveler.plot(kind="bar", ax=ax)

    ax.set_title("Nota Média por Tipo de Viajante", fontsize=12)
    ax.set_xlabel("Tipo de Viajante")
    ax.set_ylabel("Nota Média")
    ax.tick_params(axis="x", rotation=30)

    st.pyplot(fig)

# ---- Média de noites por nota
with col2:
    st.subheader("🌙 Média de Noites por Nota")

    nights_rating = (
        df_f.groupby("rating")["numberOfNights"]
            .mean()
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(
        nights_rating.index,
        nights_rating.values,
        marker="o"
    )

    ax.set_title("Média de Noites por Nota", fontsize=12)
    ax.set_xlabel("Nota")
    ax.set_ylabel("Número Médio de Noites")

    st.pyplot(fig)

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
