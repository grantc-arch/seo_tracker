# Old School SEO tracker

Tracks Google ranking position for key Old School product search terms over
time, using SerpApi (no Search Console access needed).

## How it works

1. `keywords.txt` — list of search terms to track (one per line). Edit this
   to add/remove terms.
2. `track_rankings.py` — checks each keyword's Google ranking for
   `oldschoolsa.com` via SerpApi and appends a row to `data/rankings.csv`.
3. `.github/workflows/track.yml` — runs step 2 automatically every Monday via
   GitHub Actions, and commits the updated CSV back to the repo.
4. `dashboard.py` — Streamlit app that reads `data/rankings.csv` and shows
   current rankings + trend charts.

## Setup

### 1. Get a SerpApi key
Sign up free at https://serpapi.com (free tier: 100 searches/month — plenty
for a handful of keywords checked weekly). Copy your API key from the
dashboard.

### 2. Push this folder to a GitHub repo

```bash
git init
git add .
git commit -m "Initial SEO tracker"
git remote add origin https://github.com/<you>/seo-tracker.git
git push -u origin main
```

### 3. Add your API key as a GitHub secret
In the repo: **Settings → Secrets and variables → Actions → New repository
secret**
- Name: `SERPAPI_KEY`
- Value: your SerpApi key

### 4. Run it once manually to seed data
You don't have to wait for Monday — trigger it manually:
**Actions tab → Track SEO rankings → Run workflow**

Or run locally:
```bash
export SERPAPI_KEY=your_key_here
pip install -r requirements.txt
python track_rankings.py
```

### 5. Deploy the dashboard
Push to GitHub, then deploy `dashboard.py` on
[Streamlit Community Cloud](https://streamlit.io/cloud) pointing at this repo
— same as the merch dashboard. It reads `data/rankings.csv` straight from the
repo, so it updates automatically each time the Action commits new data.

## Notes

- Rankings are checked against `google.co.za` to reflect local search results.
- A keyword with no matching Old School URL in the first page(s) of results
  shows as "not ranking" rather than a position — that's expected until it
  ranks or you adjust which pages/keywords you're tracking.
- Free SerpApi tier caps at 100 searches/month. Five keywords checked weekly
  uses 20/month, leaving headroom to add more keywords or check more often.
