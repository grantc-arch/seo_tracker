"""
Debug helper — shows the raw top results SerpApi returns for one keyword,
so you can see what Google is actually returning and why oldschoolsa.com
might not be matching.

Usage:
    set SERPAPI_KEY=your_key_here
    python debug_search.py "Old School SA"
"""

import os
import sys
import requests

SERPAPI_ENDPOINT = "https://serpapi.com/search"


def main():
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("ERROR: set the SERPAPI_KEY environment variable.")
        sys.exit(1)

    keyword = sys.argv[1] if len(sys.argv) > 1 else "Old School SA"

    params = {
        "engine": "google",
        "q": keyword,
        "location": "South Africa",
        "google_domain": "google.co.za",
        "gl": "za",
        "hl": "en",
        "api_key": api_key,
    }
    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    print(f"Keyword: {keyword}")
    print(f"Search metadata status: {data.get('search_metadata', {}).get('status')}")
    print(f"Search parameters used: {data.get('search_parameters')}")
    print()

    organic = data.get("organic_results", [])
    print(f"Found {len(organic)} organic results. Top 10:\n")
    for r in organic[:10]: