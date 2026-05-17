---
name: google-maps-lead-search
description: >
  Scrape Google Maps for local/SMB businesses. Use when targeting location-based
  businesses like agencies, restaurants, clinics, contractors, etc.
  Requires RapidAPI key. Outputs businesses that need contact enrichment.
scripts:
  - execution/google_maps_search.py
  - execution/enrich_domains.py
---

# Google Maps Lead Search

## When to Use
- Targeting local businesses (agencies, restaurants, clinics, salons, contractors)
- User specifies a business type + location (e.g., "dentists in Austin")
- Building SMB lists where company data matters more than titles
- Need business metadata: ratings, reviews, phone, address

## Full Pipeline
Google Maps gives you BUSINESSES, not contacts. You need to enrich afterwards.

```
Google Maps scrape → Extract domains → Enrich with Prospeo/Blitz → Clean → Score
```

### Step 1: Scrape
```bash
python execution/google_maps_search.py --query "marketing agency" --location "Austin, TX" --limit 200
```

### Step 2: Enrich with contacts
```bash
python execution/enrich_domains.py --input .tmp/gmaps_leads.csv --output gmaps_enriched.csv --title-filter "Owner,CEO,Founder" --contacts-per-domain 2
```

### Step 3: Clean and score
```bash
python execution/clean_leads.py --input .tmp/gmaps_enriched.csv --output gmaps_clean.csv
python execution/score_leads.py --input .tmp/gmaps_clean.csv --output gmaps_scored.csv
```

## Search Tips
- Be specific with location: "Austin, TX" > "Texas"
- Use business category terms Google Maps understands: "dentist", "marketing agency", "HVAC contractor"
- Rating/review filters can indicate business maturity (high reviews = established business)
- Businesses without websites are harder to enrich — consider filtering them out

## Output Fields
company, company_domain, phone, address, city, state, rating, review_count, category, google_maps_url, source
(+ contact fields after enrichment)

## Limitations
- RapidAPI plan limits (check your subscription tier)
- Max ~20 results per API call, paginated
- Some businesses have no website — these can't be enriched via domain search
