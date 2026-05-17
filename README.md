# Lead Gen Agent

AI-powered lead generation agent that builds highly targeted lead lists. Give it an ICP and platform preferences — it asks smart clarifying questions, selects the optimal sourcing strategy, and outputs a clean, scored, deduplicated lead list.

## How It Works

1. **You describe your target** — job titles, industries, company size, geography
2. **The agent asks clarifying questions** — confirms ICP, recommends platforms, validates scope
3. **It runs the pipeline** — source leads → enrich → clean → dedupe → score → verify → export
4. **You get a clean list** — in Google Sheets or CSV, scored A/B/C/D against your ICP

## Supported Platforms

| Platform | Best For | API Key Env Var |
|----------|----------|-----------------|
| **Prospeo** | B2B title-based search (up to 25K+) | `PROSPEO_API_KEY` |
| **Apollo** | Enriched company data, technographics | `APOLLO_API_KEY` |
| **Google Maps** | Local/SMB businesses by location | `RAPIDAPI_KEY` |
| **Blitz** | Domain-to-contacts discovery | `BLITZ_API_KEY` |
| **MillionVerifier** | Email verification | `MILLIONVERIFIER_API_KEY` |

## Setup

```bash
# 1. Clone
git clone https://github.com/sixflow-ai/lead-gen-agent.git
cd lead-gen-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env with your API keys

# 4. Configure your ICP
# Edit config/profile.yaml with your business info and target audience

# 5. (Optional) Google Sheets export
# Place your Google OAuth credentials.json in config/
```

## Project Structure

```
config/
  profile.yaml        # Your business profile + ICP (fill this out first)
directives/            # SOPs — the agent reads these to know what to do
  build_lead_list.md   # Master orchestrator
  prospeo_lead_search.md
  apollo_lead_search.md
  google_maps_lead_search.md
  google_maps_zip_scrape.md
  blitz_domain_search.md
  lookalike_discovery.md
  competitor_engagers.md
  icp_onboarding.md
  icp_qualification.md
  clean_and_score_leads.md
  verify_emails.md
  export_leads.md
execution/             # Deterministic Python scripts
  prospeo_search.py
  apollo_search.py
  google_maps_search.py
  google_maps_zip_scraper.py
  blitz_search.py
  enrich_domains.py
  clean_leads.py
  score_leads.py
  verify_emails.py
  export_to_sheets.py
  utils.py
.tmp/                  # Intermediate files (auto-created, gitignored)
```

## Pipelines

The agent selects the best pipeline based on your request:

- **Title-Based B2B** — Prospeo/Apollo search for specific job titles
- **Local/SMB** — Google Maps scrape + contact enrichment
- **State-Wide Scrape** — Concurrent zip-code scraping for high volume
- **Account-Based** — Blitz domain search when you have target companies
- **Multi-Source** — Prospeo + Apollo merged and deduped
- **Lookalike** — Find companies similar to your best customers
- **Competitor Targeting** — Target audiences of specific competitors

## Lead Scoring

Every lead gets scored 0-100 against your ICP on 5 dimensions:
- **Completeness** (0-25): Data quality
- **Title Match** (0-30): Job title alignment
- **Industry Match** (0-20): Industry fit
- **Size Fit** (0-15): Company size range
- **Geography** (0-10): Location match

Grades: **A** (80+) | **B** (60-79) | **C** (40-59) | **D** (<40)