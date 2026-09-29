"""
Phase 1 pilot collector -- Media Cloud.

Collects Media Cloud Online News metadata for the same events
used in the GDELT pilot.

Requirements:
    pip install mediacloud pandas

Environment variables:
    MEDIACLOUD_API_KEY
    MEDIACLOUD_COLLECTION_IDS   (optional; defaults to 1)

Usage:
    python collect_mediacloud.py
    python collect_mediacloud.py E005
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import date, timedelta

import mediacloud.api
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

EVENT_FILE = "event_list.csv"

OUTPUT_DIR = Path("data/raw/online/mediacloud")

MAX_RECORDS = 200

SECONDS_BETWEEN_REQUESTS = 10

PLATFORM = "onlinenews-mediacloud"

# IMPORTANT:
# Collection 1 is known to work with this API key.
DEFAULT_COLLECTION_IDS = [1]


# ============================================================
# ENVIRONMENT
# ============================================================

def get_api_key():
    key = os.getenv("MEDIACLOUD_API_KEY")

    if not key:
        raise RuntimeError(
            "\nMEDIACLOUD_API_KEY is not available in this terminal.\n"
            "Run:\n"
            '$env:MEDIACLOUD_API_KEY = [Environment]::GetEnvironmentVariable("MEDIACLOUD_API_KEY", "User")\n'
        )

    return key.strip()


def get_collection_ids():
    """
    Read collection IDs from the environment.

    If MEDIACLOUD_COLLECTION_IDS is not set,
    use collection 1 because it has already been
    verified to work.
    """

    raw = os.getenv("MEDIACLOUD_COLLECTION_IDS")

    if not raw or not raw.strip():
        return DEFAULT_COLLECTION_IDS.copy()

    ids = []

    for item in raw.split(","):
        item = item.strip()

        if not item:
            continue

        try:
            ids.append(int(item))
        except ValueError:
            raise ValueError(
                f"Invalid Media Cloud collection ID: {item}"
            )

    if not ids:
        return DEFAULT_COLLECTION_IDS.copy()

    return ids


# ============================================================
# DATE HANDLING
# ============================================================

def parse_event_date(value):
    return pd.to_datetime(
        value,
        format="%d-%m-%Y"
    ).date()


def build_date_window(anchor):
    start_date = parse_event_date(anchor)

    # Seven-day window.
    # This matches the GDELT pilot.
    end_date = start_date + timedelta(days=7)

    return start_date, end_date


# ============================================================
# QUERY CLEANING
# ============================================================

def clean_query(value):
    """
    Convert GDELT-style query text into the Media Cloud query
    used by this pilot.

    Only removes quotation marks when they wrap the ENTIRE
    query.

    Examples:

        "Cebu earthquake"
            -> Cebu earthquake

        "government shutdown" reopens
            -> "government shutdown" reopens

        "Red Fort" blast
            -> "Red Fort" blast
    """

    if pd.isna(value):
        return ""

    query = str(value).strip()

    if (
        len(query) >= 2
        and query.startswith('"')
        and query.endswith('"')
        and query.count('"') == 2
    ):
        query = query[1:-1].strip()

    return query


# ============================================================
# STORY CLEANING
# ============================================================

def clean_story(story, event_id):
    return {
        "event_id": event_id,
        "mediacloud_id": story.get("id"),
        "title": story.get("title"),
        "media_name": story.get("media_name"),
        "media_url": story.get("media_url"),
        "publish_date": (
            str(story.get("publish_date"))
            if story.get("publish_date")
            else None
        ),
        "indexed_date": (
            str(story.get("indexed_date"))
            if story.get("indexed_date")
            else None
        ),
        "language": story.get("language"),
        "url": story.get("url"),
    }


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(rows, event_id):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    csv_path = OUTPUT_DIR / f"{event_id}_mediacloud.csv"

    json_path = OUTPUT_DIR / f"{event_id}_mediacloud.json"

    df = pd.DataFrame(rows)

    # Always write the CSV, including zero-result events.
    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8"
    )

    with json_path.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            rows,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved CSV : {csv_path}")
    print(f"Saved JSON: {json_path}")


# ============================================================
# COLLECT ONE EVENT
# ============================================================

def collect_event(
    mc_search,
    row,
    collection_ids
):

    event_id = str(row["event_id"]).strip()

    event_name = str(
        row.get("event_name", "")
    ).strip()

    query = clean_query(
        row["gdelt_query"]
    )

    anchor = row["anchor_date"]

    if not query:
        raise ValueError(
            f"{event_id}: query is empty"
        )

    if pd.isna(anchor):
        raise ValueError(
            f"{event_id}: anchor_date is empty"
        )

    start_date, end_date = build_date_window(
        anchor
    )

    print("\n" + "=" * 70)
    print(f"EVENT       : {event_id}")
    print(f"NAME        : {event_name}")
    print(f"QUERY       : {query!r}")
    print(f"START       : {start_date}")
    print(f"END         : {end_date}")
    print(f"PLATFORM    : {PLATFORM}")
    print(f"COLLECTIONS : {collection_ids}")
    print(f"MAX RECORDS : {MAX_RECORDS}")
    print("=" * 70)

    print("\nRequesting Media Cloud stories...")

    # --------------------------------------------------------
    # IMPORTANT FIX
    # --------------------------------------------------------
    #
    # Explicitly pass:
    #   collection_ids=[1]
    #   platform="onlinenews-mediacloud"
    #
    # We do NOT rely on the environment variable being interpreted
    # correctly inside the API call.
    #
    stories = mc_search.story_sample(
        query=query,
        start_date=start_date,
        end_date=end_date,
        collection_ids=collection_ids,
        source_ids=[],
        platform=PLATFORM,
        limit=MAX_RECORDS,
        expanded=False,
    )

    print(
        f"Stories returned: {len(stories)}"
    )

    cleaned = [
        clean_story(
            story,
            event_id
        )
        for story in stories
    ]

    save_results(
        cleaned,
        event_id
    )

    # Show a small preview.
    if cleaned:

        print("\nFirst result:")

        first = cleaned[0]

        print(
            f"  Title : {first.get('title')}"
        )

        print(
            f"  Media : {first.get('media_name')}"
        )

        print(
            f"  Date  : {first.get('publish_date')}"
        )

        print(
            f"  URL   : {first.get('url')}"
        )

    else:

        print(
            "\nWARNING: Media Cloud returned zero stories."
        )

    return cleaned


# ============================================================
# API VALIDATION
# ============================================================

def validate_api(mc_search):
    """
    Verify that the API key works before touching event data.
    """

    print("\nChecking Media Cloud API key...")

    profile = mc_search.user_profile()

    print(
        f"Authenticated Media Cloud user: "
        f"{profile.get('username', 'unknown')}"
    )

    quota = profile.get("quota", {})

    if quota:
        print(
            f"Weekly quota: "
            f"{quota.get('hits')} / {quota.get('limit')}"
        )

    print("API authentication: OK")


# ============================================================
# LOAD EVENTS
# ============================================================

def load_events():
    if not Path(EVENT_FILE).exists():
        raise FileNotFoundError(
            f"Could not find {EVENT_FILE}"
        )

    events = pd.read_csv(
        EVENT_FILE
    )

    required_columns = {
        "event_id",
        "event_name",
        "gdelt_query",
        "anchor_date",
    }

    missing = required_columns - set(
        events.columns
    )

    if missing:
        raise ValueError(
            "event_list.csv is missing columns: "
            + ", ".join(sorted(missing))
        )

    return events


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("MEDIACLOUD PHASE 1 PILOT COLLECTION")
    print("=" * 70)

    # --------------------------------------------------------
    # API key
    # --------------------------------------------------------

    api_key = get_api_key()

    print(
        "Media Cloud API key: available"
    )

    print(
        f"API key length: {len(api_key)}"
    )

    # --------------------------------------------------------
    # Collections
    # --------------------------------------------------------

    collection_ids = get_collection_ids()

    print(
        f"Collection IDs: {collection_ids}"
    )

    print(
        f"Maximum records per event: {MAX_RECORDS}"
    )

    # --------------------------------------------------------
    # Initialize API
    # --------------------------------------------------------

    mc_search = mediacloud.api.SearchApi(
        api_key
    )

    # --------------------------------------------------------
    # Validate authentication
    # --------------------------------------------------------

    try:

        validate_api(
            mc_search
        )

    except Exception as exc:

        print(
            "\nMedia Cloud authentication failed."
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Load events
    # --------------------------------------------------------

    events = load_events()

    # --------------------------------------------------------
    # Optional single-event mode
    # --------------------------------------------------------

    requested_event = None

    if len(sys.argv) > 1:
        requested_event = (
            sys.argv[1]
            .strip()
            .upper()
        )

        print(
            f"\nRunning ONLY event: "
            f"{requested_event}"
        )

    # --------------------------------------------------------
    # Collection summary
    # --------------------------------------------------------

    completed = {}
    skipped = {}
    failed = {}

    # --------------------------------------------------------
    # Process events
    # --------------------------------------------------------

    for _, row in events.iterrows():

        event_id = str(
            row["event_id"]
        ).strip().upper()

        # If a specific event was requested,
        # ignore all other events.
        if (
            requested_event
            and event_id != requested_event
        ):
            continue

        # ----------------------------------------------------
        # Existing output check
        # ----------------------------------------------------

        output_file = (
            OUTPUT_DIR
            / f"{event_id}_mediacloud.csv"
        )

        if output_file.exists():

            try:

                existing = pd.read_csv(
                    output_file
                )

                existing_count = len(
                    existing
                )

            except Exception:

                existing_count = 0

            # Do not skip zero-result files.
            #
            # This is important:
            # E004/E005 previously contained zero rows,
            # so they must be queried again.
            if existing_count > 0:

                skipped[event_id] = (
                    existing_count
                )

                print("\n" + "=" * 70)
                print(
                    f"[SKIP] {event_id}: "
                    f"{existing_count} records already exist."
                )
                print("=" * 70)

                if not requested_event:
                    print(
                        f"\nWaiting "
                        f"{SECONDS_BETWEEN_REQUESTS} seconds..."
                    )
                    time.sleep(
                        SECONDS_BETWEEN_REQUESTS
                    )

                continue

        # ----------------------------------------------------
        # Collect
        # ----------------------------------------------------

        try:

            rows = collect_event(
                mc_search,
                row,
                collection_ids
            )

            completed[event_id] = len(
                rows
            )

        except Exception as exc:

            failed[event_id] = (
                f"{type(exc).__name__}: {exc}"
            )

            error_file = (
                OUTPUT_DIR
                / f"{event_id}_error.txt"
            )

            error_file.write_text(
                f"{type(exc).__name__}: {exc}\n",
                encoding="utf-8"
            )

            print(
                f"\n[FAILED] {event_id}"
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

            print(
                f"Error saved: {error_file}"
            )

        # ----------------------------------------------------
        # Delay
        # ----------------------------------------------------

        if not requested_event:

            print(
                f"\nWaiting "
                f"{SECONDS_BETWEEN_REQUESTS} seconds..."
            )

            time.sleep(
                SECONDS_BETWEEN_REQUESTS
            )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("MEDIACLOUD COLLECTION SUMMARY")
    print("=" * 70)

    print("\nCompleted:")

    if completed:

        for event_id, count in completed.items():

            print(
                f"  {event_id}: "
                f"{count} records"
            )

    else:

        print("  None")

    print("\nSkipped:")

    if skipped:

        for event_id, count in skipped.items():

            print(
                f"  {event_id}: "
                f"{count} existing records"
            )

    else:

        print("  None")

    print("\nFailed:")

    if failed:

        for event_id, error in failed.items():

            print(
                f"  {event_id}: "
                f"{error}"
            )

    else:

        print("  None")

    print(
        f"\nOutput directory: "
        f"{OUTPUT_DIR}"
    )

    print(
        f"Collection IDs used: "
        f"{collection_ids}"
    )

    print(
        f"Platform: {PLATFORM}"
    )

    print(
        f"Maximum records requested: "
        f"{MAX_RECORDS}"
    )

    print(
        "\nCollection process finished."
    )


if __name__ == "__main__":
    main()