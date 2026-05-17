---
name: google-maps-zip-scrape
description: >
  Advanced Google Maps scraping across zip codes with concurrent threads.
  Use for large-scale local/SMB prospecting across entire states or regions.
  Much higher volume than basic Google Maps search.
scripts:
  - execution/google_maps_zip_scraper.py
  - execution/enrich_domains.py
  - execution/clean_leads.py
  - execution/score_leads.py
---

# Google Maps Zip Code Scraper

## When to Use
- Large-scale local business prospecting (hundreds to thousands of businesses)
- Targeting entire states or regions
- User says "find all [business type] in [state]"
- Need comprehensive coverage of a geography

## How It Differs from Basic Google Maps Search
- **Concurrent** — Uses multiple threads for speed (default: 5 workers)
- **Zip-code based** — Searches each zip code individually for thorough coverage
- **Rate limited** — Thread-safe sliding window rate limiter (10 req/s)
- **Review extraction** — Can optionally pull worst reviews (useful for personalization)
- **State-wide** — Can load all zip codes for a US state from bundled data

## Full Pipeline

### Step 1: Scrape by zip codes
```bash
# Entire state
python execution/google_maps_zip_scraper.py --query "dentist" --state TX --min-pop 5000

# Specific zips
python execution/google_maps_zip_scraper.py --query "marketing agency" --zips "90210,90401"

# With review extraction (for personalization)
python execution/google_maps_zip_scraper.py --query "restaurant" --state CA --reviews
```

### Step 2: Enrich with contacts
```bash
python execution/enrich_domains.py --input .tmp/gmaps_zip_leads.csv --output gmaps_enriched.csv --title-filter "Owner,CEO"
```

### Step 3: Clean and score
```bash
python execution/clean_leads.py --input .tmp/gmaps_enriched.csv --output gmaps_clean.csv
python execution/score_leads.py --input .tmp/gmaps_clean.csv --output gmaps_scored.csv
```

## Zip Code Data
The scraper can load zip codes from:
1. `data/us-zip-codes.csv` — Bundled dataset with state and population filters
2. Custom CSV file with a `zip` column
3. Comma-separated list via `--zips` flag

For the bundled dataset, use `--min-pop` to filter out very small zip codes and speed up scraping.

## Capacity
- ~10 requests/second with rate limiting
- Each zip code = 1-2 API calls (search + optional reviews)
- A state like TX has ~1,800 zip codes → ~6 minutes scrape time
- Filtering by min-pop 5000 reduces to ~400 zips → ~90 seconds

## Cost
- RapidAPI charges per request based on your subscription tier
- Check your plan limits before scraping an entire state
- Always ask the user to confirm scope before large scrapes
