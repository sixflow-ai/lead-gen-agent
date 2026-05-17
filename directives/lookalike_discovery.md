---
name: lookalike-discovery
description: >
  Find companies similar to a seed list. Use when user says "find more companies
  like X" or "lookalike list" or provides a list of ideal customers.
scripts:
  - execution/apollo_search.py
  - execution/prospeo_search.py
  - execution/blitz_search.py
---

# Lookalike Company Discovery

## When to Use
- User provides example companies: "Find more like Acme Corp and Initech"
- User has a customer list and wants to find similar companies
- Account-based expansion

## Process

### Step 1: Analyze Seed Companies
For each seed company, identify:
- Industry / vertical
- Employee count range
- Geography
- Tech stack (if Apollo available)
- Business model (SaaS, agency, e-commerce, etc.)

### Step 2: Extract Common Patterns
Find the overlap:
- What industries do they share?
- What's the size range?
- What geographies are represented?
- Any common tech stack or keywords?

### Step 3: Build Search Criteria
Use the common patterns to construct searches:

**Via Apollo** (best for this — has similar company features):
```bash
python execution/apollo_search.py --industries "[common industries]" \
    --employee-count-min [min] --employee-count-max [max] \
    --titles "[target titles]" --limit 500
```

**Via Prospeo** (if Apollo unavailable):
```bash
python execution/prospeo_search.py --industries "[common industries]" \
    --company-size-min [min] --company-size-max [max] \
    --titles "[target titles]" --limit 500
```

### Step 4: Filter & Score
The scoring system in `score_leads.py` will automatically rank by ICP fit.
Lookalike leads should score high if the seed companies match the ICP.

## Tips
- Start with 3-5 seed companies for best pattern extraction
- Look at the seed companies' LinkedIn for industry tags
- If seeds are all in one niche, the lookalike will be very targeted
- If seeds are diverse, consider splitting into multiple searches
