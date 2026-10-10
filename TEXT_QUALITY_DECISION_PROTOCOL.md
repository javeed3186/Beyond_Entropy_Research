# Text Quality Decision Protocol

**Project:** Beyond Entropy Research
**Phase:** 3 — Text Extraction and Data Quality Auditing
**Status:** Draft for pilot review
**Prepared:** 2026-10-10

## 1. Purpose

This protocol documents how extracted article text will be assessed before the pilot dataset is finalized and used for annotation or ABS/RS scoring.

No original article record will be deleted solely because an automated quality check flags it.

## 2. Current Pilot Audit

The current extraction and quality reports show:

- Inventory URLs: 969
- Successfully extracted text records: 759
- Overall extraction coverage: 78.3%
- Records marked for quality review: 290
- Short-text records under 1,000 characters: 27
- Suspicious-title flags: 19
- Records in duplicate-text groups: 248
- Duplicate-text groups: 31
- Records beyond the first occurrence of a normalized text: 217
- Unique unresolved URLs: 210
- Events represented in the current inventory: 9
- E004: no available GDELT raw file in the current collection

These figures describe the current collected dataset. They do not establish complete media coverage or validated ABS/RS scores.

## 3. Review Rules

### 3.1 Short text

Text under 1,000 characters is flagged for review, not automatically excluded.

Review whether the text contains substantive event-related reporting, an incomplete excerpt, a subscription prompt, or mostly non-article content.

### 3.2 Subscription and boilerplate signals

A subscription prompt, login message, author biography, or similar boilerplate signal triggers review.

A signal alone is not sufficient to exclude an article. Record the observed issue and the decision made.

### 3.3 Suspicious titles

Titles containing terms such as live updates, photos, videos, archives, or generic news headlines are flagged for review.

The title flag alone does not establish that the extracted article text is unusable.

### 3.4 Duplicate normalized text

The current audit normalizes text by lowercasing and collapsing whitespace.

Retain the original records and record duplicate-group identifiers. Do not automatically delete duplicate-text records.

For later analysis, document whether results are calculated at URL level, normalized-text-group level, or both. Identical normalized text does not necessarily establish that two URLs are the same underlying article.

### 3.5 Same-domain duplicate-text cases

The four identified groups involving Benzinga, The Hindu BusinessLine, Variety, and Gold Derby are recorded in `same_domain_duplicate_review.csv`.

Their causes are not yet confirmed. Keep them under review until the source records and text are checked.

### 3.6 Extraction failures

The original `extraction_failures.csv` remains the historical failure log.

Use `unresolved_extraction_failures.csv` for the current unresolved-failure review. Distinguish failure-log rows from unique URLs.

Do not interpret a fetch failure as proof that an article does not exist or that an event received no coverage.

### 3.7 Missing event data

E004 is not represented in the current article inventory because its GDELT raw file was unavailable.

Keep this collection gap explicit. Do not interpret missing data as zero media coverage.

## Duplicate-Text Analysis Procedure

The current duplicate-text audit uses lowercase text with whitespace collapsed.
It identifies exact normalized-text matches, not every near-duplicate story.

For the pilot:

1. Preserve every original extracted record and its URL.
2. Preserve `normalized_text_group_id` and duplicate indicators in audit outputs.
3. Do not automatically delete records solely because their normalized text matches.
4. Report URL-level record counts separately from unique normalized-text counts.
5. When evaluating ABS/RS scores, compare URL-level results with a sensitivity analysis that gives each normalized-text group one contribution.
6. Document how records with incomplete text or non-article material are handled before scoring.
7. Treat same-domain duplicate cases as unresolved until their causes have been verified.

Current audit figures:
- Extracted records: 759
- Unique normalized texts: 542
- Duplicate-text groups: 31
- Records in duplicate groups: 248
- Records beyond the first occurrence in each group: 217

These figures describe the current extracted dataset. They do not establish the number of distinct underlying news stories.

## 4. Review Statuses

Use the following statuses when documenting individual records:

- `retain`: text appears suitable for the intended analysis after review.
- `retain_with_flag`: retain the record but preserve a documented limitation.
- `review_incomplete`: likely incomplete extraction; inspect before scoring.
- `review_nonarticle_content`: non-article material may affect the text.
- `duplicate_text`: text matches another normalized-text group; preserve the record and group identifier.
- `exclude_with_reason`: exclude only after a documented, reproducible reason is established.
- `unresolved`: insufficient evidence to make a final decision.

Do not mark a record as reviewed merely because it appears in an audit report.

## 5. Decision Log

For each reviewed record, preserve, where available:

- Event ID
- URL and domain
- Review status
- Reason and supporting evidence
- Reviewer and review date
- Any final exclusion decision and justification

## Manual-Review Resolution Gate

Before the pilot text dataset is frozen for annotation or scoring:

1. Review every entry in `data/processed/manual_extraction_review.csv`.
2. Assign a final status using the review-status definitions in this protocol.
3. For `review_incomplete` and `review_nonarticle_content` records, decide whether the available text is suitable for the planned analysis, should be retained with a limitation, or should be excluded with a documented reason.
4. For `unresolved` records, either obtain sufficient evidence to decide or explicitly retain the unresolved status and exclude the record from analyses that require verified article text.
5. Record the decision and rationale. Do not infer completeness solely from text length or a boilerplate flag.
6. Preserve the original extracted text and maintain traceability between the review decision and the source URL.

