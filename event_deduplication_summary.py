
import re
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/processed/article_text.csv")
OUTPUT_FILE = Path("data/processed/event_deduplication_summary.csv")


def normalize_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE).fillna("")

    required = {"event_id", "url", "text"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["_normalized_text"] = df["text"].map(normalize_text)

    # Empty text is not counted as a unique article text.
    nonempty = df[df["_normalized_text"] != ""].copy()

    # A text is duplicated when the same normalized text occurs
    # more than once anywhere in the extracted dataset.
    text_counts = nonempty["_normalized_text"].value_counts()
    nonempty["_group_size"] = nonempty["_normalized_text"].map(text_counts)

    rows = []

    for event_id, event_df in df.groupby("event_id", sort=True):
        event_nonempty = nonempty[nonempty["event_id"] == event_id]
        unique_texts = event_nonempty["_normalized_text"].nunique()

        duplicate_rows = int(
            (event_nonempty["_group_size"] > 1).sum()
        )

        rows.append({
            "event_id": event_id,
            "total_records": len(event_df),
            "nonempty_text_records": len(event_nonempty),
            "unique_normalized_texts": unique_texts,
            "records_in_duplicate_groups": duplicate_rows,
            "records_beyond_first_occurrence": (
                len(event_nonempty) - unique_texts
            ),
            "duplicate_group_record_share_percent": round(
                100 * duplicate_rows / len(event_nonempty), 1
            ) if len(event_nonempty) else 0.0,
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print("EVENT DEDUPLICATION SUMMARY COMPLETE")
    print(summary.to_string(index=False))
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
