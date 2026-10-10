from pathlib import Path
import argparse
import pandas as pd

BASE = Path("data/processed")
OUTPUT = BASE / "pilot_text_dataset_review_ready.csv"

def read_csv(name):
    path = BASE / name
    if not path.exists():
        raise FileNotFoundError(f"Required input is missing: {path}")
    return pd.read_csv(path).fillna("")

def main():
    parser = argparse.ArgumentParser(
        description="Build a traceable, review-ready pilot text dataset."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Save the dataset. Without this flag, preview only."
    )
    args = parser.parse_args()

    texts = read_csv("article_text.csv")
    quality = read_csv("article_quality_report.csv")
    reviews = read_csv("manual_extraction_review.csv")

    for name, df in [
        ("article_text.csv", texts),
        ("article_quality_report.csv", quality),
        ("manual_extraction_review.csv", reviews),
    ]:
        if "url" not in df.columns:
            raise ValueError(f"{name} has no URL column.")

    for name, df in [
        ("article_text.csv", texts),
        ("article_quality_report.csv", quality),
        ("manual_extraction_review.csv", reviews),
    ]:
        urls = df["url"].astype(str).str.strip()
        if urls.eq("").any() or urls.duplicated().any():
            raise ValueError(
                f"{name} has blank or duplicate URLs. Resolve before joining."
            )
        df["url"] = urls

    quality_cols = [
        "url", "short_text", "duplicate_url", "duplicate_text",
        "suspicious_title", "needs_review"
    ]
    missing_quality = sorted(set(quality_cols) - set(quality.columns))
    if missing_quality:
        raise ValueError(f"Quality report missing columns: {missing_quality}")

    review_cols = ["url", "review_status", "reason"]
    missing_reviews = sorted(set(review_cols) - set(reviews.columns))
    if missing_reviews:
        raise ValueError(f"Manual review log missing columns: {missing_reviews}")

    if set(texts["url"]) != set(quality["url"]):
        raise ValueError(
            "Extracted-text and quality-report URL sets differ. No dataset built."
        )

    dataset = texts.merge(
        quality[quality_cols],
        on="url",
        how="left",
        validate="one_to_one",
        indicator="_quality_match"
    )
    if not dataset["_quality_match"].eq("both").all():
        raise ValueError("Some extracted records lack quality-report matches.")

    dataset = dataset.drop(columns="_quality_match")
    dataset = dataset.merge(
        reviews[review_cols],
        on="url",
        how="left",
        validate="one_to_one",
        indicator="_manual_review_match"
    )

    dataset["manual_review_status"] = dataset["review_status"].replace("", "not_manually_reviewed")
    dataset["manual_review_reason"] = dataset["reason"]
    dataset["manually_reviewed"] = dataset["_manual_review_match"].eq("both")

    # Keep the original article_text.csv fields and all quality flags.
    dataset = dataset.drop(
        columns=["review_status", "reason", "_manual_review_match"]
    )

    print("PILOT TEXT DATASET —", "WRITE MODE" if args.write else "PREVIEW ONLY")
    print("Extracted source records:", len(texts))
    print("Output records:", len(dataset))
    print("Manual-review matches:", int(dataset["manually_reviewed"].sum()))
    print("Records not manually reviewed:", int((~dataset["manually_reviewed"]).sum()))
    print("\nManual-review status counts:")
    print(dataset["manual_review_status"].value_counts().to_string())
    print("\nQuality flag totals:")
    for col in ["short_text", "duplicate_url", "duplicate_text", "suspicious_title", "needs_review"]:
        values = dataset[col].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
        print(f"{col}: {int(values.sum())}")

    print("\nPreview columns:", dataset.columns.tolist())
    print("\nManual-review records:")
    print(
        dataset.loc[dataset["manually_reviewed"],
                    ["event_id", "domain", "url", "manual_review_status",
                     "manual_review_reason"]].to_string(index=False)
    )

    if len(dataset) != len(texts):
        raise ValueError("Output record count differs from extracted source.")

    if not args.write:
        print("\nPreview only. No output dataset was saved.")
        print("Review the preview before running with --write.")
        return

    dataset.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print("\nDataset written to:", OUTPUT)

if __name__ == "__main__":
    main()
