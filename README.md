# Beyond Entropy: Reliability-Aware Sample Selection for Test-Time Fake News Detection

## 1. Project Overview

**Research Title:** Beyond Entropy: Reliability-Aware Sample Selection for Test-Time Fake News Detection

This project investigates whether **model uncertainty/entropy alone is sufficient for selecting reliable samples during test-time fake news detection**, and whether additional reliability information can improve sample selection for test-time adaptation.

The project is currently transitioning from **Phase 1 data-source feasibility and collection** toward establishing a reliable, reproducible news-data pipeline using **Media Cloud**.

The initial online-news collection experiments were conducted using **GDELT**. However, repeated HTTP 429 rate-limit responses were encountered during multi-event collection. Because reliable large-scale collection is required before proceeding to annotation and model experiments, **Media Cloud is now being investigated as the primary alternative for online-news search and collection**.

---

# 2. Research Pipeline

The planned end-to-end workflow is:

```text
Event Selection
      ↓
Data Collection
      ↓
Data Cleaning & Event Matching
      ↓
Human Annotation
      ↓
Reliability Scoring (ABS / RS)
      ↓
Statistical Analysis
      ↓
Fake-News Detection Baseline
      ↓
Entropy-Based Sample Selection
      ↓
Reliability-Aware Sample Selection
      ↓
Test-Time Adaptation
      ↓
Ablation & Robustness
      ↓
Final Evaluation
      ↓
Research Paper
```

### Present position

The project is currently between:

```text
Event Selection
      ↓
Data Collection
      ↓
Data-Source Validation
      ↓
Media Cloud Integration  ← CURRENT PHASE
      ↓
Reliable Corpus Construction
      ↓
Annotation
      ↓
Model Experiments
```

The downstream reliability-scoring and test-time-adaptation experiments have **not yet begun**.

---

# 3. Current Status

## Completed

* Research direction and initial methodology defined
* Initial 10-event pilot created
* Event metadata structure created
* GDELT selected and tested as the initial online-news discovery source
* Cebu earthquake pilot successfully retrieved 20 articles
* Returned articles manually inspected
* Language-scope issue identified
* English-only corpus scope selected for the initial study
* Trafilatura tested for article-text extraction
* Three text-heavy articles successfully extracted
* GDELT rate-limit behavior investigated
* HTTP 429 issue confirmed during multi-event collection
* Python virtual environment and basic dependencies configured
* Media Cloud identified as an alternative online-news search/data source
* Media Cloud search output downloaded and inspected
* Initial Media Cloud data is now being evaluated for compatibility with the existing collection pipeline

## Currently in Progress

* Replacing or adapting the GDELT collection layer with Media Cloud
* Understanding the Media Cloud search/result structure
* Mapping Media Cloud fields to the fields required by the existing pipeline
* Testing Media Cloud event-based collection
* Validating article relevance and event matching
* Validating article-text extraction from Media Cloud results
* Establishing a reproducible collection procedure
* Completing and validating the 10-event pilot

## Not Yet Completed

* Final large-scale corpus
* 50–100 event collection
* Human annotation
* Krippendorff's alpha analysis
* ABS model
* RS model
* Fake-news detection model
* Entropy baseline
* Reliability-aware sample selection
* Test-time adaptation experiments
* Ablation studies
* Final statistical evaluation
* Final research paper

---

# 4. Phase 1 — Data Collection and Source Validation

The first phase of the project focuses on establishing a reliable event-based news collection pipeline.

The objective is **not simply to collect as many articles as possible**.

The collection pipeline must produce data that is:

* relevant to the selected event
* associated with a known event ID
* within the defined collection window
* sufficiently diverse in source coverage
* usable for downstream text analysis
* reproducible
* traceable to its original URL/source

Only after this pipeline is stable should the project scale to the larger research corpus.

---

# 5. Event-Based Collection Design

The collection is organized around **specific real-world events** rather than unrelated news articles.

Each event contains:

* `event_id`
* `event_name`
* `category`
* `anchor_date`
* `keywords`
* search query
* notes

The event-based design allows the study to collect different media coverage surrounding the **same underlying event**.

Example:

```text
Event: 2025 Cebu earthquake
Event ID: E005
Category: Disaster
Anchor date: 2025-09-30
Search query: "Cebu earthquake"
```

The event definition is retained with each collected article so that later analysis can compare coverage while preserving event identity.

---

# 6. Initial GDELT Investigation

GDELT was the original online-news discovery source used during Phase 1.

A Cebu earthquake query:

```text
"Cebu earthquake"
```

successfully returned:

```text
20 articles
```

The results were saved as:

