"""
Reads every *_gdelt.json file in data/raw/online/, builds one flat
article inventory CSV, filters to English-language articles (per the
project's English-only scope decision), and logs everything excluded
(non-English, duplicate URLs) to a separate CSV instead of dropping it
silently.

Usage:
    python build_article_inventory.py
"""

import json
import glob
import csv
import os
import re

RAW_DIR = "data/raw/online"
OUT_INVENTORY = "data/processed/article_inventory.csv"
OUT_EXCLUDED = "data/processed/excluded_articles.csv"

os.makedirs("data/processed", exist_ok=True)


def event_id_from_filename(path):
    # expects filenames like "E001_gdelt.json"
    name = os.path.basename(path)
    match = re.match(r"(E\d+)_gdelt\.json", name)
    return match.group(1) if match else name


def main():
    files = sorted(glob.glob(f"{RAW_DIR}/*_gdelt.json"))
    if not files:
        print(f"No *_gdelt.json files found in {RAW_DIR} -- nothing to build.")
        return

    seen_urls = set()
    kept_rows = []
    excluded_rows = []

    for path in files:
        event_id = event_id_from_filename(path)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"[{event_id}] could not parse {path}, skipping file")
                continue

        articles = data.get("articles", [])
        print(f"[{event_id}] {len(articles)} raw records in file")

        for a in articles:
            url = a.get("url", "")
            title = a.get("title", "")
            domain = a.get("domain", "")
            date = a.get("seendate", "")
            language = a.get("language", "")

            row = {
                "event_id": event_id,
                "title": title,
                "domain": domain,
                "date": date,
                "language": language,
                "url": url,
            }

            if not url:
                excluded_rows.append({**row, "exclusion_reason": "missing_url"})
                continue

            if url in seen_urls:
                excluded_rows.append({**row, "exclusion_reason": "duplicate_url"})
                continue

            if language != "English":
                excluded_rows.append({**row, "exclusion_reason": f"non_english:{language}"})
                continue

            seen_urls.add(url)
            kept_rows.append(row)

    fieldnames = ["event_id", "title", "domain", "date", "language", "url"]
    with open(OUT_INVENTORY, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)

    excluded_fieldnames = fieldnames + ["exclusion_reason"]
    with open(OUT_EXCLUDED, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=excluded_fieldnames)
        writer.writeheader()
        writer.writerows(excluded_rows)

    print(f"\nKept {len(kept_rows)} articles -> {OUT_INVENTORY}")
    print(f"Excluded {len(excluded_rows)} articles -> {OUT_EXCLUDED}")

    # quick per-event breakdown so you can see coverage at a glance
    counts = {}
    for row in kept_rows:
        counts[row["event_id"]] = counts.get(row["event_id"], 0) + 1
    print("\nKept articles per event:")
    for eid in sorted(counts):
        print(f"  {eid}: {counts[eid]}")


if __name__ == "__main__":
    main()