# SteamScope — Team Ryan

BANA409 Assignment 4, **Part 1: The Data App**. A small Streamlit dashboard for an indie game publishing lead. The separate phone trade-in exercise in Part 2 is outside this repository's scope.

## Step 1 — Dataset and decision-maker

**Dataset:** [Steam Store Games (Clean dataset), Nik Davis, Kaggle](https://www.kaggle.com/datasets/nikdavis/steam-store-games). The committed `steam.csv` is the original CSV downloaded through Kaggle's dataset download endpoint; no sampling or aggregation was applied to the source file. It contains 27,075 games, 18 columns, and approximately 5.8 MB, below the exercise's 25 MB guideline. One row is one Steam application/game, identified by `appid`. These are real observations collected from Steam and SteamSpy, not simulated games.

The release dates in this file run from 30 June 1997 through 1 May 2019. This is a **2019 snapshot**, not current market data; release date is not the date a price or rating was measured. The Kaggle listing reports its last update as 12 June 2019. The precise per-row observation dates are not supplied. The [author's collection notebook](https://nik-davis.github.io/posts/2019/steam-data-collection/) shows GBP prices; price labels in the app therefore use pounds. These are listed prices at collection, not verified original launch prices. The dataset license is **CC BY 4.0**; attribution is included in the app and this README. Original collection and dataset copyright remain with their respective owners.

**One user:** the publishing lead at a small independent PC game publisher, reviewing comparable titles before setting the next game's positioning and price range. This historical version demonstrates the workflow. A current launch decision would require a fresh extract.

## Step 2 — Why a dashboard

The lead would review this every Monday during release planning, and again before pricing meetings. **If the publishing lead sees that the relevant paid-game peer group is concentrated below the proposed price and its player reception is stronger, they will shortlist comparable titles and request a pricing and positioning review before approving the proposal.** This is a research trigger, not a rule that competitors' prices should be copied.

Without it, the lead would search store pages and copy prices and review counts into a spreadsheet for each meeting. That repeats manual work and risks mixing currencies, release cohorts, and free-to-play games. No measured time saving is claimed. A weekly email would freeze one peer group; this user needs to change genre, release years, business model, and review threshold during a meeting. A one-off report would go stale in the intended production workflow, while an alert alone cannot explain which comparable games deserve inspection.

## Step 3 — EDA, selection, and layout

`eda.ipynb` contains the executed shape, data types, missing values, duplicate checks, price/review distributions, and price-versus-reception exploration. It can be rerun independently of Streamlit. The raw CSV has no blank fields and no duplicated application IDs. Ratings are strongly affected by review volume, so a minimum-review filter is useful. Prices and review counts have long upper tails, so medians are more defensible headline summaries than means.

### Three headline numbers

1. **Comparable games:** distinct games in the selected peer group. This tells the lead whether the comparison is broad enough to investigate.
2. **Median listed price (GBP):** the middle game-level listed price, including zero-priced games only when the selected business-model filter includes them. It is a benchmark, not a forecast of willingness to pay.
3. **Median positive reviews per game:** compute `positive_ratings / (positive_ratings + negative_ratings)` for every reviewed game, then take the unweighted median. A blockbuster does not dominate this measure. Zero-review games have an undefined percentage and are excluded from this metric, not assigned 0%.

### Two supporting charts

- **Price distribution:** game counts in explicit price bands. The median alone hides whether the peer group clusters in one range or splits across cheap and premium titles. Free games have their own band. Paid bins are lower-exclusive and upper-inclusive; the final bin is above £30.
- **Reception by release year:** median game-level positive-review percentage for each release cohort, with reviewed-game counts in tooltips. The user can check whether a price reference comes from older or newer peers. This is a cross-sectional cohort comparison, **not** a time series showing ratings changing. Empty cohorts are missing, not zero. Older games have had more time to accumulate reviews and 2019 ends in May.

### Filters and page order

Genre, release years, paid/free status, and minimum reviews define the actual competitive set. Genre uses exact membership in the semicolon-separated labels, so one game is counted once even if it has several genres. Defaults are Indie, paid, 2016–2018, and at least 50 reviews: a recent set of complete release years relative to this snapshot, with some review evidence. The review threshold is an analyst choice, not statistical proof of reliability; it creates visibility bias against little-reviewed games and can be lowered.

The page sketch is: **title and user/decision caption → snapshot and refresh disclosure → three side-by-side metrics → two side-by-side charts → expandable game details and CSV download → attribution.** Filters sit in the sidebar. The source-period disclosure comes before the numbers because mistaking 2019 data for today's market would invalidate the decision. Metrics answer the quick peer-group question; charts show spread and cohort differences; details come last because they are for selecting titles to research.

### What I cut

- **Revenue and profit estimates.** Multiplying the owners-range midpoint by the listed price would imply precision that is unavailable. Owners include estimates and may include bundles or free copies, prices can change, and refunds, discounts, fees, and costs are missing. The raw estimated owners range is available only in the optional detail table.
- **Top publishers and achievement counts.** Both can produce attractive rankings, but they do not directly help this lead compare prices and reception for a chosen peer group. Publisher size could distract from a small indie title's competitive set.
- **Playtime as a headline.** The EDA checks it, but zero values can reflect limited observations and titles differ in intended length. It would add another ambiguous success measure.

### Handling misleading data

The app labels currency and historical coverage, separates free games, identifies the review denominator, provides a minimum-review filter, and displays an empty-state message for impossible filters. It does not claim causal links between price and reception, equate owners with purchases, or draw market-growth conclusions from a partial 2019 cohort. Genre totals are overlapping if users compare different filter settings; they must not be summed. The CSV contains only titles captured by the collection process, so it is not proof of complete catalog coverage or a representative sample of future releases.

## Step 4 — Refresh and action

**Production refresh:** weekly, on Sunday night, from an authorized current Steam/SteamSpy extract; store the observation timestamp and currency for every extract. The publishing lead reviews it on Monday and before each pricing decision. Minute-level updates add cost without changing a weekly planning decision. This demo reads a frozen bundled CSV and performs **no automatic refresh**; clearing the cache cannot make the 2019 data current.

**Track:** the median listed price of a fixed paid-game competitor panel in GBP. If it changes by at least **10% week over week**, with at least 30 comparable games and no panel-membership change, the lead should investigate promotions and changed store prices before approving the next proposal. This is a proposed operational threshold, not an effect established by this single snapshot. A production panel history and discount flags are needed to distinguish promotions from sustained price changes; the demo does not manufacture that history.

**Staleness cost:** a week-old production extract can miss a promotion or repricing and send the lead into a meeting with the wrong peer benchmark. If a production extract is older than seven days, show a stale-data banner and refresh before pricing approval. This historical demo already warns that it is unsuitable for a present-day launch decision.

## License

Application code and original documentation: MIT (see LICENSE). The bundled Kaggle dataset remains CC BY 4.0 by Nik Davis; the MIT license does not relicense this source data.

## Run locally

Python 3.14 is the course-required deployment version. With [uv](https://docs.astral.sh/uv/):

```sh
uv sync
uv run streamlit run app.py
```

For the EDA notebook, use `uv sync --group dev` and a Jupyter-compatible editor. Alternatively install `requirements.txt` and run `streamlit run app.py`. The app reads the committed CSV relative to `app.py`, requires no Kaggle login or API calls at startup, and needs no secrets.

## Deploy on Streamlit Community Cloud

- Repository: `ryanhu0628-111/steam-market-dashboard`
- Branch: `main`
- Main file path: `app.py`
- Advanced settings → Python version: **3.14**, as required by the exercise
- Secrets: leave empty

Click Deploy. The app URL is assigned by Streamlit after deployment; no deployed URL is claimed in advance. If the repository is not suggested, type its full name manually or paste the GitHub URL of `app.py`.

Before submission, review the README so its decisions reflect your own reasoning, and replace Team Ryan if your actual team uses a different name. Assignment 4 requires your deployed app and repository URLs in the first markdown cell of `phone-trade-in.ipynb`; that separate Part 2 submission is not included here.
