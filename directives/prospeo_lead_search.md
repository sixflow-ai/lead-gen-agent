---
name: prospeo-lead-search
description: >
  Search Prospeo for B2B leads by job title, location, industry, and company size.
  Use when targeting specific decision-maker titles at scale (up to 25K+).
  Also supports domain search and LinkedIn email finder.
scripts:
  - execution/prospeo_search.py
---

# Prospeo Lead Search

## When to Use
- User wants B2B leads by job title (e.g., "VP of Marketing at SaaS companies")
- Need email addresses for specific LinkedIn profiles
- Have company domains and need to find who works there
- Building lists of 500-25,000+ leads

## API Capabilities

### 1. Lead Search (`search_leads`)
Title-first search with company filters. Best for broad prospecting.
- **Titles**: Job titles to target (array, supports multiple)
- **Locations**: Geographic filter (country, state, city)
- **Industries**: Industry filter
- **Company size**: Min/max employee count
- **Keywords**: Additional search terms
- **Pagination**: 100 per page, supports deep pagination

### 2. Domain Search (`domain_search`)
Find all contacts at a specific company domain.
- Input: company domain (e.g., "acme.com")
- Returns: all known contacts with emails

### 3. LinkedIn Email Finder (`find_email`)
Find email for a specific LinkedIn profile URL.
- Input: LinkedIn profile URL
- Returns: verified email + contact details

## Usage Examples

```bash
# Basic title search
python execution/prospeo_search.py --titles "VP Marketing,Head of Growth" --locations "United States" --limit 500

# With industry and size filters
python execution/prospeo_search.py --titles "CTO,VP Engineering" --industries "SaaS,Software" --company-size-min 50 --company-size-max 500 --limit 1000

# Narrow geographic search
python execution/prospeo_search.py --titles "CEO,Founder" --locations "San Francisco,New York" --limit 200
```

## Rate Limits & Credits
- Each search page costs credits based on results returned
- Rate limit: ~60 requests/minute. Script auto-waits on 429.
- Domain search: 1 credit per domain
- LinkedIn finder: 1 credit per lookup

## Output Format
CSV with columns: first_name, last_name, email, job_title, company, company_domain, linkedin_url, location, industry, company_size, source

## Tips
- Use multiple title variations: "VP Marketing" + "Vice President of Marketing" + "VP of Marketing"
- Broader searches = more results but lower ICP fit. Use scoring to filter after.
- Combine with Apollo for maximum coverage, then dedupe