```text
data/raw/online/E005_gdelt.json
```

The returned articles included different types of event coverage, including:

* death-toll updates
* scientific explanations
* government response
* international responses
* relief efforts
* human-interest stories

This demonstrated that event-based online-news discovery was technically feasible.

---

# 7. GDELT Rate-Limit Problem

During multi-event collection, GDELT repeatedly returned:

```text
HTTP 429
Too Many Requests
```

Different request-spacing strategies were tested, including:

```text
6 seconds
15 seconds
30 seconds
```

Limited retries were also introduced.

Some events eventually succeeded after retrying, while others continued to receive 429 responses or experienced connection timeouts.

### Important methodological rule

A rate-limit response must never be interpreted as an absence of news coverage.

```text
429 ≠ zero articles
```

A successful search response is required before making a statement about article availability.

### Current decision

Because the research requires a reproducible collection procedure before scaling to a larger corpus, the project is now investigating **Media Cloud as the replacement/alternative online-news search layer**.

GDELT therefore remains part of the project's **initial feasibility investigation**, but it is no longer the preferred collection path while the Media Cloud pipeline is being evaluated.

---

# 8. Media Cloud — Current Phase

Media Cloud is now being investigated as the next online-news collection source.

The current objective is to determine whether Media Cloud can provide the information required by the downstream research pipeline.

The investigation includes:

```text
Media Cloud Search
      ↓
Search Results
      ↓
Article Metadata
      ↓
Event Matching
      ↓
Article URL
      ↓
Article Text Extraction
      ↓
Cleaning / Deduplication
      ↓
Research Corpus
```

The initial Media Cloud search data has been downloaded and inspected.

The next task is to establish the mapping between Media Cloud results and the fields currently expected by the project.

---

# 9. Media Cloud Field Validation

The existing downstream pipeline requires article-level information such as:

* event ID
* article title/headline
* source/domain
* publication date
* article URL
* search/event information
* article text where available

The Media Cloud integration will therefore be evaluated based on whether these fields can be obtained consistently.

The integration should use a normalization layer rather than tightly coupling the rest of the project to Media Cloud's raw response format.

Conceptually:

```text
Media Cloud Response
        ↓
Normalization Layer
        ↓
Standard Article Record
        ↓
Existing Research Pipeline
```

This makes it possible to change the news source later without rewriting the entire research system.

---

# 10. Language Scope

The Cebu pilot exposed a multilingual-data issue.

Some returned articles were not in English.

Because the initial linguistic analysis and model development are English-oriented, the current corpus scope is:

> **English-language articles for the initial research study.**

Non-English articles will be filtered from the primary corpus and documented as a dataset limitation.

Language filtering should occur during the data-cleaning stage rather than silently discarding records without documentation.

---

# 11. Article Text Extraction

The research requires article text for later linguistic and reliability analysis.

**Trafilatura** was tested as the initial article-text extraction method.

Three text-heavy articles were successfully extracted during the GDELT pilot:

| Article source              | Extracted characters |
| --------------------------- | -------------------: |
| Rappler — fault explanation |                6,634 |
| Rappler — death toll report |                1,670 |
| Philstar — tent city report |                1,660 |

The basic extraction pipeline has therefore been demonstrated:

```text
News Search
    ↓
Article URL
    ↓
Article Page
    ↓
Trafilatura
    ↓
Article Body Text
```

However, extraction success must still be validated across a larger and more diverse set of sources before the pipeline is considered production-ready.

---

# 12. Data Cleaning Requirements

Before the corpus is used for annotation or modeling, the collection pipeline must handle:

### Language filtering

Keep the initial research corpus English-only.

### Duplicate removal

Multiple search results may point to the same article or syndicated content.

### Event matching

Articles must actually relate to the target event.

### Date validation

Articles must fall within the defined collection window.

### URL validation

The original article URL should be preserved.

### Source tracking

The publication/source domain should be retained.

### Extraction validation

Articles with missing or unusable text should be recorded rather than silently removed.

---

# 13. Standard Article Record

Regardless of whether the article originates from GDELT, Media Cloud, or another source, the project should normalize it into a common structure.

A target structure is:

```text
event_id
event_name
title
source
domain
publication_date
url
language
query
article_text
collection_source
collection_timestamp
```

This provides a stable interface for the downstream research pipeline.

---

# 14. Current Technical Environment

The project is being developed locally using VS Code.

Development environment:

```text
Python 3.14.7
```

A Python virtual environment is used for the project.

The basic environment has been configured with packages including:

```text
requests
pandas
numpy
python-dateutil
tzdata
certifi
urllib3
idna
charset_normalizer
trafilatura
```

---

# 15. Current Scripts

