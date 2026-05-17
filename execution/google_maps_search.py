"""
Google Maps Lead Scraper — Local/SMB business discovery.

Scrapes Google Maps via RapidAPI for local businesses by keyword + location.
Great for targeting: agencies, restaurants, clinics, contractors, etc.

Usage:
    python execution/google_maps_search.py --query "marketing agency" \
        --location "Austin, TX" --limit 200
"""

import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, save_leads_csv


def search_google_maps(
    query: str,
    location: str = "",
    limit: int = 200,
) -> list[dict]:
    """Search Google Maps for businesses and extract lead data."""
    api_key = get_env("RAPIDAPI_KEY")

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "local-business-data.p.rapidapi.com",
    }

    all_leads = []
    offset = 0
    batch_size = 20  # API returns max 20 per call

    search_query = f"{query} {location}".strip() if location else query

    while len(all_leads) < limit:
        params = {
            "query": search_query,
            "limit": batch_size,
            "offset": offset,
            "zoom": 13,
            "language": "en",
            "region": "us",
        }

        print(f"Searching Google Maps offset={offset} (have {len(all_leads)} leads)...")
        resp = requests.get(
            "https://local-business-data.p.rapidapi.com/search",
            headers=headers,
            params=params,
        )

        if resp.status_code == 429:
            print("Rate limited. Waiting 30s...")
            time.sleep(30)
            continue

        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            break

        data = resp.json()
        businesses = data.get("data", [])

        if not businesses:
            break

        for biz in businesses:
            lead = {
                "company": biz.get("name", ""),
                "company_domain": (biz.get("website") or "").replace("https://", "").replace("http://", "").rstrip("/"),
                "phone": biz.get("phone_number", ""),
                "address": biz.get("full_address", ""),
                "city": biz.get("city", ""),
                "state": biz.get("state", ""),
                "rating": biz.get("rating", ""),
                "review_count": biz.get("review_count", ""),
                "category": biz.get("type", ""),
                "google_maps_url": biz.get("place_link", ""),
                "source": "google_maps",
                # These get filled in by enrichment step
                "first_name": "",
                "last_name": "",
                "email": "",
                "job_title": "",
            }
            all_leads.append(lead)

        offset += batch_size
        if len(businesses) < batch_size:
            break

        time.sleep(1)

    return all_leads[:limit]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Google Maps for local businesses")
    parser.add_argument("--query", required=True, help="Business type to search for")
    parser.add_argument("--location", default="", help="City/region to search in")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--output", default="gmaps_leads.csv")
    args = parser.parse_args()

    leads = search_google_maps(
        query=args.query,
        location=args.location,
        limit=args.limit,
    )

    if leads:
        save_leads_csv(leads, args.output)
        print(f"Done. {len(leads)} businesses found.")
    else:
        print("No businesses found.")
