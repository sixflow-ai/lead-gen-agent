---
name: apollo-lead-search
description: >
  Search Apollo.io for B2B leads with enriched company data.
  Use when you need technographics, funding data, or hiring signals.
scripts:
  - execution/apollo_search.py
---

# Apollo.io Lead Search

## When to Use
- Need enriched company data (tech stack, funding, hiring)
- Want Apollo's predefined industry/size filters
- Building account-based lists with deep firmographic data
- Complementing Prospeo for multi-source coverage

## Key Differences from Prospeo
- Better company-level data (tech stack, funding rounds, hiring intent)
- Predefined employee ranges (1-10, 11-50, 51-200, etc.)
- Industry taxonomy uses Apollo's tag IDs
- Rate limits are stricter (~100 requests/hour on free tier)

## Usage

```bash
# Standard search
python execution/apollo_search.py --titles "VP Marketing,CMO" --locations "United States" --limit 500

# With company filters
python execution/apollo_search.py --titles "CTO" --employee-count-min 50 --employee-count-max 500 --industries "SaaS" --limit 300
```

## Output
Same standardized CSV format as all other sources.
