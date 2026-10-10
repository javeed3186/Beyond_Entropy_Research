from pathlib import Path
import argparse
import pandas as pd

BASE = Path("data/processed")
OUTPUT = BASE / "phase3_quality_control_summary.csv"

def read_csv(name):
    path = BASE / name
    if not path.exists():
        raise FileNotFoundError(f"Required input is missing: {path}")
    return pd.read_csv(path).fillna("")

def require_columns(df, name, columns):
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")

def as_bool(series):
    return series.astype(str).str.strip().str.lower().isin(
        ["true", "1", "yes"]
    )

def normalize_text(value):
    return " ".join(str(value).lower().split())

def main():
    parser = argparse.ArgumentParser(
        description="Rebuild the Phase 3 quality-control summary."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the regenerated summary CSV. Without this flag, preview only."
    )
    args = parser.parse_args()

    inventory = read_csv("article_inventory.csv")
    texts = read_csv("article_text.csv")
    quality = read_csv("article_quality_report.csv")
    failures = read_csv("unresolved_extraction_failures.csv")

    require_columns(inventory, "article_inventory.csv", ["event_id", "url"])
    require_columns(texts, "article_text.csv", ["event_id", "url", "text"])
    require_columns(
        quality,
        "article_quality_report.csv",
        ["event_id", "url", "short_text", "suspicious_title", "needs_review"]
    )
    require_columns(
        failures,
        "unresolved_extraction_failures.csv",
        ["event_id", "url"]
    )

    if texts["url"].astype(str).duplicated().any():
        raise ValueError("article_text.csv has duplicate URLs; investigate before summarizing.")

    if quality["url"].astype(str).duplicated().any():
        raise ValueError("article_quality_report.csv has duplicate URLs; investigate before summarizing.")

    if set(texts["url"].astype(str)) != set(quality["url"].astype(str)):
        raise ValueError("article_text.csv and article_quality_report.csv URL sets differ.")

    events = sorted(set(inventory["event_id"].astype(str)))
    rows = []

    for event in events:
        inv = inventory[inventory["event_id"].astype(str) == event]
        txt = texts[texts["event_id"].astype(str) == event].copy()
        qua = quality[quality["event_id"].astype(str) == event].copy()
        fail = failures[failures["event_id"].astype(str) == event]

        normalized = txt["text"].map(normalize_text)
        counts = normalized.value_counts()
        duplicate_group_rows = int(normalized.map(counts).gt(1).sum())
        beyond_first = int((counts[counts > 1] - 1).sum())

        extracted = len(txt)
        unresolved_unique = fail["url"].astype(str).nunique()

        rows.append({
            "event_id": event,
            "inventory_urls": int(inv["url"].astype(str).nunique()),
            "successful_urls": int(txt["url"].astype(str).nunique()),
            "extraction_rate_percent": round(
                100 * txt["url"].astype(str).nunique() /
                max(1, inv["url"].astype(str).nunique()), 1
            ),
            "extracted_records": extracted,
            "needs_review": int(as_bool(qua["needs_review"]).sum()),
            "short_text": int(as_bool(qua["short_text"]).sum()),
            "suspicious_title": int(as_bool(qua["suspicious_title"]).sum()),
            "total_records": extracted,
            "nonempty_text_records": int(txt["text"].astype(str).str.strip().ne("").sum()),
            "unique_normalized_texts": int(normalized.nunique()),
            "records_in_duplicate_groups": duplicate_group_rows,
            "records_beyond_first_occurrence": beyond_first,
            "duplicate_group_record_share_percent": round(
                100 * duplicate_group_rows / max(1, extracted), 1
            ),
            "unresolved_failure_rows": len(fail),
            "unresolved_unique_urls": unresolved_unique,
        })

    result = pd.DataFrame(rows)

    print("REGENERATED SUMMARY —", "WRITE MODE" if args.write else "PREVIEW ONLY")
    print(result.to_string(index=False))

    print("\nTOTALS")
    for col in [
        "inventory_urls", "successful_urls", "extracted_records",
        "needs_review", "short_text", "suspicious_title",
        "records_beyond_first_occurrence",
        "unresolved_failure_rows", "unresolved_unique_urls"
    ]:
        print(f"{col}: {int(result[col].sum())}")

    if not args.write:
        print("\nPreview only. Existing summary was not changed.")
        print("If the figures are validated, rerun with --write to save.")
        return

    result.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"\nSummary written to: {OUTPUT}")

if __name__ == "__main__":
    main()
