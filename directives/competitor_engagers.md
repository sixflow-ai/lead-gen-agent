---
name: competitor-engagers
description: >
  Find people engaging with competitor content on LinkedIn.
  Use when user says "target competitor's audience" or "people who follow X".
scripts:
  - execution/prospeo_search.py
  - execution/apollo_search.py
---

# Competitor Engagers

## When to Use
- User wants to target people engaging with a competitor's content
- "Find people who follow [competitor] on LinkedIn"
- Stealing share from specific competitors

## Process

### Step 1: Identify Competitors
Ask the user:
- "Who are your main competitors?"
- "Any specific competitor content or LinkedIn pages to target?"

### Step 2: Build Keyword Search
Use competitor names, product names, and related terms as keywords:

```bash
python execution/apollo_search.py \
    --titles "VP Marketing,CMO,Head of Growth" \
    --keywords "competitor_name,competitor_product" \
    --limit 500
```

### Step 3: Domain-Based Discovery
If you know competitor customer domains (from case studies, reviews, etc.):

```bash
python execution/blitz_search.py \
    --domains "customer1.com,customer2.com" \
    --titles "VP Marketing" \
    --contacts-per-domain 3
```

## Alternative: Manual LinkedIn Approach
If API-based approaches don't yield enough results, suggest the user:
1. Go to the competitor's LinkedIn company page
2. Look at followers / people who engage with posts
3. Export those profiles for email finding via Prospeo's LinkedIn finder

## Limitations
- LinkedIn doesn't expose engagement data via APIs easily
- This is best used as a keyword/company-based proxy
- Combine with other sources for best coverage
