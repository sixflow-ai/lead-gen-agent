"""Shared utilities for all execution scripts."""

import os
import json
import csv
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TMP_DIR = PROJECT_ROOT / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

CONFIG_DIR = PROJECT_ROOT / "config"


def load_profile():
    """Load the business profile / ICP config."""
    profile_path = CONFIG_DIR / "profile.yaml"
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found at {profile_path}. Copy config/profile.yaml and fill it in.")
    with open(profile_path) as f:
        return yaml.safe_load(f)


def get_env(key: str, required: bool = True) -> str:
    """Get an environment variable."""
    val = os.getenv(key, "")
    if required and not val:
        raise ValueError(f"Missing required env var: {key}. Add it to .env")
    return val


def save_leads_csv(leads: list[dict], filename: str) -> Path:
    """Save leads to a CSV in .tmp/. Returns the file path."""
    if not leads:
        print(f"No leads to save for {filename}")
        return None

    filepath = TMP_DIR / filename
    fieldnames = list(leads[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)
    print(f"Saved {len(leads)} leads to {filepath}")
    return filepath


def load_leads_csv(filepath: str | Path) -> list[dict]:
    """Load leads from a CSV file."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_json(data, filename: str) -> Path:
    """Save data as JSON in .tmp/."""
    filepath = TMP_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return filepath


def load_json(filepath: str | Path):
    """Load JSON from a file."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def dedupe_leads(leads: list[dict], key: str = "email") -> list[dict]:
    """Deduplicate leads by a given key field."""
    seen = set()
    unique = []
    for lead in leads:
        val = (lead.get(key) or "").strip().lower()
        if val and val not in seen:
            seen.add(val)
            unique.append(lead)
    removed = len(leads) - len(unique)
    if removed:
        print(f"Deduped: removed {removed} duplicates by '{key}'")
    return unique
