"""
Phase 1 article-text extraction.

Input:
    data/processed/article_inventory.csv

Outputs:
    data/processed/article_text.csv
    data/processed/extraction_failures.csv

The script saves after every successful article so that
progress is not lost if the run stops.
"""

import os
import time
import pandas as pd
import trafilatura


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

INPUT_FILE = "data/processed/article_inventory.csv"

OUTPUT_FILE = "data/processed/article_text.csv"

FAILURE_FILE = "data/processed/extraction_failures.csv"


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

REQUEST_DELAY = 2

# Articles with fewer characters than this are treated
# as probably unusable for later linguistic analysis.
MIN_TEXT_LENGTH = 300


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    # Check that inventory exists
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found.")
        print("Run build_article_inventory.py first.")
        return

    # Read article inventory
    df = pd.read_csv(INPUT_FILE)

    print("=" * 60)
    print("ARTICLE TEXT EXTRACTION")
    print("=" * 60)

    print(f"Articles in inventory: {len(df)}")
    print()

    # -----------------------------------------------------
    # Load previous successful results if available
    # -----------------------------------------------------

    if os.path.exists(OUTPUT_FILE):

        results_df = pd.read_csv(
            OUTPUT_FILE,
            keep_default_na=False
        )

        processed_urls = set(
            results_df["url"]
        )

        print(
            f"Existing successful articles: "
            f"{len(processed_urls)}"
        )

    else:

        results_df = pd.DataFrame(
            columns=[
                "event_id",
                "title",
                "domain",
                "date",
                "language",
                "url",
                "text",
                "text_length"
            ]
        )

        processed_urls = set()

    # -----------------------------------------------------
    # Load previous failures if available
    # -----------------------------------------------------

    if os.path.exists(FAILURE_FILE):

        failures_df = pd.read_csv(
            FAILURE_FILE,
            keep_default_na=False
        )

    else:

        failures_df = pd.DataFrame(
            columns=[
                "event_id",
                "title",
                "domain",
                "url",
                "failure_reason"
            ]
        )

    # -----------------------------------------------------
    # Process articles
    # -----------------------------------------------------

    for position, row in df.iterrows():

        url = row["url"]

        # Skip already processed URLs
        if url in processed_urls:

            print(
                f"[{position + 1}/{len(df)}] "
                f"ALREADY DONE: {row['domain']}"
            )

            continue

        print(
            f"[{position + 1}/{len(df)}] "
            f"{row['domain']}"
        )

        try:

            # -------------------------------------------------
            # Download webpage
            # -------------------------------------------------

            downloaded = trafilatura.fetch_url(url)

            if downloaded is None:

                reason = "fetch_failed"

                print(
                    f"    -> FAILED: {reason}"
                )

                failure = {
                    "event_id": row["event_id"],
                    "title": row["title"],
                    "domain": row["domain"],
                    "url": url,
                    "failure_reason": reason
                }

                failures_df = pd.concat(
                    [
                        failures_df,
                        pd.DataFrame([failure])
                    ],
                    ignore_index=True
                )

                failures_df.to_csv(
                    FAILURE_FILE,
                    index=False
                )

                time.sleep(REQUEST_DELAY)

                continue

            # -------------------------------------------------
            # Extract article text
            # -------------------------------------------------

            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_precision=True
            )

            if text is None:

                reason = "no_text_extracted"

                print(
                    f"    -> FAILED: {reason}"
                )

                failure = {
                    "event_id": row["event_id"],
                    "title": row["title"],
                    "domain": row["domain"],
                    "url": url,
                    "failure_reason": reason
                }

                failures_df = pd.concat(
                    [
                        failures_df,
                        pd.DataFrame([failure])
                    ],
                    ignore_index=True
                )

                failures_df.to_csv(
                    FAILURE_FILE,
                    index=False
                )

                time.sleep(REQUEST_DELAY)

                continue

            # -------------------------------------------------
            # Check text length
            # -------------------------------------------------

            text_length = len(text)

            if text_length < MIN_TEXT_LENGTH:

                reason = f"text_too_short:{text_length}"

                print(
                    f"    -> FAILED: {reason}"
                )

                failure = {
                    "event_id": row["event_id"],
                    "title": row["title"],
                    "domain": row["domain"],
                    "url": url,
                    "failure_reason": reason
                }

                failures_df = pd.concat(
                    [
                        failures_df,
                        pd.DataFrame([failure])
                    ],
                    ignore_index=True
                )

                failures_df.to_csv(
                    FAILURE_FILE,
                    index=False
                )

                time.sleep(REQUEST_DELAY)

                continue

            # -------------------------------------------------
            # Successful extraction
            # -------------------------------------------------

            result = {
                "event_id": row["event_id"],
                "title": row["title"],
                "domain": row["domain"],
                "date": row["date"],
                "language": row["language"],
                "url": url,
                "text": text,
                "text_length": text_length
            }

            results_df = pd.concat(
                [
                    results_df,
                    pd.DataFrame([result])
                ],
                ignore_index=True
            )

            # Save immediately
            results_df.to_csv(
                OUTPUT_FILE,
                index=False
            )

            processed_urls.add(url)

            print(
                f"    -> SUCCESS: "
                f"{text_length} characters"
            )

        except Exception as e:

            reason = (
                f"{type(e).__name__}: "
                f"{str(e)}"
            )

            print(
                f"    -> ERROR: {reason}"
            )

            failure = {
                "event_id": row["event_id"],
                "title": row["title"],
                "domain": row["domain"],
                "url": url,
                "failure_reason": reason
            }

            failures_df = pd.concat(
                [
                    failures_df,
                    pd.DataFrame([failure])
                ],
                ignore_index=True
            )

            failures_df.to_csv(
                FAILURE_FILE,
                index=False
            )

        # Don't hammer news websites
        time.sleep(REQUEST_DELAY)

    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)

    print(
        f"Successful articles: "
        f"{len(results_df)}"
    )

    print(
        f"Failed articles: "
        f"{len(failures_df)}"
    )

    print()
    print(
        f"Saved successful articles to:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print()
    print(
        f"Saved failures to:"
    )

    print(
        f"  {FAILURE_FILE}"
    )

    # -----------------------------------------------------
    # Per-event counts
    # -----------------------------------------------------

    if len(results_df) > 0:

        print()
        print("Successful articles per event:")

        counts = (
            results_df
            .groupby("event_id")
            .size()
            .sort_index()
        )

        for event_id, count in counts.items():

            print(
                f"  {event_id}: {count}"
            )


if __name__ == "__main__":
    main()