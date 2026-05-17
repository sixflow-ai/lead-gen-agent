"""
Apollo.io Lead Search — B2B database with company + contact data.

Searches Apollo's people database by title, location, industry, company size.
Supports enrichment with technographics, funding data, etc.

Usage:
    python execution/apollo_search.py --titles "VP Marketing,CMO" \
        --locations "United States" --limit 500
"""

import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, save_leads_csv


APOLLO_BASE = "https://api.apollo.io"


def search_people(
    titles: list[str],
    locations: list[str] = None,
    industries: list[str] = None,
    employee_count_min: int = None,
    employee_count_max: int = None,
    keywords: list[str] = None,
    limit: int = 500,
) -> list[dict]:
    """Search Apollo for people matching criteria."""
    api_key = get_env("APOLLO_API_KEY")
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}

    all_leads = []
    page = 1
    per_page = min(limit, 100)

    # Map employee count to Apollo's ranges
    employee_ranges = []
    if employee_count_min is not None or employee_count_max is not None:
        # Apollo uses predefined ranges: 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+
        ranges = ["1,10", "11,50", "51,200", "201,500", "501,1000", "1001,5000", "5001,10000", "10001,"]
        for r in ranges:
            parts = r.split(",")
            low = int(parts[0])
            high = int(parts[1]) if parts[1] else 999999
            if (employee_count_min is None or high >= employee_count_min) and \
               (employee_count_max is None or low <= employee_count_max):
                employee_ranges.append(r)

    while len(all_leads) < limit:
        payload = {
            "person_titles": titles,
            "page": page,
            "per_page": per_page,
        }
        if locations:
            payload["person_locations"] = locations
        if industries:
            payload["organization_industry_tag_ids"] = industries
        if employee_ranges:
            payload["organization_num_employees_ranges"] = employee_ranges
        if keywords:
            payload["q_keywords"] = " ".join(keywords)

        print(f"Searching Apollo page {page} (have {len(all_leads)} leads)...")
        resp = requests.post(f"{APOLLO_BASE}/v1/mixed_people/search", headers=headers, json=payload)

        if resp.status_code == 429:
            print("Rate limited. Waiting 60s...")
            time.sleep(60)
            continue

        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            break

        data = resp.json()
        people = data.get("people", [])

        if not people:
            break

        for p in people:
            org = p.get("organization", {}) or {}
            lead = {
                "first_name": p.get("first_name", ""),
                "last_name": p.get("last_name", ""),
                "email": p.get("email", ""),
                "job_title": p.get("title", ""),
                "company": org.get("name", ""),
                "company_domain": org.get("primary_domain", ""),
                "linkedin_url": p.get("linkedin_url", ""),
                "location": f"{p.get('city', '')}, {p.get('state', '')}, {p.get('country', '')}".strip(", "),
                "industry": org.get("industry", ""),
                "company_size": org.get("estimated_num_employees", ""),
                "source": "apollo",
            }
            all_leads.append(lead)

        pagination = data.get("pagination", {})
        if page >= pagination.get("total_pages", 1):
            break

        page += 1
        time.sleep(1)

    return all_leads[:limit]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Apollo for leads")
    parser.add_argument("--titles", required=True, help="Comma-separated job titles")
    parser.add_argument("--locations", default="", help="Comma-separated locations")
    parser.add_argument("--industries", default="", help="Comma-separated industries")
    parser.add_argument("--employee-count-min", type=int, default=None)
    parser.add_argument("--employee-count-max", type=int, default=None)
    parser.add_argument("--keywords", default="", help="Comma-separated keywords")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--output", default="apollo_leads.csv")
    args = parser.parse_args()

    leads = search_people(
        titles=[t.strip() for t in args.titles.split(",")],
        locations=[l.strip() for l in args.locations.split(",") if l.strip()] or None,
        industries=[i.strip() for i in args.industries.split(",") if i.strip()] or None,
        employee_count_min=args.employee_count_min,
        employee_count_max=args.employee_count_max,
        keywords=[k.strip() for k in args.keywords.split(",") if k.strip()] or None,
        limit=args.limit,
    )

    if leads:
        save_leads_csv(leads, args.output)
        print(f"Done. {len(leads)} leads exported.")
    else:
        print("No leads found.")
