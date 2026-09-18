"""
SEO rank tracker for Old School (oldschoolsa.com)

Reads keywords.txt, checks Google ranking position for each keyword via
SerpApi, and appends one row per keyword per run to data/rankings.csv.

Usage:
    export SERPAPI_KEY=your_key_here
    python track_rankings.py

Designed to be run on a schedule (see .github/workflows/track.yml).
"""

import os
import csv
import sys
from datetime import datetime, timezone
import requests

TARGET_DOMAIN = "oldschool.co.za"
KEYWORDS_FILE = "keywords.txt"
OUTPUT_FILE = "data/rankings.csv"
SEARCH_LOCATION = "South Africa"
SERPAPI_ENDPOINT = "https://serpapi.com/search"


def load_keywords(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def find_domain_rank(results: dict, domain: str) -> tuple[int | None, str | None]:
    """Return (position, matched_url) for the first result whose link contains domain."""
    organic = results.get("organic_results", [])
    for r in organic:
        link = r.get("link", "")
        if domain in link:
            return r.get("position"), link
    return None, None


def check_keyword(keyword: str, api_key: str) -> dict:
    params = {
        "engine": "google",
        "q": keyword,
        "location": SEARCH_LOCATION,
        "google_domain": "google.co.za",
        "gl": "za",
        "hl": "en",
        "api_key": api_key,
    }
    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    position, url = find_domain_rank(data, TARGET_DOMAIN)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "keyword": keyword,
        "position": position if position is not None else "",
        "url": url or "",
        "found": position is not None,
    }


def append_rows(rows: list[dict], path: str):
    file_exists = os.path.isfile(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "keyword", "position", "url", "found"])
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("ERROR: set the SERPAPI_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    keywords = load_keywords(KEYWORDS_FILE)
    if not keywords:
        print("No keywords found in keywords.txt", file=sys.stderr)
        sys.exit(1)

    rows = []
    for kw in keywords:
        print(f"Checking: {kw}")
        try:
            row = check_keyword(kw, api_key)
            rows.append(row)
            pos_display = row["position"] if row["found"] else "not in top results"
            print(f"  -> position: {pos_display}")
        except Exception as e:
            print(f"  -> failed: {e}", file=sys.stderr)

    if rows:
        append_rows(rows, OUTPUT_FILE)
        print(f"Appended {len(rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
