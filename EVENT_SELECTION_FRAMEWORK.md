# Final Event-Sample Selection Framework

## Working Scope

- Candidate pool: 60 events, provisionally 10 per existing category.
- Final sample: target 50 events, with expansion toward 100 only if collection capacity and source coverage support it.
- Study period: 2025-10-09 through 2026-10-08 inclusive. Interpret this as the half-open interval `[2025-10-09 00:00 UTC, 2026-10-09 00:00 UTC)`.
- Geographic scope: global events. Collected news items must be in English, consistent with the project's pilot scope.
- Categories: Politics, Health, Disaster, Technology, Entertainment, and Other. Assign one primary category; use Other only for discrete social, religious, institutional, or cultural events that do not fit the first five categories.
- Pilot rule: E001-E010 are feasibility cases, not members of the final sample. Candidate IDs use `C001` onward and must not reuse pilot IDs.

These are working design decisions for the candidate pool, not claims that the final sample has already been selected.

## Candidate Inclusion

Include a candidate only when all of the following hold:

1. It is a discrete, dateable event or decision, rather than an open-ended issue or an arbitrary point in a continuing story.
2. Its anchor date is corroborated by a primary record or by two independent established news sources. Record the evidence URL(s) in the candidate CSV.
3. A specific event query can be written using names, location, and event-specific terms, without relying on a broad topic term alone.
4. A small, non-comparative preflight confirms retrievable English-language coverage in the planned online-news, social-media, and television sources. Record provider limits and failures; a failed request is not evidence of zero coverage. Until those providers and their access terms are chosen, record `modality_feasibility_status=PENDING` and do not treat the candidate as eligible for final selection.
5. The event falls wholly within the study period and is not one of the ten pilot events.

Exclude events with ambiguous boundaries, no defensible anchor date, insufficient cross-modality feasibility, or a collection window crossing the study-period boundary. Keep exclusions and reasons in a separate audit rather than silently deleting candidates.

## Candidate Discovery and Final Selection

Build the 60-event pool with 10 candidates in each category. Within categories, seek geographic and event-type variety; do not let multiple related developments from one continuing story occupy several slots. Candidate discovery sources are leads only: verify dates and descriptions independently before setting `verification_status` to `VERIFIED`.

After screening, target 50 final events, initially allocating 8 or 9 per category and assigning the remaining slots to categories with eligible candidates, while keeping regional and event-type variety. If fewer than 50 candidates pass, expand the pool before collection. Select among eligible candidates with a recorded, reproducible random draw (seed `20261009`) within category and geographic strata. Do not rank events by observed article volume or apparent source agreement; those are research outcomes and would bias the sample.

Keep the complete candidate pool, exclusions, verification evidence, final-selection flag, and reason for any manual override. Re-run the draw only if eligibility rules change, and record the change.

## Collection Window and Search Terms

For an anchor date `D`, use a seven-day window from `D 00:00 UTC` inclusive to `D + 7 days 00:00 UTC` exclusive. Adapt these boundaries to each provider's date semantics and record the actual request parameters. Use the same event query concepts and time window across modalities, while allowing provider-specific syntax. Store the exact query used per provider; do not silently broaden a query after a failed or low-yield request.

Search terms should include the event's principal names and location, a common alternate name where applicable, and distinguishing terms. Avoid terms that primarily retrieve unrelated recurring topics. Pilot query precision and recall on a small sample before bulk collection.

## Relevance, Matching, and Deduplication

- Treat each modality's records as event-linked only when the item substantively refers to the defined event, not merely a person, place, or broad topic in common.
- Preserve the provider record ID, source, URL or post/broadcast identifier, timestamp, language, query, collection timestamp, and event ID.
- Deduplicate exact URLs and provider IDs first; then flag likely duplicates using normalized title, publisher, and publication time. Preserve cross-source links so syndication and shared stories can be analyzed rather than erased.
- Verify cross-modality event matching against the item itself and a source transcript, caption, post, or equivalent record. A matching keyword alone is insufficient. Retain match decision, reviewer, and reason.
- Keep request errors, rate limits, zero-result responses, and cap-hit flags distinct. Record exclusions and relevance decisions so usable-item counts can be reconstructed.

## Pilot-to-Final Gate

Before scaling, select and document the social-media and television providers, confirm that all collection providers support the intended date-window semantics, document their terms and limits, and test a small sample of candidate events across all planned modalities. The source-composition pilot is descriptive feasibility evidence; it does not establish a preferred source or justify selecting events based on one provider's yield.