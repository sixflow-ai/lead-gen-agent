"""
Google Maps Zip Code Scraper — Advanced local business discovery.

Scrapes Google Maps across multiple zip codes with concurrent threads,
rate limiting, and optional bad review extraction. Based on patterns from
growthenginenowoslawski/google-maps-scraper.

Usage:
    # Search a state
    python execution/google_maps_zip_scraper.py --query "dentist" --state TX --min-pop 5000

    # Search specific zips
    python execution/google_maps_zip_scraper.py --query "marketing agency" --zips "90210,90401,91101"

    # Search from a file
    python execution/google_maps_zip_scraper.py --query "plumber" --file .tmp/target_zips.csv
"""

import argparse
import csv
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_env, save_leads_csv, TMP_DIR, PROJECT_ROOT


class RateLimiter:
    """Thread-safe sliding window rate limiter."""

    def __init__(self, max_per_second: float = 10.0):
        self.max_requests = max_per_second
        self.lock = threading.Lock()
        self.request_times = []

    def wait(self):
        with self.lock:
            now = time.time()
            self.request_times = [t for t in self.request_times if now - t < 1.0]
            if len(self.request_times) >= self.max_requests:
                oldest = min(self.request_times)
                wait_time = 1.0 - (now - oldest) + 0.01
                if wait_time > 0:
                    time.sleep(wait_time)
            self.request_times.append(time.time())


class GoogleMapsZipScraper:
    """Concurrent Google Maps scraper across zip codes."""

    def __init__(self, api_key: str, max_workers: int = 5):
        self.api_key = api_key
        self.base_url = "https://google-maps-extractor2.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-host": "google-maps-extractor2.p.rapidapi.com",
            "x-rapidapi-key": api_key,
        }
        self.results = []
        self.results_lock = threading.Lock()
        self.rate_limiter = RateLimiter(max_per_second=10.0)
        self.max_workers = max_workers

    def search_location(self, query: str, limit: int = 20) -> list[dict]:
        """Search for businesses at a location."""
        self.rate_limiter.wait()
        try:
            resp = requests.get(
                f"{self.base_url}/locate_and_search",
                headers=self.headers,
                params={"query": query, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
            return []

    def get_bad_review(self, business_id: str) -> dict | None:
        """Get the worst review for a business."""
        self.rate_limiter.wait()
        try:
            resp = requests.get(
                f"{self.base_url}/business_reviews",
                headers=self.headers,
                params={"business_id": business_id, "limit": 20},
            )
            resp.raise_for_status()
            reviews = resp.json().get("data", [])
            if reviews:
                worst = sorted(reviews, key=lambda x: x.get("rating", 5))[0]
                return {
                    "text": worst.get("text", ""),
                    "rating": worst.get("rating", ""),
                    "date": worst.get("time", ""),
                }
        except requests.exceptions.RequestException:
            pass
        return None

    def _process_zip(self, query: str, zip_code: str, idx: int, total: int, fetch_reviews: bool) -> list[dict]:
        """Process a single zip code."""
        full_query = f"{query} in {zip_code}"
        businesses = self.search_location(full_query)

        if businesses:
            print(f"[{idx}/{total}] {zip_code}: {len(businesses)} businesses")
        else:
            print(f"[{idx}/{total}] {zip_code}: 0 businesses")
            return []

        results = []
        for biz in businesses:
            # Extract domain
            website = biz.get("website_domain") or biz.get("website") or biz.get("url") or ""
            if website.startswith("http"):
                try:
                    website = urlparse(website).netloc
                except Exception:
                    pass

            result = {
                "company": biz.get("name", ""),
                "company_domain": website.replace("www.", "").rstrip("/"),
                "phone": biz.get("phone") or biz.get("full_phone", ""),
                "address": biz.get("address", ""),
                "rating": biz.get("rating", ""),
                "review_count": biz.get("reviews_count", ""),
                "category": biz.get("type", ""),
                "zip_code": zip_code,
                "google_id": biz.get("google_id", ""),
                "source": "google_maps_zip",
                "first_name": "",
                "last_name": "",
                "email": "",
                "job_title": "",
            }

            # Optionally fetch bad reviews (useful for personalization)
            if fetch_reviews and result["google_id"]:
                review = self.get_bad_review(result["google_id"])
                if review:
                    result["worst_review_text"] = review["text"]
                    result["worst_review_rating"] = review["rating"]

            results.append(result)
        return results

    def scrape(
        self,
        query: str,
        zip_codes: list[str],
        fetch_reviews: bool = False,
    ) -> list[dict]:
        """Scrape businesses across all zip codes concurrently."""
        print(f"Scraping '{query}' across {len(zip_codes)} zip codes ({self.max_workers} workers)...")
        start = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_zip, query, z, i + 1, len(zip_codes), fetch_reviews): z
                for i, z in enumerate(zip_codes)
            }
            for future in as_completed(futures):
                try:
                    batch = future.result()
                    with self.results_lock:
                        self.results.extend(batch)
                except Exception as e:
                    print(f"  Error: {e}")

        elapsed = time.time() - start
        print(f"Done: {len(self.results)} businesses in {elapsed:.0f}s")
        return self.results


def load_bundled_zips(state: str = None, min_pop: int = 0) -> list[str]:
    """Load zip codes from bundled data file, optionally filtered by state/population."""
    zip_file = PROJECT_ROOT / "data" / "us-zip-codes.csv"
    if not zip_file.exists():
        print(f"Bundled zip file not found at {zip_file}")
        print("You can provide zips via --zips or --file instead.")
        return []

    zips = []
    with open(zip_file, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if state and row.get("state", "").upper() != state.upper():
                continue
            try:
                pop = int(row.get("irs_estimated_population", 0))
            except (ValueError, TypeError):
                pop = 0
            if min_pop > 0 and pop < min_pop:
                continue
            z = row.get("zip", "").strip()
            if z:
                zips.append(z.zfill(5))
    return zips


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Google Maps across zip codes")
    parser.add_argument("--query", "-q", required=True, help="Business type to search")
    parser.add_argument("--state", "-s", help="2-letter US state code")
    parser.add_argument("--zips", "-z", help="Comma-separated zip codes")
    parser.add_argument("--file", "-f", help="CSV file with 'zip' column")
    parser.add_argument("--min-pop", type=int, default=0, help="Minimum zip population (with --state)")
    parser.add_argument("--workers", "-w", type=int, default=5, help="Concurrent threads")
    parser.add_argument("--reviews", action="store_true", help="Also fetch worst review per business")
    parser.add_argument("--output", "-o", default="gmaps_zip_leads.csv")
    args = parser.parse_args()

    api_key = get_env("RAPIDAPI_KEY")
    zip_codes = []

    if args.zips:
        zip_codes = [z.strip().zfill(5) for z in args.zips.split(",") if z.strip()]
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            zip_codes = [row.get("zip", "").strip().zfill(5) for row in reader if row.get("zip", "").strip()]
    elif args.state:
        zip_codes = load_bundled_zips(state=args.state, min_pop=args.min_pop)

    if not zip_codes:
        print("No zip codes. Use --state, --zips, or --file.")
        sys.exit(1)

    print(f"Loaded {len(zip_codes)} zip codes")

    scraper = GoogleMapsZipScraper(api_key, max_workers=args.workers)
    leads = scraper.scrape(args.query, zip_codes, fetch_reviews=args.reviews)

    if leads:
        save_leads_csv(leads, args.output)
        print(f"Exported {len(leads)} businesses to .tmp/{args.output}")
    else:
        print("No businesses found.")
