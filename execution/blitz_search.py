"""
Blitz List Builder — Domain-to-contacts discovery.

Given a list of company domains, finds decision-maker contacts at each.
Useful when you have target companies but need to find the right people.

Usage:
    python execution/blitz_search.py --domains "acme.com,initech.com" --limit 50
    python execution/blitz_search.py --domains-file .tmp/domains.txt --limit 50
"""

import argparse
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, save_leads_csv, TMP_DIR


BLITZ_BASE = os.getenv("BLITZ_BASE_URL", "https://api.useblitz.com")


def find_contacts_for_domain(
    domain: str,
    titles: list[str] = None,
    limit: int = 10,
    api_key: str = None,
) -> list[dict]:
    """Find contacts at a specific domain via Blitz company enrichment.

    API: POST {BLITZ_BASE_URL}/api/enrichment/company
    Auth: Bearer token
    Response: { company: {...}, employees: [{first_name, last_name, title, email, ...}] }
    Retry: exponential backoff on 429/5xx, up to 4 attempts.
    """
    api_key = api_key or get_env("BLITZ_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Exponential backoff retry
    for attempt in range(4):
        resp = requests.post(
            f"{BLITZ_BASE}/api/enrichment/company",
            headers=headers,
            json={"domain": domain},
        )
        if resp.status_code == 429 or resp.status_code >= 500:
            wait = 1 * (2 ** attempt)
            print(f"Retrying {domain} in {wait}s (status {resp.status_code})...")
            time.sleep(wait)
            continue
        break

    if resp.status_code != 200:
        print(f"Error for {domain}: {resp.status_code} {resp.text[:200]}")
        return []

    data = resp.json()
    company = data.get("company", {}) or {}
    employees = data.get("employees", []) or []

    # Filter by title keywords if specified
    if titles:
        title_lower = [t.lower() for t in titles]
        matched = [e for e in employees if any(kw in (e.get("title") or "").lower() for kw in title_lower)]
        employees = matched if matched else employees[:limit]

    leads = []
    for e in employees[:limit]:
        leads.append({
            "first_name": e.get("first_name", ""),
            "last_name": e.get("last_name", ""),
            "email": e.get("email", ""),
            "job_title": e.get("title", ""),
            "company": company.get("name", ""),
            "company_domain": domain,
            "linkedin_url": e.get("linkedin_url", ""),
            "location": e.get("location", ""),
            "industry": company.get("industry", ""),
            "company_size": str(company.get("headcount", "")),
            "source": "blitz",
        })
    return leads


def bulk_domain_search(
    domains: list[str],
    titles: list[str] = None,
    contacts_per_domain: int = 5,
) -> list[dict]:
    """Search multiple domains for contacts."""
    api_key = get_env("BLITZ_API_KEY")
    all_leads = []

    for i, domain in enumerate(domains):
        domain = domain.strip()
        if not domain:
            continue
        print(f"[{i+1}/{len(domains)}] Searching {domain}...")
        leads = find_contacts_for_domain(domain, titles=titles, limit=contacts_per_domain, api_key=api_key)
        all_leads.extend(leads)
        if i < len(domains) - 1:
            time.sleep(0.5)

    return all_leads


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find contacts by company domain")
    parser.add_argument("--domains", default="", help="Comma-separated domains")
    parser.add_argument("--domains-file", default="", help="File with one domain per line")
    parser.add_argument("--titles", default="", help="Filter by job titles (comma-separated)")
    parser.add_argument("--contacts-per-domain", type=int, default=5)
    parser.add_argument("--output", default="blitz_leads.csv")
    args = parser.parse_args()

    domain_list = []
    if args.domains:
        domain_list = [d.strip() for d in args.domains.split(",") if d.strip()]
    elif args.domains_file:
        with open(args.domains_file) as f:
            domain_list = [line.strip() for line in f if line.strip()]

    if not domain_list:
        print("No domains provided. Use --domains or --domains-file")
        sys.exit(1)

    title_filter = [t.strip() for t in args.titles.split(",") if t.strip()] or None

    leads = bulk_domain_search(domain_list, titles=title_filter, contacts_per_domain=args.contacts_per_domain)

    if leads:
        save_leads_csv(leads, args.output)
        print(f"Done. {len(leads)} contacts found across {len(domain_list)} domains.")
    else:
        print("No contacts found.")
