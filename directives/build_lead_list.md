---
name: build-lead-list
description: >
  Master orchestrator for building targeted lead lists. Use when user says
  "build a list", "find leads", "get me contacts", or any lead generation request.
  Always starts by asking clarifying questions before executing.
scripts:
  - execution/prospeo_search.py
  - execution/apollo_search.py
  - execution/google_maps_search.py
  - execution/blitz_search.py
  - execution/enrich_domains.py
  - execution/clean_leads.py
  - execution/score_leads.py
  - execution/verify_emails.py
  - execution/export_to_sheets.py
---

# Build Lead List — Master Orchestrator

## Overview

This is the primary workflow. User gives you an ICP (or you read it from `config/profile.yaml`), you figure out the best platform(s) and strategy, then execute the full pipeline: source → enrich → clean → score → verify → export.

## Step 0: Read Profile

Before anything else, read `config/profile.yaml` to understand:
- Who the user is (business context)
- Their default ICP (titles, industries, geos, company size)
- Which platforms are enabled (have API keys)
- Output preferences

## Step 1: Clarifying Questions

**ALWAYS ask before building.** Never just start scraping. Ask:

1. **ICP Confirmation**: "Your profile targets [titles] at [industries] companies with [size] employees in [geos]. Is this still the target, or do you want to adjust for this run?"

2. **Volume**: "How many leads do you need? (e.g., 200 for a test, 1000 for a full campaign)"

3. **Platform Selection**: Based on enabled platforms and the ICP, recommend the best approach:
   - **Prospeo** → Best for B2B title-based search at scale. Use when targeting specific job titles at companies matching firmographic filters.
   - **Apollo** → Best when you need enriched data (technographics, funding, hiring). Good for sophisticated ICP filtering.
   - **Google Maps** → Best for local/SMB (restaurants, agencies, clinics, contractors). Searches by business type + location.
   - **Blitz** → Best when you already have a list of target company domains and need to find contacts there.
   - **Multi-platform** → For maximum coverage, use Prospeo + Apollo, then dedupe. Or Google Maps → Enrich with Prospeo.

4. **Special Requirements**: "Any specific companies to include/exclude? Keywords? Recent funding? Hiring signals?"

## Step 2: Strategy Selection

Based on answers, pick the pipeline:

### Pipeline A: Title-Based Search (B2B)
Best for: "Find me VPs of Marketing at SaaS companies"
```
Prospeo/Apollo search → Clean → Score → Verify → Export
```

### Pipeline B: Local/SMB Discovery
Best for: "Find me dentists in Austin" or "marketing agencies in California"
```
Google Maps search → Enrich domains (Prospeo) → Clean → Score → Verify → Export
```

### Pipeline C: Account-Based (Domain List)
Best for: "Find contacts at these 50 companies"
```
Blitz domain search → Clean → Score → Verify → Export
```

### Pipeline D: Multi-Source Merge
Best for: Maximum coverage, large campaigns
```
Prospeo search + Apollo search → Merge & dedupe → Clean → Score → Verify → Export
```

### Pipeline E: Google Maps + Title Filter
Best for: "Find owners of [business type] in [location]"
```
Google Maps search → Enrich with title filter → Clean → Score → Export
```

### Pipeline F: State-Wide Zip Code Scrape
Best for: "Find all [business type] in [state]" — large-scale local prospecting
```
Google Maps Zip Scraper (concurrent) → Enrich domains → Clean → Score → Export
```

### Pipeline G: Lookalike Discovery
Best for: "Find companies like my best customers"
```
Analyze seed companies → Extract patterns → Search Apollo/Prospeo → Clean → Score → Export
```

### Pipeline H: Competitor Targeting
Best for: "Target people who use [competitor]"
```
Keyword search (competitor names) → Filter by ICP titles → Clean → Score → Export
```

## Step 3: Execute Pipeline

Run each script in order. Between steps:
- Check the output count and sample a few rows
- If a step produces 0 results, investigate before continuing
- Report progress to the user at each stage

### Source Phase
Run the appropriate search script(s):
```bash
# B2B title search
python execution/prospeo_search.py --titles "VP Marketing,CMO" --locations "United States" --limit 500 --output prospeo_raw.csv
python execution/apollo_search.py --titles "VP Marketing,CMO" --locations "United States" --limit 500 --output apollo_raw.csv

# Local business search (basic)
python execution/google_maps_search.py --query "marketing agency" --location "Austin TX" --limit 200 --output gmaps_raw.csv

# Local business search (advanced — state-wide zip scrape)
python execution/google_maps_zip_scraper.py --query "dentist" --state TX --min-pop 5000 --output gmaps_zip_raw.csv

# Domain-to-contacts
python execution/blitz_search.py --domains "acme.com,initech.com" --output blitz_raw.csv
```

### Enrich Phase (if needed)
For Google Maps leads that lack contacts:
```bash
python execution/enrich_domains.py --input .tmp/gmaps_raw.csv --output gmaps_enriched.csv --title-filter "Owner,CEO,Founder"
```

### Clean Phase
Merge and clean all sources:
```bash
python execution/clean_leads.py --merge .tmp/prospeo_raw.csv,.tmp/apollo_raw.csv --output clean_leads.csv
```

### Score Phase
```bash
python execution/score_leads.py --input .tmp/clean_leads.csv --output scored_leads.csv --min-grade C
```

### Verify Phase (if MillionVerifier enabled)
```bash
python execution/verify_emails.py --input .tmp/scored_leads.csv --output verified_leads.csv
```

### Export Phase
```bash
python execution/export_to_sheets.py --input .tmp/verified_leads.csv --sheet-id "SHEET_ID" --tab "Leads May 2024"
```

## Step 4: Report

After export, give the user a summary:
- Total leads exported
- Grade distribution (A/B/C/D)
- Source breakdown (how many from each platform)
- Top 5 sample leads
- Any issues or recommendations

## Edge Cases & Learnings

- If Prospeo returns 0 results, try broadening titles (add synonyms) or removing industry filter
- If Apollo rate limits, wait 60s and retry. Max ~500 leads per session recommended.
- Google Maps is limited by location specificity. "Austin TX" works better than "Texas"
- Always dedupe before scoring — duplicate leads across platforms are common
- For campaigns >1000 leads, consider running in batches of 500
