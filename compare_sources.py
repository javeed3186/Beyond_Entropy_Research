"""
Phase 1 source comparison -- GDELT vs Media Cloud.

Usage:
    python compare_sources.py
        -> compare E005 by default

    python compare_sources.py E005
        -> compare a specific event

Purpose:
    Compare story metadata collected from GDELT and Media Cloud
    for the same event and date window.

The comparison includes:
    - record counts
    - publisher/domain counts
    - normalized URL overlap
    - normalized title overlap
    - domain overlap
    - daily publication coverage
    - story-level match tables

This script does not claim that either source is more complete.
It only reports measurable overlap and coverage differences.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

RAW_GDELT_DIR = Path("data/raw/online")
RAW_MEDIACLOUD_DIR = Path("data/raw/online/mediacloud")
OUTPUT_DIR = Path("data/processed/source_comparison")


def normalize_url(url):
    """Normalize a URL for exact comparison."""

    if not url or pd.isna(url):
        return ""

    url = str(url).strip().lower()

    if not url:
        return ""

    parsed = urlparse(url)

    host = parsed.netloc.lower()

    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.rstrip("/")

    return f"{host}{path}"


def normalize_title(title):
    """Normalize a title for exact normalized-title comparison."""

    if not title or pd.isna(title):
        return ""

    title = str(title).lower()
    title = re.sub(r"[^\w\s]", " ", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


def extract_domain(url):
    """Extract publisher domain from a URL."""

    if not url or pd.isna(url):
        return ""

    try:
        host = urlparse(str(url)).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def load_gdelt(event_id):
    """Load GDELT event JSON."""

    path = RAW_GDELT_DIR / f"{event_id}_gdelt.json"

    print("Loading GDELT...")
    print(f"File: {path}")

    if not path.exists():
        raise FileNotFoundError(f"GDELT file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    rows = []

    for article in articles:
        url = article.get("url", "")
        rows.append(
            {
                "event_id": event_id,
                "title": article.get("title", ""),
                "url": url,
                "normalized_url": normalize_url(url),
                "normalized_title": normalize_title(article.get("title", "")),
                "domain": article.get("domain") or extract_domain(url),
                "publish_date": article.get("seendate", "")[:8] if article.get("seendate") else "",
                "source": "gdelt",
            }
        )

    return pd.DataFrame(rows)


def load_mediacloud(event_id):
    """Load the exact event-specific Media Cloud CSV."""

    path = RAW_MEDIACLOUD_DIR / f"{event_id}_mediacloud.csv"

    print()
    print("Loading Media Cloud...")
    print(f"File: {path}")

    if not path.exists():
        raise FileNotFoundError(f"Media Cloud file not found: {path}")

    df = pd.read_csv(path)
    rows = []

    for _, row in df.iterrows():
        url = row.get("url", "")
        publish_date = row.get("publish_date", "")

        if pd.isna(publish_date):
            publish_date = ""
        else:
            publish_date = str(publish_date)[:10]

        rows.append(
            {
                "event_id": event_id,
                "title": row.get("title", ""),
                "url": url,
                "normalized_url": normalize_url(url),
                "normalized_title": normalize_title(row.get("title", "")),
                "domain": row.get("media_url") or row.get("media_name") or extract_domain(url),
                "publish_date": publish_date,
                "source": "mediacloud",
            }
        )

    return pd.DataFrame(rows)


def domain_counts(df):
    """Return sorted domain counts."""

    if df.empty:
        return Counter()

    values = df["domain"].fillna("").astype(str).str.strip()
    values = values[values != ""]
    return Counter(values)


def calculate_overlap(gdelt, mediacloud):
    gdelt_urls = set(gdelt.loc[gdelt["normalized_url"] != "", "normalized_url"])
    mc_urls = set(mediacloud.loc[mediacloud["normalized_url"] != "", "normalized_url"])

    gdelt_titles = set(gdelt.loc[gdelt["normalized_title"] != "", "normalized_title"])
    mc_titles = set(mediacloud.loc[mediacloud["normalized_title"] != "", "normalized_title"])

    gdelt_domains = set(gdelt.loc[gdelt["domain"] != "", "domain"])
    mc_domains = set(mediacloud.loc[mediacloud["domain"] != "", "domain"])

    return {
        "url_overlap": gdelt_urls & mc_urls,
        "title_overlap": gdelt_titles & mc_titles,
        "domain_overlap": gdelt_domains & mc_domains,
    }


def make_daily_comparison(gdelt, mediacloud):
    gdelt_daily = gdelt.groupby("publish_date").size().rename("gdelt_count")
    mc_daily = mediacloud.groupby("publish_date").size().rename("mediacloud_count")
    daily = pd.concat([gdelt_daily, mc_daily], axis=1).fillna(0)
    daily["gdelt_count"] = daily["gdelt_count"].astype(int)
    daily["mediacloud_count"] = daily["mediacloud_count"].astype(int)
    return daily.reset_index().sort_values("publish_date")


def make_story_comparison(gdelt, mediacloud):
    mc_urls = set(mediacloud.loc[mediacloud["normalized_url"] != "", "normalized_url"])
    mc_titles = set(mediacloud.loc[mediacloud["normalized_title"] != "", "normalized_title"])

    gdelt_out = gdelt.copy()
    gdelt_out["url_match"] = gdelt_out["normalized_url"].isin(mc_urls)
    gdelt_out["title_match"] = gdelt_out["normalized_title"].isin(mc_titles)
    return gdelt_out


def build_summary(event_id, gdelt, mediacloud, overlap):
    gdelt_records = len(gdelt)
    mc_records = len(mediacloud)

    gdelt_domains = set(gdelt.loc[gdelt["domain"] != "", "domain"])
    mc_domains = set(mediacloud.loc[mediacloud["domain"] != "", "domain"])

    url_matches = len(overlap["url_overlap"])
    title_matches = len(overlap["title_overlap"])

    gdelt_url_percentage = (url_matches / gdelt_records * 100) if gdelt_records else 0
    mc_url_percentage = (url_matches / mc_records * 100) if mc_records else 0

    return pd.DataFrame(
        [
            {
                "event_id": event_id,
                "gdelt_records": gdelt_records,
                "mediacloud_records": mc_records,
                "gdelt_unique_domains": len(gdelt_domains),
                "mediacloud_unique_domains": len(mc_domains),
                "domain_overlap": len(overlap["domain_overlap"]),
                "url_overlap": url_matches,
                "normalized_title_overlap": title_matches,
                "gdelt_url_matches": url_matches,
                "mediacloud_url_matches": url_matches,
                "gdelt_title_matches": title_matches,
                "mediacloud_title_matches": title_matches,
                "gdelt_url_match_percentage": round(gdelt_url_percentage, 2),
                "mediacloud_url_match_percentage": round(mc_url_percentage, 2),
            }
        ]
    )


def main():
    event_id = sys.argv[1].strip().upper() if len(sys.argv) > 1 else "E005"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 70)
    print(f"SOURCE COMPARISON — {event_id}")
    print("=" * 70)

    gdelt = load_gdelt(event_id)
    mediacloud = load_mediacloud(event_id)

    print()
    print("-" * 70)
    print(f"GDELT records      : {len(gdelt)}")
    print(f"Media Cloud records: {len(mediacloud)}")

    overlap = calculate_overlap(gdelt, mediacloud)

    print()
    print("=" * 70)
    print("OVERLAP RESULTS")
    print("=" * 70)
    print(f"Exact normalized URL overlap : {len(overlap['url_overlap'])}")
    print(f"Normalized title overlap     : {len(overlap['title_overlap'])}")
    print(f"Domain overlap               : {len(overlap['domain_overlap'])}")

    print()
    print(f"GDELT URL matches             : {len(overlap['url_overlap'])}")
    print(f"Media Cloud URL matches       : {len(overlap['url_overlap'])}")

    print()
    print("=" * 70)
    print("GDELT DOMAINS")
    print("=" * 70)
    for domain, count in sorted(domain_counts(gdelt).items()):
        print(f"{domain}: {count}")

    print()
    print("=" * 70)
    print("MEDIA CLOUD DOMAINS")
    print("=" * 70)
    for domain, count in sorted(domain_counts(mediacloud).items()):
        print(f"{domain}: {count}")

    print()
    print("=" * 70)
    print("DOMAINS FOUND IN BOTH SOURCES")
    print("=" * 70)
    if overlap["domain_overlap"]:
        for domain in sorted(overlap["domain_overlap"]):
            print(domain)
    else:
        print("No overlapping publisher domains.")

    daily = make_daily_comparison(gdelt, mediacloud)

    print()
    print("=" * 70)
    print("DAILY COVERAGE")
    print("=" * 70)
    print(daily.to_string(index=False))

    story_comparison = make_story_comparison(gdelt, mediacloud)

    print()
    print("=" * 70)
    print("GDELT STORIES ALSO FOUND IN MEDIA CLOUD")
    print("=" * 70)
    matched_urls = story_comparison[story_comparison["url_match"]]
    if matched_urls.empty:
        print("No exact normalized URL matches.")
    else:
        print(matched_urls[["title", "domain", "url"]].to_string(index=False))

    print()
    print("=" * 70)
    print("GDELT STORIES WITH MATCHING NORMALIZED TITLE")
    print("=" * 70)
    matched_titles = story_comparison[story_comparison["title_match"]]
    if matched_titles.empty:
        print("No normalized title matches.")
    else:
        print(matched_titles[["title", "domain", "url"]].to_string(index=False))

    summary = build_summary(event_id, gdelt, mediacloud, overlap)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(summary.to_string(index=False))

    gdelt_output = OUTPUT_DIR / f"{event_id}_gdelt_comparison.csv"
    mc_output = OUTPUT_DIR / f"{event_id}_mediacloud_comparison.csv"
    daily_output = OUTPUT_DIR / f"{event_id}_daily_comparison.csv"
    summary_output = OUTPUT_DIR / f"{event_id}_source_comparison_summary.csv"

    story_comparison.to_csv(gdelt_output, index=False, encoding="utf-8")
    mediacloud.to_csv(mc_output, index=False, encoding="utf-8")
    daily.to_csv(daily_output, index=False, encoding="utf-8")
    summary.to_csv(summary_output, index=False, encoding="utf-8")

    print()
    print("=" * 70)
    print("OUTPUT FILES")
    print("=" * 70)
    print(f"GDELT comparison : {gdelt_output}")
    print(f"Media Cloud      : {mc_output}")
    print(f"Daily comparison : {daily_output}")
    print(f"Summary          : {summary_output}")

    print()
    print("Comparison completed successfully.")


if __name__ == "__main__":
    main()
