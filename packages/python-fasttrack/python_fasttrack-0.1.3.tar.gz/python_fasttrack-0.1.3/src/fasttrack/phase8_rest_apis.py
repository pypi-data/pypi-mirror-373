#!/usr/bin/env python3
"""
Phase 8 — REST APIs (requests + JSON) starter project — AUTH DEMOS INCLUDED

What you’ll practice:
- GET requests with timeouts & query params
- JSON parsing + error handling
- Pagination (GitHub API)
- Rate‑limit awareness (headers + backoff)
- Reusable requests.Session with retries
- Save results to CSV/Excel
- Minimal CLI to run demos
- API key auth via env var (OpenWeatherMap)

APIs used:
- GitHub REST v3 (public; optional auth via GITHUB_TOKEN)
- Open‑Meteo forecast API (no key)
- JSONPlaceholder (demo data)
- OpenWeatherMap Current Weather (requires key via OWM_API_KEY or --owm-key)
- SpaceX Public API v4/v5 (no key)

Auth notes:
- If env var `GITHUB_TOKEN` is set, requests include `Authorization: Bearer <token>`.
- If `python-dotenv` is installed and a `.env` exists, it will be auto‑loaded.
- For OpenWeatherMap, supply `--owm-key` or set `OWM_API_KEY` in env/.env.

Examples:
  python phase8_rest_apis.py github --org microsoft --limit 200 --excel api_outputs.xlsx
  python phase8_rest_apis.py weather --lat 60.39 --lon 5.32 --hours 24 --csv weather.csv
  python phase8_rest_apis.py todos --csv todos.csv
  python phase8_rest_apis.py owm --city Rome,IT --excel owm_rome.xlsx
  python phase8_rest_apis.py spacex --limit 20 --excel spacex_launches.xlsx
  python phase8_rest_apis.py github --org microsoft --limit 200 --excel api_outputs.xlsx
  python phase8_rest_apis.py weather --lat 60.39 --lon 5.32 --hours 24 --csv weather.csv
  python phase8_rest_apis.py todos --csv todos.csv
  python phase8_rest_apis.py owm --city Rome,IT --excel owm_rome.xlsx

Tip: add “-v” for verbose logs.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Optional dotenv support (if installed)
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # gracefully handle absence


# =============================
# HTTP plumbing (session + retry)
# =============================

def build_session(total_retries: int = 3, backoff_factor: float = 0.5, timeout_s: float = 10.0) -> Tuple[requests.Session, float]:
    """Return a (session, default_timeout_seconds) with sensible retry settings.
    Also checks env for a GitHub token and sets Authorization header if present.
    """
    # Load .env if python-dotenv is available
    if load_dotenv is not None:
        try:
            load_dotenv()  # developer convenience only
        except Exception:
            pass

    import os

    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS"),
        raise_on_status=False,
    )
    sess = requests.Session()
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    # GitHub recommends a User‑Agent header
    sess.headers.update({
        "User-Agent": "phase8-rest-apis-starter/1.4",
        "Accept": "application/vnd.github+json, application/json",
    })

    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        sess.headers.update({"Authorization": f"Bearer {gh_token}"})
    return sess, timeout_s


def build_cached_session(cache_name: str = "phase8_cache", expire_seconds: int = 600,
                         total_retries: int = 3, backoff_factor: float = 0.5, timeout_s: float = 10.0) -> Tuple[requests.Session, float]:
    """Return a CachedSession if requests-cache is installed; otherwise fall back to normal session.
    Useful for quick iteration during development to avoid re-hitting public APIs.
    """
    try:
        import requests_cache  # type: ignore
    except Exception:
        # Fall back silently
        return build_session(total_retries=total_retries, backoff_factor=backoff_factor, timeout_s=timeout_s)

    # Load .env if available (for tokens)
    if load_dotenv is not None:
        try:
            load_dotenv()
        except Exception:
            pass

    import os
    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS"),
        raise_on_status=False,
    )
    sess = requests_cache.CachedSession(cache_name, expire_after=expire_seconds)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    sess.headers.update({
        "User-Agent": "phase8-rest-apis-starter/1.4",
        "Accept": "application/vnd.github+json, application/json",
    })
    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        sess.headers.update({"Authorization": f"Bearer {gh_token}"})
    return sess, timeout_s


@dataclass
class HTTPClient:
    session: requests.Session
    timeout_s: float = 10.0
    verbose: bool = False

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Tuple[Dict[str, Any] | List[Any], requests.Response]:
        if self.verbose:
            print(f"GET {url} params={params}")
        resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout_s)

        # If GitHub token is invalid, retry once without Authorization so public calls still work
        if resp.status_code == 401 and "api.github.com" in url and "Authorization" in self.session.headers:
            if self.verbose:
                print("401 Bad credentials. Retrying once without Authorization header…")
            auth = self.session.headers.pop("Authorization", None)
            try:
                resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout_s)
            finally:
                if auth is not None:
                    self.session.headers["Authorization"] = auth

        # Basic error handling
        if resp.status_code >= 400:
            try:
                err = resp.json()
            except Exception:
                err = {"message": resp.text[:200]}
            raise requests.HTTPError(f"HTTP {resp.status_code} for {url}: {err}")

        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise ValueError(f"Response was not valid JSON from {url}")

        return data, resp


# -----------------------------
# GitHub API — repos (with pagination)
# -----------------------------

def parse_link_header(link_value: str) -> Dict[str, str]:
    """Parse an RFC5988 Link header into a dict of {rel: url}."""
    out: Dict[str, str] = {}
    for part in link_value.split(','):
        segs = part.split(';')
        if len(segs) < 2:
            continue
        url = segs[0].strip().lstrip('<').rstrip('>')
        rel = None
        for s in segs[1:]:
            s = s.strip()
            if s.startswith('rel='):
                rel = s.split('=')[1].strip('"')
                break
        if rel:
            out[rel] = url
    return out


def github_list_repos(client: HTTPClient, org: Optional[str] = None, user: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    assert (org is None) ^ (user is None), "Provide exactly one of org or user."
    base = f"https://api.github.com/{'orgs/' + org + '/repos' if org else 'users/' + user + '/repos'}"
    per_page = min(100, max(1, limit))
    params = {"per_page": per_page, "type": "public", "sort": "updated"}
    results: List[Dict[str, Any]] = []
    url = base

    while url and len(results) < limit:
        data, resp = client.get_json(url, params=params)
        if not isinstance(data, list):
            raise ValueError("Expected a list of repos from GitHub API")
        for repo in data:
            results.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "private": repo.get("private"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count"),
                "forks_count": repo.get("forks_count"),
                "open_issues": repo.get("open_issues_count"),
                "updated_at": repo.get("updated_at"),
                "html_url": repo.get("html_url"),
            })
            if len(results) >= limit:
                break
        # Pagination via Link header
        next_url = None
        if 'Link' in resp.headers:
            links = parse_link_header(resp.headers['Link'])
            next_url = links.get('next')
        url = next_url
        params = None  # after first request, GitHub includes params in Link
        # Respect rate limit if returned
        rl_reset = resp.headers.get('X-RateLimit-Reset')
        rl_remaining = resp.headers.get('X-RateLimit-Remaining')
        if rl_remaining is not None and rl_reset is not None and rl_remaining == '0':
            try:
                reset_ts = int(rl_reset)
                sleep_for = max(0, reset_ts - int(time.time()) + 1)
                if client.verbose:
                    print(f"GitHub rate limit hit. Sleeping {sleep_for}s…")
                time.sleep(sleep_for)
            except Exception:
                time.sleep(60)

    return results


# -----------------------------
# Open‑Meteo — simple hourly temperature + wind
# -----------------------------

def open_meteo_forecast(client: HTTPClient, lat: float, lon: float, hours: int = 24) -> List[Dict[str, Any]]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m",
        "past_hours": 0,
        "forecast_hours": max(1, min(120, hours)),
        "timezone": "auto",
    }
    data, _ = client.get_json(url, params=params)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    winds = hourly.get("wind_speed_10m", [])
    out: List[Dict[str, Any]] = []
    for t, temp, wind in zip(times, temps, winds):
        out.append({
            "time": t,
            "temperature_C": temp,
            "wind_speed_m_s": wind,
        })
    return out


# -----------------------------
# JSONPlaceholder — demo todos
# -----------------------------

def jsonplaceholder_todos(client: HTTPClient) -> List[Dict[str, Any]]:
    url = "https://jsonplaceholder.typicode.com/todos"
    data, _ = client.get_json(url)
    if not isinstance(data, list):
        raise ValueError("Expected list of todos")
    return [
        {"id": d.get("id"), "userId": d.get("userId"), "title": d.get("title"), "completed": d.get("completed")}
        for d in data
    ]


# -----------------------------
# OpenWeatherMap — current weather (API key demo)
# -----------------------------

def owm_current_weather(client: HTTPClient, *, api_key: str, lat: Optional[float] = None, lon: Optional[float] = None, city: Optional[str] = None) -> Dict[str, Any]:
    """Fetch current weather via OpenWeatherMap.

    Authentication: query param `appid=<key>`.
    Location: either (lat, lon) or city name like "Rome,IT".
    """
    if (lat is None or lon is None) and not city:
        raise ValueError("Provide either --lat & --lon or --city for OWM")
    params: Dict[str, Any] = {"appid": api_key, "units": "metric"}
    if city:
        params["q"] = city
    else:
        params.update({"lat": lat, "lon": lon})
    url = "https://api.openweathermap.org/data/2.5/weather"
    data, _ = client.get_json(url, params=params)
    weather_list = data.get("weather", []) or [{}]
    w0 = weather_list[0] if isinstance(weather_list, list) else {}
    main = data.get("main", {})
    wind = data.get("wind", {})
    sysb = data.get("sys", {})
    record = {
        "name": data.get("name"),
        "country": sysb.get("country"),
        "dt": data.get("dt"),
        "condition": w0.get("main"),
        "description": w0.get("description"),
        "temp_C": main.get("temp"),
        "feels_like_C": main.get("feels_like"),
        "humidity_pct": main.get("humidity"),
        "wind_speed_m_s": wind.get("speed"),
        "wind_deg": wind.get("deg"),
        "lat": (data.get("coord") or {}).get("lat"),
        "lon": (data.get("coord") or {}).get("lon"),
    }
    return record


# -----------------------------
# Utilities: save to CSV/Excel/SQLite + metrics
# -----------------------------

def to_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame.from_records(rows)


def save_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def _excel_sanitize(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy safe for Excel: strip timezone info from datetimes."""
    out = df.copy()
    for col in out.columns:
        ser = out[col]
        # If pandas recognizes tz-aware dtype
        if pd.api.types.is_datetime64tz_dtype(ser):
            out[col] = ser.dt.tz_convert(None)
        # If object column may contain datetime objects with tz info
        elif ser.dtype == object and ser.map(lambda x: hasattr(x, 'tzinfo'), na_action='ignore').any():
            out[col] = pd.to_datetime(ser, errors='coerce').dt.tz_convert(None)
    return out


