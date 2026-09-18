import requests
import pandas as pd
import json
import time
import os

RAW_DIR = "data/raw"

os.makedirs(f"{RAW_DIR}/online", exist_ok=True)
os.makedirs(f"{RAW_DIR}/social", exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Research Pilot)"
}


def query_gdelt(keywords, start_date, end_date, max_records=20):

    query = " OR ".join(
        f'"{kw.strip()}"'
        for kw in keywords.split(",")
    )

    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": max_records,
        "startdatetime": start_date,
        "enddatetime": end_date,
    }

    for attempt in range(4):

        response = requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params=params,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code == 429:
            wait = 10 * (attempt + 1)
            print(f"  -> GDELT rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue

        response.raise_for_status()
        return response.json()

    raise Exception("GDELT failed after 4 attempts")


def query_reddit(keywords, limit=20):

    query = keywords.split(",")[0].strip()

    params = {
        "q": query,
        "sort": "top",
        "limit": limit,
        "t": "year"
    }

    response = requests.get(
        "https://www.reddit.com/search.json",
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def to_gdelt_datetime(date):

    return date.replace("-", "") + "000000"


def main():

    events = pd.read_csv("event_list.csv")

    for _, row in events.iterrows():

        event_id = row["event_id"]
        keywords = row["keywords"]
        anchor = row["anchor_date"]

        if pd.isna(anchor):
            continue

        start = to_gdelt_datetime(anchor)

        end_date = (
            pd.to_datetime(anchor)
            + pd.Timedelta(days=7)
        ).strftime("%Y-%m-%d")

        end = to_gdelt_datetime(end_date)

        # -----------------------------
        # GDELT
        # -----------------------------

        print(f"\n[{event_id}] GDELT")
        print(f"Keywords: {keywords}")

        try:

            result = query_gdelt(
                keywords,
                start,
                end
            )

            with open(
                f"{RAW_DIR}/online/{event_id}_gdelt.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    result,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            count = len(
                result.get("articles", [])
            )

            print(f"  -> {count} articles saved")

        except Exception as e:

            print(f"  -> GDELT failed: {e}")

        time.sleep(5)

        # -----------------------------
        # Reddit
        # -----------------------------

        print(f"[{event_id}] Reddit")

        try:

            result = query_reddit(keywords)

            with open(
                f"{RAW_DIR}/social/{event_id}_reddit.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    result,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            count = len(
                result.get("data", {}).get(
                    "children", []
                )
            )

            print(f"  -> {count} posts saved")

        except Exception as e:

            print(f"  -> Reddit failed: {e}")

        time.sleep(5)

    print("\nDone.")


if __name__ == "__main__":
    main()