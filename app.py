from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SteamScope | Market benchmarks", page_icon="🎮", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv(Path(__file__).parent / "steam.csv")
    data = data.drop_duplicates("appid").copy()
    data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")
    data["year"] = data["release_date"].dt.year
    data["reviews"] = data["positive_ratings"] + data["negative_ratings"]
    data["positive_pct"] = data["positive_ratings"].div(data["reviews"].replace(0, float("nan"))) * 100
    return data

df = load_data()
st.title("SteamScope — Team Ryan")
st.caption("For an indie publishing lead: compare competing games and set a price range for further research.")
st.info("Historical Kaggle snapshot (2019); release dates: 30 Jun 1997–1 May 2019. Prices are GBP at collection, not launch prices. Production plan: weekly refresh; Monday review.")

with st.sidebar:
    st.header("Define your peer group")
    genre_options = sorted(set(";".join(df["genres"].dropna()).split(";")))
    genre = st.selectbox("Genre", ["All genres"] + genre_options, index=(["All genres"] + genre_options).index("Indie"))
    years = st.slider("Release years", 1997, 2019, (2016, 2018), help="2019 ends on 1 May and is incomplete.")
    pricing = st.radio("Business model", ["Paid games", "Free games", "All games"])
    min_reviews = st.select_slider("Minimum reviews per game", options=[0, 10, 50, 100, 500, 1000], value=50, help="Reduces unstable percentages. This deliberately excludes many little-reviewed games.")
    st.caption("Default: paid indie games from 2016–2018 with at least 50 reviews. Use complete release years for comparisons.")

mask = df["year"].between(*years) & (df["reviews"] >= min_reviews)
if genre != "All genres":
    mask &= df["genres"].str.split(";").apply(lambda labels: genre in labels if isinstance(labels, list) else False)
if pricing == "Paid games":
    mask &= df["price"] > 0
elif pricing == "Free games":
    mask &= df["price"] == 0
view = df.loc[mask].copy()
if view.empty:
    st.warning("No games match these filters. Widen the release years or lower the review minimum.")
    st.stop()

a, b, c = st.columns(3)
a.metric("Comparable games", f"{len(view):,}")
b.metric("Median listed price", f"£{view['price'].median():.2f}")
reviewed = view.loc[view["reviews"] > 0]
c.metric("Median positive reviews per game", f"{reviewed['positive_pct'].median():.1f}%" if not reviewed.empty else "N/A")
st.caption(f"All metrics use the same {len(view):,} filtered games. Positive-review KPI is the unweighted median of each game's positive / total reviews; zero-review games are excluded only from this KPI.")

left, right = st.columns(2)
with left:
    st.subheader("Listed price distribution")
    bins = [-0.01, 0, 5, 10, 15, 20, 30, float("inf")]
    labels = ["Free", "£0–5", "£5–10", "£10–15", "£15–20", "£20–30", "£30+"]
    bands = pd.cut(view["price"], bins=bins, labels=labels, right=True)
    counts = bands.value_counts(sort=False).rename_axis("Price band").reset_index(name="Games")
    chart = alt.Chart(counts).mark_bar(color="#2675b8").encode(
        x=alt.X("Price band:N", sort=labels, axis=alt.Axis(labelAngle=-35)),
        y=alt.Y("Games:Q", title="Number of games"), tooltip=["Price band:N", "Games:Q"]
    ).properties(height=310)
    st.altair_chart(chart, width="stretch")
    st.caption("Paid bands exclude the lower boundary and include the upper boundary; £30+ means above £30. This is a historical peer-price reference, not a recommended launch price.")
with right:
    st.subheader("Player reception by release year")
    reception = reviewed.groupby("year", as_index=False).agg(positive_pct=("positive_pct", "median"), games=("appid", "size"))
    all_years = pd.DataFrame({"year": range(years[0], years[1] + 1)})
    reception = all_years.merge(reception, on="year", how="left")
    chart = alt.Chart(reception).mark_bar(color="#23a08d").encode(
        x=alt.X("year:O", title="Release year", axis=alt.Axis(labelAngle=-35)),
        y=alt.Y("positive_pct:Q", title="Median positive reviews (%)", scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip("year:O", title="Release year"), alt.Tooltip("positive_pct:Q", title="Median positive %", format=".1f"), alt.Tooltip("games:Q", title="Reviewed games")]
    ).properties(height=310)
    st.altair_chart(chart, width="stretch")
    st.caption("Each bar is a different release cohort observed in one snapshot, not a trend in ratings over time. Missing bars mean no reviewed games. Older titles had longer to gather reviews; 2019 is partial.")

with st.expander("Inspect and download comparable games"):
    detail = view[["name", "release_date", "genres", "price", "reviews", "positive_pct", "owners"]].sort_values("reviews", ascending=False)
    detail = detail.rename(columns={"name": "Game", "release_date": "Released", "genres": "Genres", "price": "Price (GBP)", "reviews": "Reviews", "positive_pct": "Positive reviews (%)", "owners": "Estimated owners range"})
    st.dataframe(detail, hide_index=True, width="stretch", column_config={"Price (GBP)": st.column_config.NumberColumn(format="£%.2f"), "Positive reviews (%)": st.column_config.NumberColumn(format="%.1f%%")})
    st.download_button("Download this peer group", detail.to_csv(index=False).encode("utf-8"), "steam_peer_group.csv", "text/csv")

st.caption("Source: Nik Davis, Steam Store Games (Clean dataset), Kaggle, CC BY 4.0. Real Steam / SteamSpy observations; owners are estimates, not sales. No revenue or profit is inferred. Games may have multiple genres; genre matches count each app once.")
st.markdown("[Kaggle dataset](https://www.kaggle.com/datasets/nikdavis/steam-store-games) · [Collection methodology](https://nik-davis.github.io/posts/2019/steam-data-collection/)")
