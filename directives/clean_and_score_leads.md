---
name: clean-and-score-leads
description: >
  Clean, deduplicate, and quality-score a lead list. Use after sourcing leads
  from any platform. Also handles merging multi-source lists.
scripts:
  - execution/clean_leads.py
  - execution/score_leads.py
---

# Clean and Score Leads

## When to Use
- After any lead sourcing step
- When merging leads from multiple platforms
- When user asks to "clean up" or "dedupe" a list
- Before exporting to Sheets or sending to a campaign tool

## Cleaning Pipeline

### What clean_leads.py does:
1. **Normalize**: Standardizes all fields (title case names, lowercase emails, clean domains)
2. **Validate emails**: Regex check for proper format
3. **Remove generics**: Strips info@, admin@, support@, etc.
4. **Deduplicate**: By email (default) or domain

### What score_leads.py does:
Scores each lead 0-100 across 5 dimensions against the ICP in `config/profile.yaml`:
- **Completeness** (0-25): How many fields are filled
- **Title match** (0-30): Does job title match ICP titles/seniority
- **Industry match** (0-20): Does industry match ICP
- **Size fit** (0-15): Is company size in ICP range
- **Geography** (0-10): Is location in target geos

Grades: A (80+), B (60-79), C (40-59), D (<40)

## Usage

```bash
# Clean a single file
python execution/clean_leads.py --input .tmp/raw.csv --output clean.csv

# Merge multiple sources
python execution/clean_leads.py --merge .tmp/prospeo.csv,.tmp/apollo.csv --output merged_clean.csv

# Score against ICP
python execution/score_leads.py --input .tmp/clean.csv --output scored.csv --min-grade B
```
