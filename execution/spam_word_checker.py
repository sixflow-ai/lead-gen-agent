"""
Spam Word Checker — Scan cold email copy for deliverability issues.

Checks subject lines, body copy, and CTAs against a comprehensive list
of spam triggers, banned phrases, and formatting issues.

Usage:
    python execution/spam_word_checker.py --input .tmp/email_copy.md
    python execution/spam_word_checker.py --text "Act now! Free consultation available!!!"
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import TMP_DIR


# Banned single words (in subject or body)
BANNED_WORDS = {
    "get", "bank", "credit", "access", "open", "compare", "problem", "now",
    "billing", "deal", "finance", "free", "bonus", "guarantee", "winner",
    "prize", "cash", "earn", "income", "profit", "urgent", "expires",
    "discount", "offer", "save", "cheap", "bargain", "lowest", "affordable",
}

# Banned phrases
BANNED_PHRASES = [
    "act now", "limited time", "click here", "risk-free", "no obligation",
    "earn money", "make money", "work from home", "be your own boss",
    "double your", "increase your", "million dollars", "once in a lifetime",
    "order now", "buy now", "sign up free", "no cost", "no fees",
    "100% free", "100% satisfied", "apply now", "call now",
    "congratulations", "dear friend", "for free", "great offer",
    "incredible deal", "info you requested", "limited offer",
    "no purchase necessary", "not spam", "please read",
    "special promotion", "this isn't spam", "unbelievable",
    "what are you waiting for", "while supplies last", "you are selected",
    "you have been selected", "your income",
    # Cold email specific
    "off chance", "one time", "circle back", "bumping this once",
    "just checking in", "following up on my last", "hope this finds you",
    "i hope this email", "touching base", "per my last email",
    "as per our conversation", "i wanted to reach out",
    "i came across your", "i stumbled upon",
    # Phishing-style
    "access your account", "verify identity", "final notice",
    "password reset", "confirm your identity", "account suspended",
    "verify your account", "security alert",
    # Spam categories
    "lose weight", "weight loss", "diet", "viagra", "cialis",
    "online casino", "poker", "lottery",
]

# Formatting issues
FORMAT_ISSUES = {
    "em_dash": r"—",
    "all_caps_word": r"\b[A-Z]{4,}\b",  # Words with 4+ capital letters
    "multiple_exclamation": r"!{2,}",
    "multiple_question": r"\?{2,}",
    "dollar_amount": r"\$\d+",
    "percentage_claim": r"\d+%\s*(off|discount|increase|growth|more)",
}


def check_text(text: str) -> dict:
    """Check text for spam issues. Returns dict with findings."""
    issues = []
    warnings = []
    text_lower = text.lower()

    # Check banned words (only flag if they appear in suspicious context)
    for word in BANNED_WORDS:
        # Look for the word as a standalone word
        pattern = r'\b' + re.escape(word) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            issues.append(f"Banned word: '{word}' (found {len(matches)}x)")

    # Check banned phrases
    for phrase in BANNED_PHRASES:
        if phrase in text_lower:
            issues.append(f"Banned phrase: '{phrase}'")

    # Check formatting issues
    for name, pattern in FORMAT_ISSUES.items():
        matches = re.findall(pattern, text)
        if matches:
            label = name.replace("_", " ").title()
            if name == "em_dash":
                issues.append(f"{label}: Use periods or commas instead of em dashes")
            elif name == "all_caps_word":
                # Filter out common abbreviations
                real_caps = [m for m in matches if m not in {"HTML", "CSS", "API", "CEO", "CTO", "VP", "CFO", "CMO", "COO", "SaaS", "B2B", "B2C", "ROI", "KPI", "CRM", "SEO", "PPC", "AI", "ML"}]
                if real_caps:
                    warnings.append(f"{label}: {', '.join(real_caps[:3])} — avoid ALL CAPS")
            elif name == "dollar_amount":
                warnings.append(f"{label}: Dollar amounts can trigger filters")
            else:
                issues.append(f"{label}: {', '.join(matches[:3])}")

    # Check recipient:sender ratio (rough heuristic)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sender_words = {"i ", "i'm", "i've", "we ", "we're", "we've", "our ", "my "}
    recipient_words = {"you ", "you're", "you've", "your ", "they ", "their "}
    sender_count = sum(1 for s in sentences if any(w in s.lower() + " " for w in sender_words))
    recipient_count = sum(1 for s in sentences if any(w in s.lower() + " " for w in recipient_words))
    if sender_count > 0 and recipient_count / max(sender_count, 1) < 2:
        warnings.append(f"Sender:recipient ratio is low ({recipient_count}:{sender_count}). Aim for 3:1 about-them-to-about-you.")

    # Check word count
    word_count = len(text.split())
    if word_count > 125:
        warnings.append(f"Word count: {word_count} — target 50-90 words, max 125")
    elif word_count > 90:
        warnings.append(f"Word count: {word_count} — slightly long, target 50-90")

    # Check unsubscribe line issues
    if "if i don't hear" in text_lower or "if you don't respond" in text_lower:
        issues.append("Bad unsubscribe: Don't promise to stop based on silence. Only explicit opt-out should stop sequences.")

    # Score
    score = max(0, 100 - (len(issues) * 10) - (len(warnings) * 3))
    grade = "PASS" if score >= 85 else "REVIEW" if score >= 70 else "FAIL"

    return {
        "score": score,
        "grade": grade,
        "issues": issues,
        "warnings": warnings,
        "word_count": word_count,
    }


def check_file(filepath: str) -> dict:
    """Check an entire file for spam issues."""
    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    # Split by email sections if possible (look for "Subject:" or "---" dividers)
    sections = re.split(r'\n---+\n|\n#{1,3}\s+(?:Email|Step|Follow)', text)

    all_results = []
    for i, section in enumerate(sections):
        section = section.strip()
        if not section or len(section) < 20:
            continue
        result = check_text(section)
        result["section"] = i + 1
        all_results.append(result)

    return {
        "sections": all_results,
        "total_issues": sum(len(r["issues"]) for r in all_results),
        "total_warnings": sum(len(r["warnings"]) for r in all_results),
        "overall_grade": "FAIL" if any(r["grade"] == "FAIL" for r in all_results)
                         else "REVIEW" if any(r["grade"] == "REVIEW" for r in all_results)
                         else "PASS",
    }


def print_results(results: dict):
    """Pretty-print spam check results."""
    if "sections" in results:
        print(f"\n{'='*60}")
        print(f"SPAM CHECK RESULTS — Overall: {results['overall_grade']}")
        print(f"Issues: {results['total_issues']} | Warnings: {results['total_warnings']}")
        print(f"{'='*60}\n")

        for r in results["sections"]:
            print(f"--- Section {r['section']} (Score: {r['score']}, {r['grade']}, {r['word_count']} words) ---")
            for issue in r["issues"]:
                print(f"  [ISSUE] {issue}")
            for warning in r["warnings"]:
                print(f"  [WARN]  {warning}")
            if not r["issues"] and not r["warnings"]:
                print("  Clean!")
            print()
    else:
        print(f"\nScore: {results['score']} ({results['grade']})")
        print(f"Word count: {results['word_count']}")
        for issue in results["issues"]:
            print(f"  [ISSUE] {issue}")
        for warning in results["warnings"]:
            print(f"  [WARN]  {warning}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check cold email copy for spam triggers")
    parser.add_argument("--input", help="File to check")
    parser.add_argument("--text", help="Text to check directly")
    args = parser.parse_args()

    if args.input:
        results = check_file(args.input)
        print_results(results)
    elif args.text:
        results = check_text(args.text)
        print_results(results)
    else:
        print("Provide --input or --text")
        sys.exit(1)
