"""Summarize source composition from the existing GDELT and Media Cloud files.

Run from the project root with:
    python analyze_source_composition.py

The output describes retrievals, not relative real-world coverage. In particular,
the E004 zero-result label applies to the tested Media Cloud query/window only.
"""

import csv
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


PROJECT_DIR = Path(__file__).resolve().parent
GDELT_DIR = PROJECT_DIR / "data" / "raw" / "online"
MEDIACLOUD_DIR = GDELT_DIR / "mediacloud"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed" / "source_comparison"
EVENT_IDS = ["E{:03d}".format(number) for number in range(1, 11)]

COLLECTION_STATUS = {
    "E001": "GDELT_CAP",
    "E002": "GDELT_CAP",
    "E003": "MEDIACLOUD_CAP",
    "E004": "TESTED_ZERO_RESULT",
    "E005": "NORMAL",
    "E006": "NORMAL",
    "E007": "NORMAL",
    "E008": "GDELT_CAP",
    "E009": "BOTH_CAP",
    "E010": "NORMAL",
}
E004_STATUS_NOTE = (
    "Classification refers only to the tested Media Cloud query/window; "
    "it is not evidence of total real-world event coverage."
)

# The collectors request at most 200 records per call.
# A result of exactly 200 therefore means the requested limit was reached,
# not that exactly 200 stories exist in the underlying source population.
REQUEST_LIMIT = 200


def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def url_host(url):
    """Return a normalized hostname, including for URLs without a scheme."""
    value = clean_text(url)
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else "//{}".format(value))
    host = (parsed.hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def normalize_url(url):
    """Normalize URLs for exact URL-overlap comparison."""
    value = clean_text(url)
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else "//{}".format(value))
    host = url_host(value)
    if not host:
        return ""
    path = parsed.path.rstrip("/").lower()
    return "{}{}".format(host, path)


def load_gdelt(path):
    if not path.exists():
        return [], False

    with path.open("r", encoding="utf-8") as source_file:
        payload = json.load(source_file)

    if isinstance(payload, dict):
        records = (
            payload.get("articles")
            or payload.get("results")
            or payload.get("data")
            or []
        )
    elif isinstance(payload, list):
        records = payload
    else:
        records = []

    return records, True


def load_mediacloud(path):
    if not path.exists():
        return [], False
    with path.open("r", encoding="utf-8-sig", newline="") as source_file:
        return list(csv.DictReader(source_file)), True