def save_excel(dfs: Dict[str, pd.DataFrame], path: str) -> None:
    """Write multiple DataFrames to one Excel file.
    - Converts tz-aware datetimes to tz-naive (Excel limitation)
    - If the target file is locked (open in Excel), saves to a timestamped filename
    """
    import datetime as _dt
    try:
        with pd.ExcelWriter(path, engine="openpyxl") as xlw:
            for sheet, df in dfs.items():
                df2 = _excel_sanitize(df)
                df2.to_excel(xlw, sheet_name=sheet[:31], index=False)
    except PermissionError:
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        alt = f"{path.rsplit('.', 1)[0]}_{ts}.xlsx"
        with pd.ExcelWriter(alt, engine="openpyxl") as xlw:
            for sheet, df in dfs.items():
                df2 = _excel_sanitize(df)
                df2.to_excel(xlw, sheet_name=sheet[:31], index=False)
        print(f"⚠️ '{path}' is locked (likely open in Excel). Wrote to '{alt}' instead.")


def save_sqlite(dfs: Dict[str, pd.DataFrame], path: str) -> None:
    """Append/replace tables into a SQLite DB file based on sheet names."""
    import sqlite3
    con = sqlite3.connect(path)
    try:
        for table, df in dfs.items():
            df2 = _excel_sanitize(df)  # also strips tz for sqlite text output
            df2.to_sql(table, con, if_exists='replace', index=False)
    finally:
        con.close()


