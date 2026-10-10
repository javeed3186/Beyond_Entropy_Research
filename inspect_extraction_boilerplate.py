
import re
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/processed/article_text.csv")

# These are review signals, not automatic rejection rules.
BOILERPLATE_PATTERNS = {
    "subscription_prompt": r"\b(subscribe today|subscription|subscribe now|"
                           r"ad-free access|digital edition access)\b",
    "account_or_membership": r"\b(sign in|log in|create an account|"
                             r"membership benefits|subscriber only)\b",
    "cookie_or_privacy_prompt": r"\b(accept all cookies|manage cookies|"
                                r"privacy preferences)\b",
}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE).fillna("")

    required = {"event_id", "domain", "title", "url", "text"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    flagged = []

    for _, row in df.iterrows():
        text = str(row["text"])
        matched = [
            label
            for label, pattern in BOILERPLATE_PATTERNS.items()
            if re.search(pattern, text, flags=re.IGNORECASE)
        ]

        if matched:
            flagged.append({
                "event_id": row["event_id"],
                "domain": row["domain"],
                "title": row["title"],
                "url": row["url"],
                "text_length": len(text),
                "boilerplate_signals": "; ".join(matched),
                "text_preview": re.sub(r"\s+", " ", text)[:300],
            })

    report = pd.DataFrame(flagged)
    output = Path("data/processed/boilerplate_review.csv")
    report.to_csv(output, index=False, encoding="utf-8")

    print("BOILERPLATE REVIEW SCAN COMPLETE")
    print("Input records:", len(df))
    print("Records with review signals:", len(report))
    print("Output:", output)

    if not report.empty:
        print("\nFlag counts by signal:")
        for label in BOILERPLATE_PATTERNS:
            count = report["boilerplate_signals"].str.contains(
                label, regex=False
            ).sum()
            print(f"{label}: {count}")

        print("\nFirst 15 flagged records:")
        print(
            report[
                ["event_id", "domain", "text_length",
                 "boilerplate_signals", "title"]
            ].head(15).to_string(index=False, max_colwidth=80)
        )


if __name__ == "__main__":
    main()
