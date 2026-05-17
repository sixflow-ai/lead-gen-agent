---
name: verify-emails
description: >
  Verify email addresses using MillionVerifier before outreach.
  Use after cleaning/scoring, before export. Protects sender reputation.
scripts:
  - execution/verify_emails.py
---

# Verify Emails

## When to Use
- Before any email campaign
- After cleaning and scoring, as the final quality gate
- When user asks to "verify" or "validate" emails

## How It Works
- Calls MillionVerifier API for each email
- Keeps only emails with "ok" / "valid" status
- Removes invalid, disposable, catch-all risky addresses

## Usage
```bash
python execution/verify_emails.py --input .tmp/scored_leads.csv --output verified_leads.csv
```

## Cost Awareness
- MillionVerifier charges per verification
- For lists >500, consider using bulk upload endpoint
- Always verify AFTER deduplication to minimize cost
