import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Music & Mental Health Analytics",
    page_icon="🎵",
    layout="wide"
)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/mxmh_survey_results.csv")
    return df

df = load_data()

# ------------------------------------------------
# CLEANING
# ------------------------------------------------
df = df.copy()

df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Hours per day"] = pd.to_numeric(df["Hours per day"], errors="coerce")

mental_cols = ["Anxiety","Depression","Insomnia","OCD"]

for col in mental_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------
st.sidebar.title("🎵 Music Analytics")

selected_genre = st.sidebar.multiselect(
    "Favorite Genre",
    sorted(df["Fav genre"].dropna().unique()),
    default=None
)

age_range = st.sidebar.slider(
    "Age Range",
    int(df["Age"].min()),
    int(df["Age"].max()),
    (
        int(df["Age"].min()),
        int(df["Age"].max())
    )
)

filtered = df[
    (df["Age"] >= age_range[0]) &
    (df["Age"] <= age_range[1])
]

if selected_genre:
    filtered = filtered[
        filtered["Fav genre"].isin(selected_genre)
    ]

# ------------------------------------------------
# HEADER
# ------------------------------------------------
st.title("🎵 Music & Mental Health Dashboard")

st.markdown(
"""
Comprehensive exploratory analysis of music listening
habits and mental health indicators.
"""
)

# ------------------------------------------------
# KPI SECTION
# ------------------------------------------------
c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("Respondents", len(filtered))
c2.metric("Avg Age", round(filtered["Age"].mean(),1))
c3.metric("Avg Hours", round(filtered["Hours per day"].mean(),1))
c4.metric(
    "Top Genre",
    filtered["Fav genre"].mode()[0]
)
c5.metric(
    "Top Platform",
    filtered["Primary streaming service"].mode()[0]
)

st.divider()

# ------------------------------------------------
# STREAMING ANALYSIS
# ------------------------------------------------
st.subheader("Streaming Service Distribution")

service = (
    filtered["Primary streaming service"]
    .value_counts()
    .reset_index()
)

service.columns = ["Service","Count"]

fig = px.pie(
    service,
    names="Service",
    values="Count",
    hole=0.45
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# GENRE ANALYSIS
# ------------------------------------------------
st.subheader("Favorite Genres")

genre = (
    filtered["Fav genre"]
    .value_counts()
    .reset_index()
)

genre.columns = ["Genre","Count"]

fig = px.bar(
    genre,
    x="Genre",
    y="Count",
    color="Count"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# MENTAL HEALTH DISTRIBUTIONS
# ------------------------------------------------
st.subheader("Mental Health Scores")

col1,col2 = st.columns(2)

with col1:
    fig = px.histogram(
        filtered,
        x="Anxiety",
        nbins=10,
        title="Anxiety"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        filtered,
        x="Depression",
        nbins=10,
        title="Depression"
    )
    st.plotly_chart(fig, use_container_width=True)

col3,col4 = st.columns(2)

with col3:
    fig = px.histogram(
        filtered,
        x="Insomnia",
        nbins=10,
        title="Insomnia"
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = px.histogram(
        filtered,
        x="OCD",
        nbins=10,
        title="OCD"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# CORRELATION
# ------------------------------------------------
st.subheader("Correlation Matrix")

corr_cols = [
    "Age",
    "Hours per day",
    "Anxiety",
    "Depression",
    "Insomnia",
    "OCD"
]

corr = filtered[corr_cols].corr()

fig = px.imshow(
    corr,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# HOURS VS MENTAL HEALTH
# ------------------------------------------------
st.subheader("Listening Hours vs Mental Health")

metric = st.selectbox(
    "Select Mental Health Metric",
    mental_cols
)

fig = px.scatter(
    filtered,
    x="Hours per day",
    y=metric,
    color="Fav genre",
    trendline="ols",
    opacity=0.7
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# ADVANCED INSIGHTS
# ------------------------------------------------
st.subheader("Advanced Behavioral Insights")

c1,c2 = st.columns(2)

with c1:

    exploratory = (
        filtered
        .groupby("Exploratory")[mental_cols]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        exploratory,
        x="Exploratory",
        y=mental_cols,
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with c2:

    instrumental = (
        filtered
        .groupby("Instrumentalist")[mental_cols]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        instrumental,
        x="Instrumentalist",
        y=mental_cols,
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ------------------------------------------------
# HEATMAP OF GENRE FREQUENCY
# ------------------------------------------------
st.subheader("Genre Frequency Heatmap")

freq_cols = [
    c for c in df.columns
    if "Frequency [" in c
]

mapping = {
    "Never":0,
    "Rarely":1,
    "Sometimes":2,
    "Very frequently":3
}

heat_df = filtered[freq_cols].replace(mapping)

genre_heat = heat_df.mean().sort_values()

fig = px.imshow(
    [genre_heat.values],
    x=genre_heat.index,
    aspect="auto"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ------------------------------------------------
# DATA VIEW
# ------------------------------------------------
st.subheader("Dataset Preview")

st.dataframe(filtered)

csv = filtered.to_csv(index=False)

st.download_button(
    "Download Filtered Data",
    csv,
    "filtered_music_data.csv",
    "text/csv"
)
