# Research Progress

## Completed

- Defined research direction and overall pipeline.
- Created a 10-event pilot across multiple news categories.
- Structured event metadata in `event_list.csv`.
- Tested GDELT for online-news discovery.
- Retrieved and inspected 20 Cebu earthquake articles.
- Identified multilingual results and selected English-only scope for the initial corpus.
- Tested Trafilatura on 3 text-heavy articles across Rappler and Philstar.
- Investigated GDELT HTTP 429 rate limiting using 6s, 15s, and 30s spacing and limited retries.
- Established the local Python/VS Code development environment.

## Current

- Designing the final event sample. A 12-month framework and 60 candidate leads across six categories are drafted; event-source confirmation and social/TV provider feasibility remain pending.

## Planned

1. Verify the 60 candidate leads against primary or independent established sources.
2. Choose social-media and TV providers, then preflight event availability across modalities.
3. Select the final 50–100 events using the documented stratified procedure.
4. Freeze collection and matching rules; collect, clean, deduplicate, and extract the corpus.
5. Human annotation and inter-annotator agreement.
6. Develop and validate ABS/RS.
7. Statistical analysis.
8. Build fake-news detection baseline.
9. Implement entropy-based sample selection.
10. Implement reliability-aware sample selection.
11. Test under test-time adaptation.
12. Run ablation and robustness studies.
13. Perform final evaluation and write the paper.

## Important

Do not present ABS/RS performance, entropy limitations, or superiority of the proposed method as established findings yet. They are hypotheses to be tested.
