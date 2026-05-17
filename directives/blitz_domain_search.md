---
name: blitz-domain-search
description: >
  Find contacts at specific company domains using Blitz.
  Use when you have a list of target companies (domains) and need to find
  the right people. Account-based approach.
scripts:
  - execution/blitz_search.py
---

# Blitz Domain Search

## When to Use
- User has a list of target company domains
- Account-based marketing: "find contacts at these 50 companies"
- Enriching a company list with decision-maker contacts
- Complementing Google Maps output (domains → contacts)

## Usage

```bash
# Direct domains
python execution/blitz_search.py --domains "acme.com,initech.com" --contacts-per-domain 5

# From a file (one domain per line)
python execution/blitz_search.py --domains-file .tmp/target_domains.txt --contacts-per-domain 3

# With title filter
python execution/blitz_search.py --domains "acme.com" --titles "VP Marketing,CMO" --contacts-per-domain 3
```

## Output
Standard CSV: first_name, last_name, email, job_title, company, company_domain, linkedin_url, location, source
