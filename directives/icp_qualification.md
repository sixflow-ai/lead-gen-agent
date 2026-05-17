---
name: icp-qualification
description: >
  Build qualification prompts and filters for lead lists.
  Use when the user wants to tighten targeting or when list quality is low.
scripts:
  - execution/score_leads.py
---

# ICP Qualification

## When to Use
- Lead list has too many C/D grade leads
- User says "this list isn't targeted enough"
- Need to add additional filters post-scrape
- Building custom scoring criteria beyond the default

## Qualification Framework

### Tier 1: Must-Have (Hard Filters)
These eliminate leads entirely:
- Job title must match one of the ICP titles
- Company must be in target industry
- Company size must be in range
- Geography must match

### Tier 2: Should-Have (Scoring Boost)
These increase the score:
- Has LinkedIn URL (reachable via LinkedIn too)
- Has verified email
- Company domain found (not just a free email)
- Has phone number

### Tier 3: Nice-to-Have (Bonus Signals)
These indicate high intent:
- Company recently raised funding
- Hiring for relevant roles
- Using competitor tools
- High growth indicators

## Custom Scoring
If the default scoring in `score_leads.py` doesn't fit, you can:
1. Add custom scoring logic to the script
2. Post-process with Python to add custom fields
3. Filter the scored CSV manually (sort by score, cut at threshold)

## Output
A filtered, re-scored lead list with only leads meeting qualification criteria.