def github_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Return a metrics dataframe derived from the raw GitHub repos df.

    Adds:
      - stars_per_fork: stargazers_count / forks_count (safe divide; 0 if forks=0)
      - stars_per_issue: stargazers_count / open_issues (safe divide; 0 if open_issues=0)
    Sorted by stars_per_fork desc, then stargazers_count desc.
    """
    if df.empty:
        return df.copy()
    m = df.copy()
    for col in ["stargazers_count", "forks_count", "open_issues"]:
        if col in m.columns:
            m[col] = pd.to_numeric(m[col], errors="coerce").fillna(0)
        else:
            m[col] = 0
    m["stars_per_fork"] = m.apply(lambda r: (r["stargazers_count"] / r["forks_count"]) if r["forks_count"] else 0.0, axis=1)
    m["stars_per_issue"] = m.apply(lambda r: (r["stargazers_count"] / r["open_issues"]) if r["open_issues"] else 0.0, axis=1)
    cols = [
        "name","full_name","language","stargazers_count","forks_count","open_issues",
        "stars_per_fork","stars_per_issue","updated_at","html_url",
    ]
    cols = [c for c in cols if c in m.columns]
    m = m[cols].sort_values(by=["stars_per_fork", "stargazers_count"], ascending=[False, False]).reset_index(drop=True)
    return m


# -----------------------------
# SpaceX — recent launches (no key)
# -----------------------------

def spacex_fetch_map(client: HTTPClient, endpoint: str, key_field: str = "id", value_field: str = "name") -> Dict[str, Any]:
    url = f"https://api.spacexdata.com/v4/{endpoint}"
    data, _ = client.get_json(url)
    mapping: Dict[str, Any] = {}
    if isinstance(data, list):
        for item in data:
            mapping[str(item.get(key_field))] = item.get(value_field)
    return mapping


def spacex_recent_launches(client: HTTPClient, limit: int = 20) -> List[Dict[str, Any]]:
    """Return a flat list of recent SpaceX launches with helpful fields.
    Uses v5 launches/query for sorting by date, and v4 endpoints for lookups.
    """
    # Build lookup maps (rocket id -> name, launchpad id -> name)
    rocket_map = spacex_fetch_map(client, "rockets")
    pad_map = spacex_fetch_map(client, "launchpads")

    # v5 launches/query with POST body for sorting + limit
    url = "https://api.spacexdata.com/v5/launches/query"
    body = {
        "query": {},
        "options": {
            "sort": {"date_utc": "desc"},
            "limit": max(1, min(100, int(limit)))
        }
    }
    # Use session.post directly but reuse headers/timeouts via client
    resp = client.session.post(url, json=body, timeout=client.timeout_s)
    if resp.status_code >= 400:
        try:
            err = resp.json()
        except Exception:
            err = {"message": resp.text[:200]}
        raise requests.HTTPError(f"HTTP {resp.status_code} for {url}: {err}")
    payload = resp.json()
    docs = payload.get("docs", []) if isinstance(payload, dict) else []

    rows: List[Dict[str, Any]] = []
    for d in docs:
        rocket_id = d.get("rocket")
        pad_id = d.get("launchpad")
        rows.append({
            "name": d.get("name"),
            "flight_number": d.get("flight_number"),
            "date_utc": d.get("date_utc"),
            "success": d.get("success"),
            "rocket": rocket_map.get(rocket_id, rocket_id),
            "launchpad": pad_map.get(pad_id, pad_id),
            "details": d.get("details"),
            "webcast": (d.get("links", {}) or {}).get("webcast"),
            "article": (d.get("links", {}) or {}).get("article"),
            "wikipedia": (d.get("links", {}) or {}).get("wikipedia"),
            "id": d.get("id"),
        })
    return rows


def spacex_summary(df: pd.DataFrame, months: int = 12) -> pd.DataFrame:
    """Summarize success counts and rates by rocket with a 365‑day window.

    Returns columns: rocket, launches, successes, success_rate_pct, first_date, last_date,
    last_365_launches, last_365_successes, last_365_success_rate_pct
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "rocket","launches","successes","success_rate_pct","first_date","last_date",
            "last_365_launches","last_365_successes","last_365_success_rate_pct"
        ])
    m = df.copy()
    m["date_utc"] = pd.to_datetime(m["date_utc"], errors="coerce", utc=True)
    # Normalize success to boolean ints
    m["_succ_int"] = pd.to_numeric(m["success"], errors="coerce").fillna(0).astype(bool).astype(int)

    # Overall aggregation without GroupBy.apply (avoids FutureWarning & duplicate columns)
    overall = (
        m.groupby("rocket", dropna=False)
         .agg(
            launches=("id", "size"),
            successes=("_succ_int", "sum"),
            first_date=("date_utc", "min"),
            last_date=("date_utc", "max"),
         )
         .reset_index()
    )
    overall["success_rate_pct"] = (overall["successes"] / overall["launches"] * 100).round(2)

    # Recent 365 days window
    now = pd.Timestamp.utcnow()
    recent_cut = now - pd.DateOffset(months=months)
    recent = m[m["date_utc"] >= recent_cut]
    recent_g = (
        recent.groupby("rocket", dropna=False)
              .agg(
                  last_365_launches=("id", "size"),
                  last_365_successes=("_succ_int", "sum"),
              )
              .reset_index()
    )
    if not recent_g.empty:
        recent_g["last_365_success_rate_pct"] = (
            (recent_g["last_365_successes"] / recent_g["last_365_launches"] * 100).round(2)
        )
    else:
        recent_g["last_365_success_rate_pct"] = pd.Series(dtype="float")

    out = pd.merge(overall, recent_g, on="rocket", how="left").fillna({
        "last_365_launches": 0,
        "last_365_successes": 0,
        "last_365_success_rate_pct": 0.0,
    })
    out = out.sort_values(by=["last_365_success_rate_pct", "launches"], ascending=[False, False]).reset_index(drop=True)
    return out


