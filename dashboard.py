import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Old School SEO Tracker", layout="wide")

DATA_FILE = Path("data/rankings.csv")

st.title("Old School — SEO visibility tracker")
st.caption("Google ranking position (google.co.za) for key product search terms, tracked weekly via SerpApi.")

if not DATA_FILE.exists():
    st.info(
        "No ranking data yet. Once `track_rankings.py` has run at least once "
        "(locally or via the GitHub Action), `data/rankings.csv` will appear here."
    )
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
df["position"] = pd.to_numeric(df["position"], errors="coerce")

if df.empty:
    st.info("Rankings file is empty — waiting on the first tracking run.")
    st.stop()

latest_ts = df["timestamp"].max()
latest = df[df["timestamp"] == latest_ts]

col1, col2, col3 = st.columns(3)
tracked = latest["keyword"].nunique()
ranked = latest["position"].notna().sum()
avg_pos = latest["position"].dropna().mean()

col1.metric("Keywords tracked", tracked)
col2.metric("Currently ranking (top 100)", f"{ranked}/{tracked}")
col3.metric("Average position", f"{avg_pos:.1f}" if pd.notna(avg_pos) else "—")

st.subheader("Latest rankings")
display_latest = latest[["keyword", "position", "url"]].copy()
display_latest["position"] = display_latest["position"].apply(
    lambda x: int(x) if pd.notna(x) else "not ranking"
)
st.dataframe(display_latest, use_container_width=True, hide_index=True)

st.subheader("Ranking trend over time")
plot_df = df.dropna(subset=["position"]).copy()
if plot_df.empty:
    st.info("No ranking positions recorded yet for any keyword.")
else:
    fig = px.line(
        plot_df.sort_values("timestamp"),
        x="timestamp",
        y="position",
        color="keyword",
        markers=True,
    )
    # Lower position number = better rank, so flip the y-axis
    fig.update_yaxes(autorange="reversed", title="Google position (lower is better)")
    fig.update_xaxes(title="Date")
    fig.update_layout(legend_title_text="Keyword", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Keyword history")
keyword_choice = st.selectbox("Select a keyword", sorted(df["keyword"].unique()))
kw_df = df[df["keyword"] == keyword_choice].sort_values("timestamp")
st.dataframe(
    kw_df[["timestamp", "position", "url"]],
    use_container_width=True,
    hide_index=True,
)
