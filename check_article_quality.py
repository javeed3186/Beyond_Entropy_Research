"""
Quality check for the extracted article-text dataset.

Input:
    data/processed/article_text.csv

Output:
    data/processed/article_quality_report.csv

Checks:
    - text length
    - very short articles
    - duplicate URLs
    - duplicate text
    - suspicious archive/topic pages
"""

import pandas as pd
import os
import re

INPUT_FILE = "data/processed/article_text.csv"
OUTPUT_FILE = "data/processed/article_quality_report.csv"

MIN_REASONABLE_LENGTH = 1000


def normalize_text(text):
    """Normalize text for duplicate-text checking."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():

    print("=" * 60)
    print("ARTICLE TEXT QUALITY CHECK")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"\nTotal extracted articles: {len(df)}")

    # ---------------------------------------------------------
    # Basic checks
    # ---------------------------------------------------------

    df["text"] = df["text"].fillna("")
    df["text_length"] = pd.to_numeric(
        df["text_length"],
        errors="coerce"
    ).fillna(0)

    # ---------------------------------------------------------
    # Length categories
    # ---------------------------------------------------------

    very_short = df[df["text_length"] < 1000]
    short = df[
        (df["text_length"] >= 1000) &
        (df["text_length"] < 2000)
    ]
    medium = df[
        (df["text_length"] >= 2000) &
        (df["text_length"] < 5000)
    ]
    long = df[df["text_length"] >= 5000]

    print("\nTEXT LENGTH DISTRIBUTION")
    print("-" * 40)
    print(f"< 1000 characters : {len(very_short)}")
    print(f"1000–1999        : {len(short)}")
    print(f"2000–4999        : {len(medium)}")
    print(f">= 5000          : {len(long)}")

    # ---------------------------------------------------------
    # URL duplicates
    # ---------------------------------------------------------

    duplicate_url_mask = df["url"].duplicated(keep=False)
    duplicate_urls = df[duplicate_url_mask]

    print("\nURL DUPLICATES")
    print("-" * 40)
    print(f"Duplicate URL rows: {len(duplicate_urls)}")

    # ---------------------------------------------------------
    # Exact text duplicates
    # ---------------------------------------------------------

    df["_normalized_text"] = df["text"].apply(normalize_text)

    duplicate_text_mask = df["_normalized_text"].duplicated(
        keep=False
    )

    duplicate_text = df[duplicate_text_mask]

    print("\nEXACT / NORMALIZED TEXT DUPLICATES")
    print("-" * 40)
    print(f"Duplicate text rows: {len(duplicate_text)}")

    # ---------------------------------------------------------
    # Suspicious titles
    # ---------------------------------------------------------

    suspicious_pattern = (
        r"\b(latest news|live updates|updates|"
        r"photos|videos|news headlines|"
        r"topic|archive)\b"
    )

    suspicious_mask = df["title"].fillna("").str.contains(
        suspicious_pattern,
        case=False,
        regex=True
    )

    suspicious = df[suspicious_mask]

    print("\nPOTENTIALLY SUSPICIOUS / ARCHIVE-LIKE PAGES")
    print("-" * 40)
    print(f"Potentially suspicious rows: {len(suspicious)}")

    # ---------------------------------------------------------
    # Build quality report
    # ---------------------------------------------------------

    report = df[
        [
            "event_id",
            "title",
            "domain",
            "date",
            "language",
            "url",
            "text_length",
        ]
    ].copy()

    report["short_text"] = report["text_length"] < MIN_REASONABLE_LENGTH

    report["duplicate_url"] = df["url"].duplicated(
        keep=False
    )

    report["duplicate_text"] = duplicate_text_mask

    report["suspicious_title"] = suspicious_mask

    # Overall flag
    report["needs_review"] = (
        report["short_text"] |
        report["duplicate_url"] |
        report["duplicate_text"] |
        report["suspicious_title"]
    )

    # ---------------------------------------------------------
    # Save report
    # ---------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("QUALITY CHECK COMPLETE")
    print("=" * 60)

    print(f"Report saved to:")
    print(f"  {OUTPUT_FILE}")

    print("\nArticles requiring manual review:")
    print(
        f"  {report['needs_review'].sum()}"
        f" / {len(report)}"
    )

    # ---------------------------------------------------------
    # Show short articles
    # ---------------------------------------------------------

    if len(very_short) > 0:

        print("\nSHORT ARTICLES (<1000 characters)")
        print("-" * 40)

        for _, row in very_short.iterrows():
            print(
                f"{row['event_id']} | "
                f"{row['domain']} | "
                f"{row['text_length']} chars"
            )

    # ---------------------------------------------------------
    # Show suspicious pages
    # ---------------------------------------------------------

    if len(suspicious) > 0:

        print("\nPOTENTIALLY SUSPICIOUS PAGES")
        print("-" * 40)

        for _, row in suspicious.iterrows():
            print(
                f"{row['event_id']} | "
                f"{row['domain']} | "
                f"{row['title'][:100]}"
            )


if __name__ == "__main__":
    main()