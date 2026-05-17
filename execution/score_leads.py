"""
Lead Quality Scoring — Multi-dimensional lead grading.

Scores each lead on completeness, ICP fit, and data quality.
Outputs a scored list sorted by quality.

Usage:
    python execution/score_leads.py --input .tmp/clean_leads.csv --output scored_leads.csv
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_leads_csv, save_leads_csv, load_profile


def score_lead(lead: dict, icp: dict) -> dict:
    """Score a single lead against ICP criteria. Returns lead with score fields added."""
    scores = {}

    # 1. Completeness (0-25 points)
    completeness = 0
    key_fields = ["first_name", "last_name", "email", "job_title", "company"]
    bonus_fields = ["company_domain", "linkedin_url", "phone", "location", "industry"]
    for f in key_fields:
        if lead.get(f, "").strip():
            completeness += 4
    for f in bonus_fields:
        if lead.get(f, "").strip():
            completeness += 1
    scores["completeness"] = min(completeness, 25)

    # 2. Title match (0-30 points)
    title_score = 0
    lead_title = (lead.get("job_title") or "").lower()
    icp_titles = [t.lower() for t in (icp.get("job_titles") or []) if t]
    icp_seniority = [s.lower() for s in (icp.get("seniority_levels") or []) if s]

    for target_title in icp_titles:
        if target_title in lead_title:
            title_score = 30
            break
    if title_score == 0:
        for level in icp_seniority:
            if level in lead_title:
                title_score = 20
                break
    if title_score == 0 and lead_title:
        # Partial credit for having a title at all
        title_score = 5
    scores["title_match"] = title_score

    # 3. Industry match (0-20 points)
    industry_score = 0
    lead_industry = (lead.get("industry") or "").lower()
    icp_industries = [i.lower() for i in (icp.get("industries") or []) if i]
    if lead_industry:
        for target_ind in icp_industries:
            if target_ind in lead_industry or lead_industry in target_ind:
                industry_score = 20
                break
        if industry_score == 0:
            industry_score = 5  # Has industry data but no match
    scores["industry_match"] = industry_score

    # 4. Company size fit (0-15 points)
    size_score = 0
    try:
        lead_size = int(str(lead.get("company_size", "0")).replace(",", "").split("-")[0])
        min_emp = icp.get("company_size", {}).get("min_employees", 0)
        max_emp = icp.get("company_size", {}).get("max_employees", 999999)
        if min_emp <= lead_size <= max_emp:
            size_score = 15
        elif lead_size > 0:
            size_score = 5  # Has size data but outside range
    except (ValueError, TypeError):
        pass
    scores["size_fit"] = size_score

    # 5. Geography match (0-10 points)
    geo_score = 0
    lead_location = (lead.get("location") or "").lower()
    icp_geos = [g.lower() for g in (icp.get("geographies") or []) if g]
    if lead_location:
        for geo in icp_geos:
            if geo in lead_location:
                geo_score = 10
                break
        if geo_score == 0:
            geo_score = 3
    scores["geo_match"] = geo_score

    # Total score
    total = sum(scores.values())
    lead["score_total"] = total
    lead["score_grade"] = "A" if total >= 80 else "B" if total >= 60 else "C" if total >= 40 else "D"
    lead["score_completeness"] = scores["completeness"]
    lead["score_title"] = scores["title_match"]
    lead["score_industry"] = scores["industry_match"]
    lead["score_size"] = scores["size_fit"]
    lead["score_geo"] = scores["geo_match"]

    return lead


def score_leads(leads: list[dict]) -> list[dict]:
    """Score all leads against the ICP from profile.yaml."""
    profile = load_profile()
    icp = profile.get("icp", {})

    scored = [score_lead(l, icp) for l in leads]
    scored.sort(key=lambda x: x.get("score_total", 0), reverse=True)

    # Print summary
    grades = {"A": 0, "B": 0, "C": 0, "D": 0}
    for l in scored:
        grades[l["score_grade"]] = grades.get(l["score_grade"], 0) + 1
    print(f"Scoring complete: A={grades['A']}, B={grades['B']}, C={grades['C']}, D={grades['D']}")

    return scored


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score leads against ICP")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", default="scored_leads.csv")
    parser.add_argument("--min-grade", default="D", choices=["A", "B", "C", "D"], help="Minimum grade to keep")
    args = parser.parse_args()

    leads = load_leads_csv(args.input)
    print(f"Loaded {len(leads)} leads for scoring")

    scored = score_leads(leads)

    grade_order = {"A": 4, "B": 3, "C": 2, "D": 1}
    min_val = grade_order[args.min_grade]
    filtered = [l for l in scored if grade_order.get(l.get("score_grade", "D"), 0) >= min_val]

    if filtered:
        save_leads_csv(filtered, args.output)
        print(f"Saved {len(filtered)} leads with grade >= {args.min_grade}")
    else:
        print("No leads met the minimum grade threshold.")
