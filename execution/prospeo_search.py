"""
Prospeo Lead Search — Title-first B2B prospecting.

Searches Prospeo's database by job title, location, industry, and company size.
Returns contacts with emails. Supports pagination for large exports (25K+).

Usage:
    python execution/prospeo_search.py --titles "VP Marketing,Head of Growth" \
        --locations "United States" --limit 500

API docs: https://prospeo.io/api/documentation
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, save_leads_csv, TMP_DIR


PROSPEO_BASE = "https://api.prospeo.io"


def search_leads(
    titles: list[str],
    locations: list[str] = None,
    industries: list[str] = None,
    company_size_min: int = None,
    company_size_max: int = None,
    keywords: list[str] = None,
    limit: int = 500,
) -> list[dict]:
    """Search Prospeo for leads matching the given criteria.

    API: POST https://api.prospeo.io/search-person
    Pagination: 25 results/page, max 1000 pages (25K results per search)
    Rate limit: ~2-2.5 req/s (120-150 req/min). Uses 500ms delays.
    Credits: 1 credit per API request that returns results.
    """
    api_key = get_env("PROSPEO_API_KEY")
    headers = {"Content-Type": "application/json", "X-KEY": api_key}

    all_leads = []
    page = 1
    per_page = 25  # Prospeo returns 25 results per page (fixed)

    while len(all_leads) < limit:
        payload = {
            "titles": titles,
            "page": page,
        }
        if locations:
            # Prospeo location format: "State, United States #US"
            payload["locations"] = locations
        if industries:
            # Must match Prospeo's 256-name taxonomy exactly
            payload["industries"] = industries
        if company_size_min is not None:
            payload["company_headcount_min"] = company_size_min
        if company_size_max is not None:
            payload["company_headcount_max"] = company_size_max
        if keywords:
            payload["keywords"] = keywords

        print(f"Searching Prospeo page {page} (have {len(all_leads)} leads so far)...")
        resp = requests.post(f"{PROSPEO_BASE}/search-person", headers=headers, json=payload)

        if resp.status_code == 429:
            print("Rate limited. Waiting 60s...")
            time.sleep(60)
            continue

        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            break

        data = resp.json()
        results = data.get("response", {}).get("results", [])

        if not results:
            print(f"No more results at page {page}")
            break

        for r in results:
            lead = {
                "first_name": r.get("first_name", ""),
                "last_name": r.get("last_name", ""),
                "email": r.get("email", ""),
                "job_title": r.get("title", ""),
                "company": r.get("company_name", ""),
                "company_domain": r.get("company_domain", ""),
                "linkedin_url": r.get("linkedin_url", ""),
                "location": r.get("location", ""),
                "industry": r.get("industry", ""),
                "company_size": r.get("company_size", ""),
                "source": "prospeo",
            }
            all_leads.append(lead)

        page += 1
        total_available = data.get("response", {}).get("total", 0)
        if page > 1000 or page * per_page > total_available:
            break

        time.sleep(0.5)  # Rate limit: 2-2.5 req/s

    return all_leads[:limit]


def find_email(linkedin_url: str) -> dict:
    """Find email for a single LinkedIn profile URL."""
    api_key = get_env("PROSPEO_API_KEY")
    headers = {"Content-Type": "application/json", "X-KEY": api_key}

    resp = requests.post(
        f"{PROSPEO_BASE}/v1/linkedin-email-finder",
        headers=headers,
        json={"url": linkedin_url},
    )
    if resp.status_code != 200:
        return {"error": resp.text}

    data = resp.json().get("response", {})
    return {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "email": data.get("email", ""),
        "company": data.get("company_name", ""),
        "job_title": data.get("title", ""),
        "linkedin_url": linkedin_url,
        "source": "prospeo_linkedin",
    }


def domain_search(domain: str, limit: int = 50) -> list[dict]:
    """Find all contacts at a given company domain."""
    api_key = get_env("PROSPEO_API_KEY")
    headers = {"Content-Type": "application/json", "X-KEY": api_key}

    resp = requests.post(
        f"{PROSPEO_BASE}/v1/domain-search",
        headers=headers,
        json={"domain": domain, "limit": limit},
    )
    if resp.status_code != 200:
        print(f"Error searching domain {domain}: {resp.text}")
        return []

    results = resp.json().get("response", {}).get("results", [])
    leads = []
    for r in results:
        leads.append({
            "first_name": r.get("first_name", ""),
            "last_name": r.get("last_name", ""),
            "email": r.get("email", ""),
            "job_title": r.get("title", ""),
            "company": r.get("company_name", domain),
            "company_domain": domain,
            "linkedin_url": r.get("linkedin_url", ""),
            "source": "prospeo_domain",
        })
    return leads


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Prospeo for leads")
    parser.add_argument("--titles", required=True, help="Comma-separated job titles")
    parser.add_argument("--locations", default="", help="Comma-separated locations")
    parser.add_argument("--industries", default="", help="Comma-separated industries")
    parser.add_argument("--company-size-min", type=int, default=None)
    parser.add_argument("--company-size-max", type=int, default=None)
    parser.add_argument("--keywords", default="", help="Comma-separated keywords")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--output", default="prospeo_leads.csv")
    args = parser.parse_args()

    leads = search_leads(
        titles=[t.strip() for t in args.titles.split(",")],
        locations=[l.strip() for l in args.locations.split(",") if l.strip()] or None,
        industries=[i.strip() for i in args.industries.split(",") if i.strip()] or None,
        company_size_min=args.company_size_min,
        company_size_max=args.company_size_max,
        keywords=[k.strip() for k in args.keywords.split(",") if k.strip()] or None,
        limit=args.limit,
    )

    if leads:
        save_leads_csv(leads, args.output)
        print(f"Done. {len(leads)} leads exported.")
    else:
        print("No leads found. Try broadening your search criteria.")
