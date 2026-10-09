# GDELT and Media Cloud Source Composition

## Findings

The existing event-window retrievals show different source compositions and volumes. The counts describe retrieved datasets, not comparative real-world coverage.

| Event | Records GDELT / MC | Domains GDELT / MC | Shared domains / URLs | Top-five share GDELT / MC | Collection status |
|---|---:|---:|---:|---:|---|
| E001 | 200 / 110 | 190 / 25 | 4 / 3 | 5.50% / 47.27% | GDELT_CAP |
| E002 | 200 / 68 | 53 / 18 | 1 / 1 | 39.00% / 80.88% | GDELT_CAP |
| E003 | 20 / 200 | 16 / 35 | 2 / 3 | 45.00% / 43.00% | MEDIACLOUD_CAP |
| E004 | 0 / 0 | 0 / 0 | 0 / 0 | n/a | TESTED_ZERO_RESULT |
| E005 | 30 / 76 | 17 / 18 | 0 / 0 | 60.00% / 73.68% | NORMAL |
| E006 | 135 / 78 | 101 / 29 | 11 / 19 | 15.56% / 42.31% | NORMAL |
| E007 | 20 / 20 | 15 / 12 | 0 / 0 | 50.00% / 65.00% | NORMAL |
| E008 | 200 / 29 | 115 / 24 | 5 / 5 | 17.50% / 34.48% | GDELT_CAP |
| E009 | 200 / 200 | 148 / 35 | 6 / 7 | 11.50% / 47.00% | BOTH_CAP |
| E010 | 20 / 23 | 16 / 18 | 0 / 0 | 45.00% / 43.48% | NORMAL |

Top-five shares are the fraction of each system's retrieved records attributed to its five most frequent domains. They measure within-sample concentration, not coverage.

## Language Composition

Labels and counts below are reported as stored; `English` and `en` have not been silently merged.

| Event | GDELT languages | Media Cloud languages |
|---|---|---|
| E001 | English 200 | en 110 |
| E002 | English 193; Bengali 1; Hindi 2; Marathi 3; Telugu 1 | en 68 |
| E003 | English 10; French 7; Spanish 3 | en 200 |
| E004 | No records; GDELT file absent | No records; Media Cloud CSV present |
| E005 | English 26; Japanese 1; Russian 3 | en 76 |
| E006 | English 132; Arabic 3 | en 78 |
| E007 | English 20 | en 20 |
| E008 | English 200 | en 23; es 6 |
| E009 | English 168; Spanish 30; Japanese 2 | en 167; es 32; se 1 |
| E010 | English 20 | en 18; es 5 |

Reported language populations differ, notably for E003 and E008. The Media Cloud value `se` in E009 is retained as recorded and should be validated before interpreting it.

## Source Composition and Overlap

- GDELT is much more diffuse in several events: E001 has 190 domains for 200 records, E006 has 101 for 135, and E009 has 148 for 200. Its top-five share is below 20% for E001, E006, E008, and E009.
- Media Cloud is more concentrated in seven of the nine events where both systems returned records. `inquirer.com` is its top domain for E001 (23 records), E002 (41), E003 (49), E005 (44), E007 (7), and E009 (36).
- E005 illustrates the difference: GDELT's top domains are `rappler.com` (7), `philstar.com` (6), `interaksyon.philstar.com` (2), `thestar.com.my` (2), and `bbc.com` (1). Media Cloud's are `inquirer.com` (44), `bostonglobe.com` (4), `newsday.com` (4), `baltimoresun.com` (2), and `bostonherald.com` (2). No domains or normalized URLs overlap.
- E002 also has sharply different source mixes: GDELT's top domains are Indian outlets (`news18.com`, `aninews.in`, `livemint.com`, `news.webindia123.com`, `hindustantimes.com`); Media Cloud is led by `inquirer.com` (41 of 68 records).
- E006 has the largest observed overlap: 11 shared domains and 19 normalized URLs. E005, E007, and E010 have no shared domains or URLs.

The full domain counts and actual shared/exclusive domain names are in [domain_summary.csv](data/processed/source_comparison/domain_summary.csv) and [domain_overlap.csv](data/processed/source_comparison/domain_overlap.csv). Language counts are in [language_summary.csv](data/processed/source_comparison/language_summary.csv); event-level request-limit flags are in [event_summary.csv](data/processed/source_comparison/event_summary.csv).

## Interpretation and Limits

- A result of 200 means the request limit was reached, not that exactly 200 articles existed. E001, E002, and E008 hit the GDELT limit; E003 hit the Media Cloud limit; E009 hit both.
- E004 is only a tested Media Cloud query/window zero result. Its GDELT JSON is missing, so this is not a valid two-source zero-result comparison and is not evidence that the event lacked coverage.
- Domain overlap uses normalized hostnames and preserves subdomains; it may count two subdomains of the same publisher separately. URL overlap is a normalized URL match, not a story-level or syndication match.
- The recurring Media Cloud domains may reflect its indexed outlet population, syndication, or query/relevance behavior. Domain statistics alone cannot tell which explanation applies.
- Source, language, event, and syndication differences can become confounds in the ABS research. Preserve source provenance, harmonize language codes, and avoid duplicate or syndicated stories crossing evaluation splits.

## Next Research Step

Audit existing records for event relevance, language, publisher attribution/location, syndication, and duplicate stories. Prioritize E002, E003, E005, E007, and E008, with E006 as a higher-overlap comparison. This can test whether the observed differences reflect complementary source populations or relevance and syndication artifacts. No source should be designated primary based on these descriptive counts alone.

The analysis implementation is [analyze_source_composition.py](analyze_source_composition.py); it reads the existing local files and does not call either collection API.
