"""
MediaCloud pilot collector for the Beyond Entropy Research project.

Purpose:
    Collect MediaCloud story metadata for the same event definitions
    used by the GDELT pilot.

Important:
    - Uses event_list.csv as the single source of event/query/date definitions.
    - Uses the same query and anchor-date logic as the GDELT pilot.
    - Collects metadata only.
    - Skips events that already have a successful MediaCloud CSV.
    - Records failures separately.
"""

import os
import time
from pathlib import Path

import mediacloud.api
import pandas as pd


EVENT_FILE = Path("event_list.csv")
OUTPUT_DIR = Path("data/raw/online/mediacloud")

MAX_RECORDS = 200
SECONDS_BETWEEN_REQUESTS = 10


def get_api_key():
    key = os.getenv("MEDIACLOUD_API_KEY")

    if not key:
        raise RuntimeError(
            "MEDIACLOUD_API_KEY is not set."
        )

    if key in {"...", "PASTE_YOUR_API_KEY_HERE"}:
        raise RuntimeError(
            "MEDIACLOUD_API_KEY is still a placeholder."
        )

    return key


def parse_event_date(value):
    return pd.to_datetime(
        value,
        format="%d-%m-%Y"
    ).date()


def build_date_window(anchor_date):
    start_date = parse_event_date(anchor_date)
    end_date = start_date + pd.Timedelta(days=7)

    return start_date, end_date


def collect_event(mc_search, row):
    event_id = row["event_id"]
    event_name = row["event_name"]
    query = str(row["gdelt_query"]).strip()

    start_date, end_date = build_date_window(
        row["anchor_date"]
    )

    output_file = OUTPUT_DIR / f"{event_id}_mediacloud.csv"

    print()
    print("=" * 70)
    print(f"EVENT: {event_id}")
    print(f"NAME : {event_name}")
    print(f"QUERY: {query}")
    print(f"START: {start_date}")
    print(f"END  : {end_date}")
    print("=" * 70)

    stories = mc_search.story_sample(
        query,
        start_date=start_date,
        end_date=end_date,
        limit=MAX_RECORDS,
        expanded=False,
    )

    rows = []

    for story in stories:
        rows.append(
            {
                "id": story.get("id"),
                "indexed_date": story.get("indexed_date"),
                "language": story.get("language"),
                "media_name": story.get("media_name"),
                "media_url": story.get("media_url"),
                "publish_date": story.get("publish_date"),
                "title": story.get("title"),
                "url": story.get("url"),
            }
        )

    df = pd.DataFrame(rows)

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8",
    )

    print(f"Stories returned: {len(df)}")
    print(f"Saved: {output_file}")

    return len(df)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    events = pd.read_csv(EVENT_FILE)

    api_key = get_api_key()

    mc_search = mediacloud.api.SearchApi(
        api_key
    )

    completed = []
    skipped = []
    failed = []

    for _, row in events.iterrows():

        event_id = row["event_id"]

        output_file = (
            OUTPUT_DIR
            / f"{event_id}_mediacloud.csv"
        )

        # Skip already completed events

        if output_file.exists():

            try:
                existing = pd.read_csv(
                    output_file
                )

                if len(existing) > 0:

                    print()
                    print(
                        f"[SKIP] {event_id}: "
                        f"{len(existing)} records already exist."
                    )

                    skipped.append(event_id)

                    continue

            except Exception:
                print(
                    f"[WARNING] Existing file for "
                    f"{event_id} could not be read."
                )

        # Collect event

        try:

            count = collect_event(
                mc_search,
                row
            )

            completed.append(
                (event_id, count)
            )

        except Exception as exc:

            error_file = (
                OUTPUT_DIR
                / f"{event_id}_error.txt"
            )

            error_file.write_text(
                f"{type(exc).__name__}: {exc}\n",
                encoding="utf-8"
            )

            print()
            print(
                f"[ERROR] {event_id}: "
                f"{type(exc).__name__}: {exc}"
            )

            print(
                f"Error saved: {error_file}"
            )

            failed.append(event_id)

        print(
            f"Waiting "
            f"{SECONDS_BETWEEN_REQUESTS} seconds..."
        )

        time.sleep(
            SECONDS_BETWEEN_REQUESTS
        )

    # Final summary

    print()
    print("=" * 70)
    print("MEDIACLOUD COLLECTION SUMMARY")
    print("=" * 70)

    print()
    print("Completed:")

    if completed:
        for event_id, count in completed:
            print(
                f"  {event_id}: "
                f"{count} records"
            )
    else:
        print("  None")

    print()
    print("Skipped:")

    if skipped:
        for event_id in skipped:
            print(
                f"  {event_id}"
            )
    else:
        print("  None")

    print()
    print("Failed:")

    if failed:
        for event_id in failed:
            print(
                f"  {event_id}"
            )
    else:
        print("  None")

    print()
    print(
        f"Output directory: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()