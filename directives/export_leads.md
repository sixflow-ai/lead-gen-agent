---
name: export-leads
description: >
  Export final lead list to Google Sheets or CSV. Use as the final step
  in any lead generation pipeline.
scripts:
  - execution/export_to_sheets.py
---

# Export Leads

## When to Use
- Final step after cleaning, scoring, and optionally verifying
- User asks to "export", "save", or "put in a sheet"

## Google Sheets Export
```bash
python execution/export_to_sheets.py --input .tmp/final_leads.csv --sheet-id "SHEET_ID" --tab "Leads May 2024"
```

Requires Google OAuth credentials in `config/credentials.json`.

## CSV Export
All scripts already save to `.tmp/` as CSV. For a clean local export,
just copy the final CSV from `.tmp/` to the user's desired location.

## Best Practices
- Name the sheet tab with date and campaign context
- Include score columns so user can sort/filter in Sheets
- Provide the Sheet URL to the user after export