Manual-review queue: six records. All six have documented review statuses and reasons in data/processed/manual_extraction_review.csv. Three are marked review_incomplete, two retain_with_flag, and one review_nonarticle_content. These are documented extraction-quality decisions; they do not certify article completeness. No records were automatically excluded.

## 6. Completion Criteria

Phase 3 can be closed when:

1. The extraction and quality reports are saved and their totals have been checked.
2. Short-text, boilerplate, suspicious-title, and duplicate-text handling rules are documented.
3. Priority manual-review records have decisions or explicit unresolved statuses.
4. Extraction failures and the E004 data gap are documented.
5. The procedure for producing the finalized pilot text dataset is reproducible.
6. Original records remain traceable, and exclusions are documented rather than silently applied.

## 7. Limitations

The current audit does not demonstrate that all extracted texts are complete, that normalized-text groups equal unique news stories, or that the collected records represent the full media environment.

Human annotation and evaluation of ABS/RS scoring remain subsequent research tasks.


## Manual Review Findings - 2026-10-10

The six priority records were inspected using their exact URLs in
`data/processed/article_text.csv`. Review statuses and supporting reasons
are recorded in `data/processed/manual_extraction_review.csv`. Original
article-text records were not deleted or rewritten.

| Event | Domain | Decision | Evidence and limitation |
|---|---|---|---|
| E006 | manilatimes.net | `review_incomplete` | 536 characters; two substantive sentences followed by subscription material. |
| E006 | sitkasentinel.com | `review_incomplete` | 554 characters; extraction explicitly states the full item is subscriber-only. |
| E006 | winnipegfreepress.com | `retain_with_flag` | 2,253 characters; substantive ending is present, but subscription prompts are mixed into the extraction. Completeness is not independently confirmed. |
| E002 | independent.co.uk | `retain_with_flag` | 5,669 characters; substantive reporting and background appear through the ending. Membership prompts precede the article. Completeness is not independently confirmed. |
| E008 | mashable.com | `review_nonarticle_content` | 3,952 characters; article text is followed by a substantial author biography. The source record is retained. |
| E009 | manilatimes.net | `review_incomplete` | 426 characters; one substantive sentence followed by subscription material. |

These are extraction-quality judgments based on the captured text, not
proof of the complete contents of the original webpages. The two
`retain_with_flag` decisions indicate apparent substantive usability,
not verified completeness. No records were automatically excluded.

The protocol backup is stored under `data/processed/backups`.


## Reproducible Summary Generation

The Phase 3 event-level quality-control summary is generated by:

`scripts/build_phase3_quality_control_summary.py`

The script reads these inputs from `data/processed/`:

- `article_inventory.csv`
- `article_text.csv`
- `article_quality_report.csv`
- `unresolved_extraction_failures.csv`

Preview the calculations without replacing the saved summary:

```powershell
.\venv\Scripts\python.exe scripts/build_phase3_quality_control_summary.py
```

Write the regenerated summary only after reviewing the preview:

```powershell
.\venv\Scripts\python.exe scripts/build_phase3_quality_control_summary.py --write
```

Before using write mode, back up the current
`phase3_quality_control_summary.csv` into `data/processed/backups/`.
The script checks required columns, duplicate URLs in the extracted-text
and quality-report files, and whether their URL sets agree.

The summary reports inventory and extraction counts, quality flags,
normalized-text duplicate statistics, and unresolved failure rows and
unique unresolved URLs. The current verified totals are 969 inventory
URLs, 759 extracted records, 290 `needs_review` records, 27 short-text
records, 19 suspicious-title records, 217 records beyond the first
occurrence in normalized-text duplicate groups, 247 unresolved failure
rows, and 210 unique unresolved URLs.

This summary is an extraction and quality-control report, not evidence
that every article is complete, that every normalized-text group equals
one underlying story, or that the pilot captures the full media
environment.


## Reproducible Pilot Text Dataset

The review-ready pilot dataset is generated by:

`scripts/build_pilot_text_dataset.py`

It reads `article_text.csv`, `article_quality_report.csv`, and
`manual_extraction_review.csv` from `data/processed/`. It joins quality
flags and manual-review decisions to extracted text by exact URL, checks
the URL relationships, and retains the source text.

Preview without saving:

```powershell
.\venv\Scripts\python.exe scripts/build_pilot_text_dataset.py
```

Save the review-ready dataset:

```powershell
.\venv\Scripts\python.exe scripts/build_pilot_text_dataset.py --write
```

Output:

`data/processed/pilot_text_dataset_review_ready.csv`

The output preserves all extracted article records and their text. It
does not automatically remove short texts, duplicate-text records,
suspicious titles, subscription prompts, or records marked for manual
review. Quality flags remain available for downstream sensitivity
analysis and documented research decisions.

Derived columns:

- `manual_review_status`: documented review status, or
  `not_manually_reviewed` when no manual decision exists.
- `manual_review_reason`: the recorded rationale for a manually reviewed
  record.
- `manually_reviewed`: whether an exact-URL manual-review match exists.

Validation on 2026-10-10 confirmed 759 output records, 759 unique URLs,
preservation of all source URLs and extracted text, and six exact-URL
manual-review matches. The six statuses were three `review_incomplete`,
two `retain_with_flag`, and one `review_nonarticle_content`.

This is a review-ready dataset, not a claim that every text is complete
or analytically suitable. Before any final analysis, document the
inclusion/exclusion policy and any sensitivity analyses. Human annotation
and ABS/RS scoring evaluation remain separate subsequent research tasks.
