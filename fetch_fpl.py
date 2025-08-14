
import json, os, datetime, sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def fetch_json(url, headers=None, timeout=60):
    req = Request(url, headers=headers or {"User-Agent":"Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as resp:
        return json.load(resp)

def safe_fetch(url, headers=None, timeout=60):
    try:
        return fetch_json(url, headers=headers, timeout=timeout), None
    except Exception as e:
        return None, str(e)

def read_local_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def fetch_fpl(cfg):
    base = cfg["base_url"].rstrip("/")
    def u(path): return f"{base}{path}"
    data = {}
    bs, err = safe_fetch(u(cfg["endpoints"]["bootstrap_static"]))
    data["bootstrap_static"] = bs or {"_error": err}
    fx, err = safe_fetch(u(cfg["endpoints"]["fixtures"]))
    data["fixtures"] = fx or {"_error": err}
    entry, err = safe_fetch(u(cfg["endpoints"]["entry"].format(manager_id=cfg["manager_id"])))
    data["entry"] = entry or {"_error": err}
    leagues = {}
    for lid in cfg["league_ids"]:
        league, err = safe_fetch(u(cfg["endpoints"]["league"].format(league_id=lid)))
        leagues[str(lid)] = league or {"_error": err}
    data["leagues"] = leagues
    return data

def fetch_odds(cfg):
    odds_cfg = cfg.get("odds", {})
    provider = odds_cfg.get("provider", "THE_ODDS_API")
    api_key = os.getenv("ODDS_API_KEY", "").strip()
    if not odds_cfg.get("enabled", False) or not api_key:
        return {"enabled": False, "reason": "missing_api_key_or_disabled"}

    if provider.upper() == "THE_ODDS_API":
        base = os.getenv("ODDS_API_BASE", "https://api.the-odds-api.com/v4")
        sport_key = os.getenv("ODDS_SPORT_KEY", odds_cfg.get("sport_key","soccer_epl"))
        regions = os.getenv("ODDS_REGIONS", odds_cfg.get("regions","eu"))
        markets = os.getenv("ODDS_MARKETS", odds_cfg.get("markets","h2h,totals"))
        url = f"{base}/sports/{sport_key}/odds?regions={regions}&markets={markets}&oddsFormat=decimal&apiKey={api_key}"
        data, err = safe_fetch(url, timeout=60)
        if data is None:
            return {"enabled": True, "provider": provider, "error": err}
        trimmed = []
        for m in data:
            trimmed.append({
                "id": m.get("id"),
                "commence_time": m.get("commence_time"),
                "home_team": m.get("home_team"),
                "away_team": m.get("away_team"),
                "bookmakers": m.get("bookmakers", [])[:1]
            })
        return {"enabled": True, "provider": provider, "sport_key": sport_key, "matches": trimmed}
    else:
        return {"enabled": False, "reason": f"provider_not_supported:{provider}"}

def fetch_optional(repo_root, env_var, fallback_relpath, key_name):
    url = os.getenv(env_var, "").strip()
    if url:
        data, err = safe_fetch(url, timeout=60)
        if data is not None:
            return {"source":"remote","confidence":"medium","data":data}
    local = os.path.join(repo_root, fallback_relpath)
    data = read_local_json(local)
    if data is None:
        # minimal structure per key
        if key_name == "set_pieces":
            data = {"penalties":[],"corners":[],"direct_freekicks":[]}
        elif key_name == "injuries":
            data = {"players":[]}
        elif key_name == "elite":
            data = {"highlights":[]}
    return {"source":"fallback_local","confidence":"low","data":data}

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)

    out = {}
    out["fpl"] = fetch_fpl(cfg)
    out["set_pieces"] = fetch_optional(here, "SETPIECES_URL", "extras/setpieces.json", "set_pieces")
    out["injuries"]   = fetch_optional(here, "INJURIES_URL", "extras/injuries.json", "injuries")
    out["elite"]      = fetch_optional(here, "ELITE_FEEDS_URL", "extras/elite_feeds.json", "elite")
    out["odds"]       = fetch_odds(cfg)

    out["_fetched_at_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
    out["_note"] = "Public FPL feed for Raakens Disipler (Henrik). Some sections may be fallbacks with low confidence."

    out_dir = os.path.join(here, "data")
    os.makedirs(out_dir, exist_ok=True)
    latest_path = os.path.join(out_dir, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",",":"))
    pretty_path = os.path.join(out_dir, "latest.pretty.json")
    with open(pretty_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote:", latest_path)
    print("Wrote:", pretty_path)

if __name__ == "__main__":
    sys.exit(main())
