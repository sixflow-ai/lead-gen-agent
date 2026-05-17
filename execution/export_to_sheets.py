"""
Google Sheets Export — Push final lead list to a Google Sheet.

Usage:
    python execution/export_to_sheets.py --input .tmp/scored_leads.csv \
        --sheet-id "1ABC..." --tab "Leads 2024-01"
"""

import argparse
import sys
from pathlib import Path

import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_leads_csv, get_env, CONFIG_DIR

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_google_creds() -> Credentials:
    """Get or refresh Google OAuth credentials."""
    creds_path = get_env("GOOGLE_CREDENTIALS_PATH", required=False) or str(CONFIG_DIR / "credentials.json")
    token_path = get_env("GOOGLE_TOKEN_PATH", required=False) or str(CONFIG_DIR / "token.json")

    creds = None
    token_file = Path(token_path)
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return creds


def export_to_sheet(
    leads: list[dict],
    sheet_id: str,
    tab_name: str = "Leads",
) -> str:
    """Export leads to a Google Sheet tab. Returns the sheet URL."""
    creds = get_google_creds()
    gc = gspread.authorize(creds)

    spreadsheet = gc.open_by_key(sheet_id)

    # Create or get the tab
    try:
        worksheet = spreadsheet.worksheet(tab_name)
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows=len(leads) + 1, cols=20)

    if not leads:
        print("No leads to export")
        return spreadsheet.url

    # Write headers + data
    headers = list(leads[0].keys())
    rows = [headers] + [[str(lead.get(h, "")) for h in headers] for lead in leads]
    worksheet.update(range_name="A1", values=rows)

    print(f"Exported {len(leads)} leads to sheet '{tab_name}'")
    return spreadsheet.url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export leads to Google Sheets")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--sheet-id", required=True, help="Google Sheet ID")
    parser.add_argument("--tab", default="Leads", help="Tab name")
    args = parser.parse_args()

    leads = load_leads_csv(args.input)
    print(f"Loaded {len(leads)} leads for export")

    url = export_to_sheet(leads, args.sheet_id, args.tab)
    print(f"Done. Sheet URL: {url}")