The project has used the following Phase 1 scripts:

```text
collect_gdelt.py
test_gdelt.py
test_extraction.py
inspect_gdelt.py
```

These scripts were primarily created for the GDELT feasibility stage.

As the project transitions to Media Cloud, the collection layer should be reorganized so that the news-source implementation is separated from the common data-processing pipeline.

A future structure may look like:

```text
collect_mediacloud.py
normalize_articles.py
clean_articles.py
extract_article_text.py
validate_collection.py
```

The exact structure will be finalized after the Media Cloud integration is tested.

---

# 16. Current Project Architecture

The intended architecture is:

```text
                ┌───────────────┐
                │ Event List    │
                └───────┬───────┘
                        ↓
              ┌───────────────────┐
              │ News Source Layer │
              │                   │
              │ Media Cloud       │
              │ GDELT (legacy)    │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Normalization     │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Cleaning          │
              │ Deduplication     │
              │ Event Matching    │
              │ Language Filter   │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Article Text      │
              │ Extraction        │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Research Corpus   │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Human Annotation  │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ ABS / RS          │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Fake-News Model   │
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ Entropy vs        │
              │ Reliability       │
              │ Selection         │
              └───────────────────┘
```

---

# 17. Immediate Next Steps

## Step 1 — Complete Media Cloud integration

Determine:

* how searches are performed
* what fields are returned
* how article URLs are represented
* how dates are represented
* how sources/domains are represented
* how search results are paginated
* what limits exist
* how reproducible the search process is

---

## Step 2 — Build a normalized article format

Convert Media Cloud output into the project's standard article record.

Do not make the downstream research code depend directly on Media Cloud's raw schema.

---

## Step 3 — Re-run the 10-event pilot

Use the same event definitions where possible.

For each event:

```text
Search
 ↓
Collect
 ↓
Normalize
 ↓
Filter English
 ↓
Remove duplicates
 ↓
Validate event relevance
 ↓
Extract text
 ↓
Store raw + cleaned data
```

---

## Step 4 — Validate the pilot

Measure:

* number of search results
* relevant article count
* English article count
* duplicate count
* text-extraction success rate
* source diversity
* date-window compliance
* failed URLs

This will provide evidence for whether the Media Cloud pipeline is suitable for scaling.

---

## Step 5 — Only then scale

The intended progression remains:

```text
10 events
   ↓
25 events
   ↓
50–100 events
```

Scaling should happen only after the 10-event pipeline is reproducible.

---

# 18. Future Research Stages

Once the corpus is stable:

### Human Annotation

Develop the annotation codebook and annotate a representative subset using multiple annotators.

### Inter-Annotator Agreement

Measure agreement using appropriate statistical methods, including Krippendorff's alpha where applicable.

### ABS

Develop and validate the planned reliability-related score.

### RS

Develop and validate the reasoning/source-related score.

### Statistical Analysis

Study relationships among:

* ABS
* RS
* engagement
* medium
* topic
* event

### Fake-News Detection Baseline

Develop and evaluate the base fake-news detection model.

### Entropy Baseline

Implement entropy-based sample selection for test-time adaptation.

### Reliability-Aware Selection

Introduce reliability information into the sample-selection strategy.

### Ablation

Remove individual reliability components to determine their contribution.

### Robustness

Evaluate whether findings remain stable under alternative settings and held-out data.

---

# 19. What Has NOT Been Demonstrated Yet

The following are still hypotheses or future experiments:

* that Media Cloud is superior to GDELT
* that the final corpus will contain a particular number of usable articles
* that ABS is predictive
* that RS is predictive
* that entropy is insufficient
* that reliability-aware selection improves test-time adaptation
* that the proposed method outperforms entropy-based selection

These claims should **not** be made until supported by experimental evidence.

---

# 20. Present Research Status

> **The project has completed the initial data-collection feasibility stage using GDELT and has identified intermittent HTTP 429 rate limiting as a major obstacle to reliable multi-event collection. The current phase is therefore focused on integrating and validating Media Cloud as an alternative online-news search source, while preserving a standardized article format and the existing downstream research architecture. The immediate objective is to complete and validate the 10-event pilot before scaling the corpus and proceeding to annotation, reliability scoring, and test-time adaptation experiments.**

---

# 21. Current Priority

The immediate priority is:

```text
Media Cloud
     ↓
10-event pilot
     ↓
Normalization
     ↓
Cleaning
     ↓
Event matching
     ↓
Article extraction
     ↓
Validation
     ↓
Stable corpus
```

**Do not move to ABS, RS, entropy, or test-time adaptation experiments until the data pipeline is sufficiently stable.**
