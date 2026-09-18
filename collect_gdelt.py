"""
Phase 1 pilot collector -- GDELT only, for now.

Reddit's public search.json endpoint is currently returning 403 (blocked)
from your machine, which is a separate problem (see the note at the
bottom of this file) -- not something to fix by adding retries here.
Keep this script focused on getting a clean GDELT pilot working first.

Usage:
    python collect_gdelt.py
"""

import requests
import pandas as pd
import json
import time
import os

RAW_DIR = "data/raw/online"
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (phase1-research-pilot/0.2)"}

# GDELT explicitly asked for 1 request per 5 seconds. We're using a much
# more conservative gap here because a burst of test calls earlier in this
# session appears to have triggered a temporary IP-level cooldown, not
# because single requests need this much space in normal operation.
SECONDS_BETWEEN_REQUESTS = 30
MAX_RETRIES_ON_429 = 2


def query_gdelt(query, start_date, end_date, max_records=20):
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": max_records,
        "startdatetime": start_date,
        "enddatetime": end_date,
    }
    resp = requests.get(
        "https://api.gdeltproject.org/api/v2/doc/doc",
        params=params,
        headers=HEADERS,
        timeout=30,
    )
    return resp


def to_gdelt_datetime(date_str):
    return date_str.replace("-", "") + "000000"


def main():
    events = pd.read_csv("event_list.csv")

    for _, row in events.iterrows():
        event_id = row["event_id"]
        query = row["gdelt_query"]
        anchor = row["anchor_date"]

        if pd.isna(anchor) or pd.isna(query):
            print(f"[{event_id}] missing anchor_date or gdelt_query, skipping")
            continue

        start = to_gdelt_datetime(anchor)
        end_ts = pd.to_datetime(anchor) + pd.Timedelta(days=7)
        end = to_gdelt_datetime(end_ts.strftime("%Y-%m-%d"))

        print(f"[{event_id}] querying: {query}")
        try:
            resp = query_gdelt(query, start, end)
        except requests.exceptions.RequestException as e:
            print(f"  -> request failed ({type(e).__name__}), skipping this event: {e}")
            print(f"  waiting {SECONDS_BETWEEN_REQUESTS}s before next request...")
            time.sleep(SECONDS_BETWEEN_REQUESTS)
            continue

        print(f"  status: {resp.status_code}")

        attempt = 0
        while resp.status_code == 429 and attempt < MAX_RETRIES_ON_429:
            attempt += 1
            wait = 30 * attempt
            print(f"  -> 429, retry {attempt}/{MAX_RETRIES_ON_429} after {wait}s")
            time.sleep(wait)
            try:
                resp = query_gdelt(query, start, end)
            except requests.exceptions.RequestException as e:
                print(f"  -> request failed on retry ({type(e).__name__}): {e}")
                break
            print(f"  status: {resp.status_code}")

        if resp.status_code == 200:
            try:
                result = resp.json()
                articles = result.get("articles", [])
                with open(f"{RAW_DIR}/{event_id}_gdelt.json", "w") as f:
                    json.dump(result, f, indent=2)
                print(f"  -> {len(articles)} articles saved")
            except json.JSONDecodeError:
                # GDELT sometimes returns 200 with an empty/non-JSON body
                # for zero-result queries -- save the raw text so you can
                # inspect it rather than crashing.
                with open(f"{RAW_DIR}/{event_id}_raw.txt", "w") as f:
                    f.write(resp.text)
                print("  -> got 200 but not valid JSON, raw text saved for inspection")
        elif resp.status_code == 429:
            print("  -> rate limited (429). Wait longer between requests, "
                  "or run this event alone and try again in a minute.")
        else:
            print(f"  -> unexpected status {resp.status_code}, body: {resp.text[:200]}")

        print(f"  waiting {SECONDS_BETWEEN_REQUESTS}s before next request...")
        time.sleep(SECONDS_BETWEEN_REQUESTS)

    print("\nDone. Check data/raw/online/ for each event's article count.")
    print("A 429 for one event does not mean the others failed -- check each file.")


if __name__ == "__main__":
    main()


# --- Reddit note ---
# A 403 from reddit.com/search.json usually means the request is being
# fingerprinted as a bot (missing headers reddit's anti-scraping layer
# expects, or the IP/User-Agent combo is flagged). The fix is not to
# retry harder against the public endpoint -- it's to use Reddit's
# actual API properly:
#   1. Create an app at https://www.reddit.com/prefs/apps (choose "script")
#   2. pip install praw --break-system-packages
#   3. Authenticate with client_id/client_secret/user_agent from step 1
# This is a separate task from the GDELT fix above -- do it once GDELT
# is producing clean results for all 10 events.