def spacex_summary_by_rocket(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary of success counts and rates by rocket."""
    if df.empty:
        return df.copy()
    g = df.groupby("rocket").agg(
        launches=("id", "count"),
        successes=("success", lambda x: sum(1 for v in x if v is True)),
        failures=("success", lambda x: sum(1 for v in x if v is False))
    ).reset_index()
    g["success_rate_pct"] = (g["successes"] / g["launches"] * 100).round(1)
    return g


# -----------------------------
# CLI
# -----------------------------
# -----------------------------

def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 8 — REST APIs starter")
    p.add_argument("command", choices=["github", "weather", "todos", "owm", "spacex"], help="Which demo to run")
    p.add_argument("--org", help="GitHub org (for 'github' command)")
    p.add_argument("--user", help="GitHub user (for 'github' command)")
    p.add_argument("--limit", type=int, default=100, help="Max items to fetch (github/spacex)")

    p.add_argument("--lat", type=float, help="Latitude (for 'weather' or 'owm')")
    p.add_argument("--lon", type=float, help="Longitude (for 'weather' or 'owm')")
    p.add_argument("--hours", type=int, default=24, help="How many hours ahead (weather)")

    p.add_argument("--city", help="City name for OWM, e.g., 'Rome,IT' (for 'owm')")
    p.add_argument("--owm-key", dest="owm_key", help="OpenWeatherMap API key (optional; else read OWM_API_KEY env var)")

    # SpaceX options
    p.add_argument("--months", type=int, default=12, help="Months for recent window in spacex summary")
    p.add_argument("--success-only", action="store_true", help="For spacex: only include successful launches in raw output")

    # Output options
    p.add_argument("--csv", help="Path to write CSV (single-sheet output)")
    p.add_argument("--excel", help="Path to write Excel (multi-sheet when relevant)")
    p.add_argument("--sqlite", help="Path to write/replace tables in a SQLite DB (multi-table)")

    # Caching
    p.add_argument("--cache", action="store_true", help="Use requests-cache (if installed) to cache API responses for 10 minutes")

    p.add_argument("-v", "--verbose", action="store_true", help="Verbose logging; also prints whether auth is enabled")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_cli().parse_args(argv)
    # Choose cached vs normal session
    if args.cache:
        session, timeout_s = build_cached_session()
    else:
        session, timeout_s = build_session()
    client = HTTPClient(session=session, timeout_s=timeout_s, verbose=args.verbose)

    # Optional info line about auth when verbose
    if args.verbose:
        has_auth = "Authorization" in session.headers
        print(f"GitHub auth enabled: {has_auth}")

    if args.command == "github":
        if not (args.org or args.user) or (args.org and args.user):
            print("Provide exactly one of --org or --user", file=sys.stderr)
            return 2
        rows = github_list_repos(client, org=args.org, user=args.user, limit=args.limit)
        df = to_dataframe(rows)
        metrics = github_metrics(df)
        if args.csv:
            save_csv(df, args.csv)
            print(f"Saved {len(df)} rows to {args.csv}")
        if args.excel:
            save_excel({"github_repos": df, "github_metrics": metrics}, args.excel)
            print(f"Saved {len(df)} rows to {args.excel} [sheets: github_repos, github_metrics]")
        if not (args.csv or args.excel):
            print("Raw repos (top 10):")
            print(df.head(10).to_string(index=False))
            print("Metrics (top 10):")
            print(metrics.head(10).to_string(index=False))

    elif args.command == "weather":
        if args.lat is None or args.lon is None:
            print("--lat and --lon are required for weather", file=sys.stderr)
            return 2
        rows = open_meteo_forecast(client, args.lat, args.lon, hours=args.hours)
        df = to_dataframe(rows)
        if args.csv:
            save_csv(df, args.csv)
            print(f"Saved {len(df)} rows to {args.csv}")
        if args.excel:
            save_excel({"weather_hourly": df}, args.excel)
            print(f"Saved {len(df)} rows to {args.excel} [sheet: weather_hourly]")
        if not (args.csv or args.excel):
            print(df.head(24).to_string(index=False))

    elif args.command == "todos":
        rows = jsonplaceholder_todos(client)
        df = to_dataframe(rows)
        if args.csv:
            save_csv(df, args.csv)
            print(f"Saved {len(df)} rows to {args.csv}")
        if args.excel:
            save_excel({"todos": df}, args.excel)
            print(f"Saved {len(df)} rows to {args.excel} [sheet: todos]")
        if not (args.csv or args.excel):
            print(df.head(20).to_string(index=False))

    elif args.command == "owm":
        import os
        api_key = args.owm_key or os.environ.get("OWM_API_KEY")
        if not api_key:
            print("OpenWeatherMap API key not provided. Use --owm-key or set OWM_API_KEY env var.", file=sys.stderr)
            return 2
        try:
            rec = owm_current_weather(client, api_key=api_key, lat=args.lat, lon=args.lon, city=args.city)
        except requests.HTTPError as e:
            msg = str(e)
            if " 401 " in msg or "Invalid API key" in msg:
                print("⚠️ OpenWeatherMap returned 401: invalid or inactive API key. Keys can take time to activate. Try again later or regenerate.", file=sys.stderr)
                return 2
            raise
        df = pd.DataFrame([rec])
        if args.csv:
            save_csv(df, args.csv)
            print(f"Saved 1 row to {args.csv}")
        if args.excel:
            save_excel({"owm_current": df}, args.excel)
            print(f"Saved 1 row to {args.excel} [sheet: owm_current]")
        if not (args.csv or args.excel):
            print(df.to_string(index=False))

    elif args.command == "spacex":
        rows = spacex_recent_launches(client, limit=args.limit)
        df = to_dataframe(rows)
        if args.success_only:
            df = df[df["success"] == True]
        summary = spacex_summary(df, months=args.months)
        if args.csv:
            save_csv(df, args.csv)
            print(f"Saved {len(df)} rows to {args.csv}")
        if args.excel:
            save_excel({"spacex_launches": df, "spacex_summary": summary}, args.excel)
            print(f"Saved {len(df)} rows to {args.excel} [sheets: spacex_launches, spacex_summary]")
        if not (args.csv or args.excel):
            print("Recent launches (top 20):")
            print(df.head(20).to_string(index=False))
            print("Summary by rocket (top 10):")
            print(summary.head(10).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
