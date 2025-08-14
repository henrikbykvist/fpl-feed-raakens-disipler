
# FPL Feed – Raakens Disipler (with optional odds)

Publishes a single JSON at `data/latest.json` every hour via GitHub Actions.
Read this from your custom FPL-GPT.

## Setup
1) Create a **public** GitHub repo and upload these files/folders exactly as-is.
2) Go to **Actions**, enable workflows and click **Run workflow** once.
3) The workflow also runs **every hour** (UTC).

### Odds (optional)
Add a repository secret:
- `ODDS_API_KEY` (Settings → Secrets and variables → Actions → New repository secret)
Optional repository variables:
- `ODDS_API_BASE` (default `https://api.the-odds-api.com/v4`)
- `ODDS_SPORT_KEY` (default `soccer_epl`)
- `ODDS_REGIONS` (default `eu`)
- `ODDS_MARKETS` (default `h2h,totals`)

### Optional external sources
Add repository variables to point at your own JSON feeds (else fallbacks in `extras/` are used):
- `SETPIECES_URL`, `INJURIES_URL`, `ELITE_FEEDS_URL`

## Public raw URL
`https://raw.githubusercontent.com/<USER>/<REPO>/main/data/latest.json`

## Local test (optional)
```bash
python3 fetch_fpl.py
python3 validate_feed.py
open data/latest.pretty.json
```