def summarize_source(event_id, source_name, records, file_present, url_field="url"):
    domains = Counter()
    languages = Counter()
    urls = set()

    for record in records:
        url = clean_text(record.get(url_field))

        # Media Cloud exports may expose the source URL as media_url.
        if not url and source_name == "Media Cloud":
            url = clean_text(record.get("media_url"))

        domain = url_host(url)
        normalized = normalize_url(url)
        if domain:
            domains[domain] += 1
        if normalized:
            urls.add(normalized)
        language = clean_text(record.get("language"))
        if language:
            languages[language] += 1

    ranked_domains = sorted(domains.items(), key=lambda item: (-item[1], item[0]))
    record_count = len(records)
    top_five_count = sum(count for _, count in ranked_domains[:5])
    top_one_count = ranked_domains[0][1] if ranked_domains else 0
    summary = {
        "event_id": event_id,
        "source": source_name,
        "collection_status": COLLECTION_STATUS[event_id],
        "status_note": E004_STATUS_NOTE if event_id == "E004" else "",
        "source_file_present": file_present,
        "hit_request_limit": record_count >= REQUEST_LIMIT,
        "total_records": record_count,
        "unique_urls": len(urls),
        "unique_domains": len(domains),
        "top1_domain": ranked_domains[0][0] if ranked_domains else "",
        "top1_domain_records": top_one_count,
        "top1_domain_share_pct": round(top_one_count / record_count * 100, 2) if record_count else 0,
        "top5_domain_records": top_five_count,
        "top5_domain_share_pct": round(top_five_count / record_count * 100, 2) if record_count else 0,
        "top10_domains": "; ".join(
            "{}:{}".format(domain, count) for domain, count in ranked_domains[:10]
        ),
        "domains": domains,
        "urls": urls,
        "languages": languages,
        "ranked_domains": ranked_domains,
    }
    return summary


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
    domain_summary_rows = []
    domain_overlap_rows = []
    language_summary_rows = []
    event_summary_rows = []

    for event_id in EVENT_IDS:
        gdelt_records, gdelt_present = load_gdelt(
            GDELT_DIR / "{}_gdelt.json".format(event_id)
        )
        mc_records, mc_present = load_mediacloud(
            MEDIACLOUD_DIR / "{}_mediacloud.csv".format(event_id)
        )
        gdelt = summarize_source(event_id, "GDELT", gdelt_records, gdelt_present)
        mediacloud = summarize_source(event_id, "Media Cloud", mc_records, mc_present)

        event_summary_rows.append(
            {
                "event_id": event_id,
                "collection_status": COLLECTION_STATUS[event_id],
                "status_note": E004_STATUS_NOTE if event_id == "E004" else "",
                "gdelt_file_present": gdelt["source_file_present"],
                "mediacloud_file_present": mediacloud["source_file_present"],
                "gdelt_records": gdelt["total_records"],
                "mediacloud_records": mediacloud["total_records"],
                "gdelt_hit_request_limit": gdelt["hit_request_limit"],
                "mediacloud_hit_request_limit": mediacloud["hit_request_limit"],
                "gdelt_unique_domains": gdelt["unique_domains"],
                "mediacloud_unique_domains": mediacloud["unique_domains"],
                "shared_domain_count": len(
                    gdelt["domains"].keys() & mediacloud["domains"].keys()
                ),
                "url_overlap_count": len(gdelt["urls"] & mediacloud["urls"]),
            }
        )

        for source in (gdelt, mediacloud):
            for rank, (domain, count) in enumerate(source["ranked_domains"], start=1):
                summary_row = {
                    key: value for key, value in source.items()
                    if key not in {"domains", "urls", "languages", "ranked_domains"}
                }
                summary_row.update(
                    {
                        "domain": domain,
                        "domain_records": count,
                        "domain_rank": rank,
                        "is_top_10": rank <= 10,
                    }
                )
                domain_summary_rows.append(summary_row)
            if not source["ranked_domains"]:
                summary_row = {
                    key: value for key, value in source.items()
                    if key not in {"domains", "urls", "languages", "ranked_domains"}
                }
                summary_row.update(
                    {
                        "domain": "",
                        "domain_records": 0,
                        "domain_rank": "",
                        "is_top_10": False,
                    }
                )
                domain_summary_rows.append(summary_row)

        shared_domains = gdelt["domains"].keys() & mediacloud["domains"].keys()
        domain_relations = {}
        domain_relations.update((domain, "SHARED") for domain in shared_domains)
        domain_relations.update(
            (domain, "GDELT_ONLY")
            for domain in gdelt["domains"].keys() - shared_domains
        )
        domain_relations.update(
            (domain, "MEDIACLOUD_ONLY")
            for domain in mediacloud["domains"].keys() - shared_domains
        )
        for domain, relation in sorted(domain_relations.items()):
            domain_overlap_rows.append(
                {
                    "event_id": event_id,
                    "collection_status": COLLECTION_STATUS[event_id],
                    "status_note": E004_STATUS_NOTE if event_id == "E004" else "",
                    "domain": domain,
                    "domain_relationship": relation,
                    "gdelt_domain_records": gdelt["domains"].get(domain, 0),
                    "mediacloud_domain_records": mediacloud["domains"].get(domain, 0),
                    "gdelt_unique_domains": len(gdelt["domains"]),
                    "mediacloud_unique_domains": len(mediacloud["domains"]),
                    "shared_domain_count": len(shared_domains),
                    "url_overlap_count": len(gdelt["urls"] & mediacloud["urls"]),
                    "gdelt_records": gdelt["total_records"],
                    "mediacloud_records": mediacloud["total_records"],
                    "gdelt_file_present": gdelt["source_file_present"],
                    "mediacloud_file_present": mediacloud["source_file_present"],
                }
            )
        if not domain_relations:
            domain_overlap_rows.append(
                {
                    "event_id": event_id,
                    "collection_status": COLLECTION_STATUS[event_id],
                    "status_note": E004_STATUS_NOTE if event_id == "E004" else "",
                    "domain": "",
                    "domain_relationship": "NO_DOMAINS",
                    "gdelt_domain_records": 0,
                    "mediacloud_domain_records": 0,
                    "gdelt_unique_domains": 0,
                    "mediacloud_unique_domains": 0,
                    "shared_domain_count": 0,
                    "url_overlap_count": len(gdelt["urls"] & mediacloud["urls"]),
                    "gdelt_records": gdelt["total_records"],
                    "mediacloud_records": mediacloud["total_records"],
                    "gdelt_file_present": gdelt["source_file_present"],
                    "mediacloud_file_present": mediacloud["source_file_present"],
                }
            )

        for source in (gdelt, mediacloud):
            language_counts = source["languages"] or {"NO_LANGUAGE_RECORDED": 0}
            for language, count in sorted(language_counts.items()):
                language_summary_rows.append(
                    {
                        "event_id": event_id,
                        "source": source["source"],
                        "collection_status": COLLECTION_STATUS[event_id],
                        "status_note": E004_STATUS_NOTE if event_id == "E004" else "",
                        "source_file_present": source["source_file_present"],
                        "total_records": source["total_records"],
                        "language": language,
                        "language_records": count,
                    }
                )

    domain_fields = [
        "event_id", "source", "collection_status", "status_note", "source_file_present",
        "hit_request_limit", "total_records", "unique_urls", "unique_domains", "top1_domain",
        "top1_domain_records", "top1_domain_share_pct", "top5_domain_records",
        "top5_domain_share_pct", "top10_domains", "domain", "domain_records",
        "domain_rank", "is_top_10",
    ]
    overlap_fields = [
        "event_id", "collection_status", "status_note", "domain", "domain_relationship",
        "gdelt_domain_records", "mediacloud_domain_records", "gdelt_unique_domains",
        "mediacloud_unique_domains", "shared_domain_count", "url_overlap_count",
        "gdelt_records", "mediacloud_records", "gdelt_file_present", "mediacloud_file_present",
    ]
    language_fields = [
        "event_id", "source", "collection_status", "status_note", "source_file_present",
        "total_records", "language", "language_records",
    ]
    event_fields = [
        "event_id", "collection_status", "status_note",
        "gdelt_file_present", "mediacloud_file_present",
        "gdelt_records", "mediacloud_records",
        "gdelt_hit_request_limit", "mediacloud_hit_request_limit",
        "gdelt_unique_domains", "mediacloud_unique_domains",
        "shared_domain_count", "url_overlap_count",
    ]

    write_csv(OUTPUT_DIR / "domain_summary.csv", domain_summary_rows, domain_fields)
    write_csv(OUTPUT_DIR / "domain_overlap.csv", domain_overlap_rows, overlap_fields)
    write_csv(OUTPUT_DIR / "language_summary.csv", language_summary_rows, language_fields)
    write_csv(OUTPUT_DIR / "event_summary.csv", event_summary_rows, event_fields)

    print("Wrote source-composition analysis to {}".format(OUTPUT_DIR))
    print("The tables describe retrievals; record counts are not comparative coverage percentages.")
    print("A 200-record result is flagged as hitting the request limit, not as an exact coverage count.")
    print("E004 TESTED_ZERO_RESULT applies only to the tested Media Cloud query/window.")


if __name__ == "__main__":
    main()