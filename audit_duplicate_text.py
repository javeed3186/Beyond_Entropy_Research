
import re
import hashlib
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/processed/article_text.csv")
OUTPUT_FILE = Path("data/processed/duplicate_text_audit.csv")


def normalize_text(value):
    """Lowercase text and collapse whitespace."""
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE).fillna("")

    required = {"event_id", "domain", "title", "url", "text"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["_normalized_text"] = df["text"].map(normalize_text)

    # Do not treat empty text as a duplicate group.
    df["_group_id"] = df["_normalized_text"].map(
        lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()
        if text else ""
    )

    counts = df.loc[df["_group_id"] != "", "_group_id"].value_counts()
    df["_group_size"] = df["_group_id"].map(counts).fillna(0).astype(int)

    # Include all records so each URL remains traceable.
    report = df[
        ["event_id", "domain", "title", "url", "_group_id", "_group_size"]
    ].copy()

    report = report.rename(columns={
        "_group_id": "normalized_text_group_id",
        "_group_size": "records_in_group",
    })

    report["is_duplicate_text"] = (
        (report["records_in_group"] > 1)
        & (report["normalized_text_group_id"] != "")
    )

    report.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    nonempty = df[df["_normalized_text"] != ""]
    unique_texts = nonempty["_normalized_text"].nunique()
    duplicate_groups = int((counts > 1).sum())
    duplicate_rows = int(counts[counts > 1].sum())

    print("DUPLICATE TEXT AUDIT COMPLETE")
    print(f"Input records: {len(df)}")
    print(f"Records with non-empty text: {len(nonempty)}")
    print(f"Unique normalized texts: {unique_texts}")
    print(f"Duplicate-text groups: {duplicate_groups}")
    print(f"Rows in duplicate-text groups: {duplicate_rows}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
