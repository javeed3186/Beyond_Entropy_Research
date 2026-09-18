# Beyond Entropy: Reliability-Aware Sample Selection for Test-Time Fake News Detection

## 1. Project Overview

**Research title:** Beyond Entropy: Reliability-Aware Sample Selection for Test-Time Fake News Detection

This project investigates whether **model uncertainty/entropy alone is sufficient for selecting reliable samples during test-time fake news detection**, and whether additional reliability information can improve sample selection for test-time adaptation.

The current work is focused on building and validating the **Phase 1 data-collection pipeline** before moving to annotation, scoring, and model experiments.

---

## 2. Research Pipeline

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

**Important:** Only the Phase 1 feasibility work described below has been completed so far. The later stages are planned, not implemented yet.

---

# 3. Current Status

## Completed

- Research direction and initial methodology defined
- Initial 10-event pilot created
- Event metadata structure created
- GDELT selected and tested for online-news discovery
- Cebu earthquake pilot successfully retrieved 20 articles
- Returned articles manually inspected
- Language-scope issue identified
- English-only corpus scope selected for the initial study
- Trafilatura tested for article-text extraction
- Three text-heavy articles successfully extracted
- GDELT rate-limit behavior investigated
- Python virtual environment and basic dependencies configured

## Currently in Progress

- Establishing a reliable and reproducible GDELT collection procedure
- Completing the 10-event pilot
- Deciding the final collection strategy before scaling

## Not Yet Completed

- Full 50–100 event collection
- Final large-scale corpus
- Human annotation
- Krippendorff's alpha analysis
- ABS model
- RS model
- Fake-news detection model
- Entropy baseline
- Reliability-aware sample selection
- Test-time adaptation experiments
- Ablation studies
- Final statistical evaluation

---

# 4. Completed Phase 1 Work

## 4.1 10-Event Pilot

An initial pilot event list containing 10 events was created.

The pilot covers different categories:

- Politics
- Health
- Disaster
- Technology
- Entertainment
- Other/control-type events

Each event contains:

- `event_id`
- `event_name`
- `category`
- `anchor_date`
- `keywords`
- `gdelt_query`
- `notes`

The current `event_list.csv` is the source file for the pilot.

---

## 4.2 Event-Based Collection Design

The collection is organized around **specific real-world events** instead of collecting unrelated news.

Each event has an anchor date and a seven-day collection window.

Example:

```text
Event: 2025 Cebu earthquake
Event ID: E005
Category: Disaster
Anchor date: 2025-09-30
GDELT query: "Cebu earthquake"
```

The purpose is to obtain different coverage of the **same underlying event** so that later analyses can compare media coverage while controlling for the event itself.

---

# 5. GDELT Testing

GDELT was selected as the initial online-news discovery source.

The collector retrieves article-level metadata such as:

- headline
- source/domain
- date
- article URL

### First successful pilot

The Cebu earthquake query:

```text
"Cebu earthquake"
```

successfully returned:

```text
20 articles
```

These were saved as:

```text
data/raw/online/E005_gdelt.json
```

---

# 6. Evidence: Cebu Earthquake Inspection

The 20 returned articles were inspected manually.

The results included different types of coverage:

- death-toll updates
- scientific explanations
- government response
- international responses
- relief efforts
- human-interest stories

Examples included articles about:

```text
Death toll in strong Cebu earthquake rises to 72
What we know so far about the fault that caused the Cebu earthquake
Marcos orders "tent city" for Cebu quake victims
Singapore expresses condolences over Philippine quake
Apps linking quake victims with rescuers and donors
```

This demonstrated that an event-based GDELT query can produce varied coverage of the same event.

---

# 7. Language-Scope Decision

The Cebu pilot also exposed a multilingual-data issue.

Some of the 20 returned articles were in Russian.

Because the planned linguistic analysis and initial model development are English-oriented, the current project scope is:

> **Use English-language articles for the initial research corpus.**

Non-English articles will be filtered out of the main corpus and documented as a limitation.

---

# 8. Article Text Extraction

GDELT provides article URLs, but later research stages require actual article text.

We tested **Trafilatura** as the article-text extraction method.

Three text-heavy articles were tested:

| Article source | Result |
|---|---:|
| Rappler — fault explanation | 6,634 characters |
| Rappler — death toll report | 1,670 characters |
| Philstar — tent city report | 1,660 characters |

All three tests successfully returned usable article text.

Therefore, the basic pipeline has been validated:

```text
GDELT
  ↓
Article URL
  ↓
Trafilatura
  ↓
Article body text
```

---

# 9. GDELT Rate-Limit Investigation

During multi-event collection, GDELT began returning:

```text
HTTP 429
Too Many Requests
```

This is an API rate-limit response.

Several request-spacing strategies were tested:

```text
6 seconds
   ↓
15 seconds
   ↓
30 seconds
```

Limited retries were also introduced.

### Latest 10-event run

The latest run showed:

```text
E003 → successful after retry
E005 → successful after retry
E007 → successful on first attempt
E008 → successful on first attempt
E010 → successful after retry
```

Several other events continued to receive 429 responses, and one request experienced a connection timeout.

This means:

- GDELT access works
- valid event queries can return relevant results
- multi-event collection is currently affected by intermittent throttling
- reliable large-scale collection has **not yet been established**

This is currently the main Phase 1 technical issue.

---

# 10. Important Methodological Decision

We are **not** treating a 429 response as evidence that an event has no news coverage.

A 429 means the request was rate-limited.

Therefore:

```text
429 ≠ zero articles
```

A successful query is required before making a statement about article availability.

---

# 11. Current Technical Environment

The project is being developed locally using VS Code.

Current project location during development:

```text
D:\Beyond_Entropy_Research
```

A Python virtual environment was created using Python 3.14:

```powershell
py -3.14 -m venv venv
```

The environment was activated with:

```powershell
.\venv\Scripts\Activate.ps1
```

Python was verified:

```powershell
python --version
```

Expected development version used so far:

```text
Python 3.14.7
```

---

# 12. Installed Packages

The current basic environment successfully installed:

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
six
trafilatura
```

The basic installation was verified with:

```powershell
python -c "import requests, pandas; print('All packages OK')"
```

Output:

```text
All packages OK
```

---

# 13. Current Scripts

The project has used the following scripts during Phase 1:

```text
collect_gdelt.py
test_gdelt.py
test_extraction.py
inspect_gdelt.py
```

### `collect_gdelt.py`

Main GDELT pilot collector.

Purpose:

- read the event list
- query GDELT
- use event dates and queries
- save successful GDELT responses
- handle 429 responses
- handle request failures without stopping the entire run

### `test_gdelt.py`

Used for isolated GDELT API testing.

Purpose:

- check whether the API is responding
- inspect HTTP status
- test a single query

### `test_extraction.py`

Used to test article-text extraction.

Purpose:

- download article pages
- extract article text using Trafilatura
- report extracted character count
- show the beginning of extracted text

### `inspect_gdelt.py`

Used to inspect saved GDELT results.

Purpose:

- count returned articles
- display titles
- display source domains
- display dates
- display URLs

---

# 14. Important Commands Used

## Navigate to project

```powershell
cd D:\Beyond_Entropy_Research
```

## Create virtual environment

```powershell
py -3.14 -m venv venv
```

## Activate environment

```powershell
.\venv\Scripts\Activate.ps1
```

## Check Python

```powershell
python --version
```

## Check which Python is being used

```powershell
where.exe python
```

## Install packages

```powershell
python -m pip install requests pandas
```

For article extraction:

```powershell
python -m pip install trafilatura
```

## Test imports

```powershell
python -c "import requests, pandas; print('All packages OK')"
```

## Run GDELT collector

```powershell
python collect_gdelt.py
```

## Run GDELT test

```powershell
python test_gdelt.py
```

## Run extraction test

```powershell
python test_extraction.py
```

## Inspect saved GDELT data

```powershell
python inspect_gdelt.py
```

---

# 15. Current Folder Structure

The project should eventually follow a structure similar to:

```text
Beyond_Entropy_Research/
│
├── README.md
├── event_list.csv
│
├── collect_gdelt.py
├── test_gdelt.py
├── test_extraction.py
├── inspect_gdelt.py
│
├── data/
│   └── raw/
│       ├── online/
│       │   └── E005_gdelt.json
│       │
│       └── social/
│
├── docs/
│   └── research_progress.md
│
└── venv/
```

### Do NOT push `venv/` to GitHub.

It is a local Python environment and should be recreated by each teammate.

---

# 16. GitHub Setup

The repository should contain the research source code and documentation, but not the local virtual environment.

Create a `.gitignore` file containing:

```gitignore
# Python
venv/
__pycache__/
*.py[cod]

# Environment / secrets
.env
.env.*
!.env.example

# IDE
.vscode/

# Temporary files
*.tmp
*.log

# OS
.DS_Store
Thumbs.db
```

If `.vscode/` contains useful shared project configuration, it can be selectively added later. Do not commit personal machine-specific settings or secrets.

---

# 17. Recommended Git Workflow

From the project directory:

```powershell
git init
```

Add files:

```powershell
git add .
```

Check what will be committed:

```powershell
git status
```

Create the first commit:

```powershell
git commit -m "Initial research Phase 1 pipeline"
```

Then connect the GitHub repository:

```powershell
git remote add origin YOUR_GITHUB_REPOSITORY_URL
```

Rename the branch:

```powershell
git branch -M main
```

Push:

```powershell
git push -u origin main
```

**Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual repository URL. Do not commit API keys or credentials.**

---

# 18. How a Teammate Can Continue the Project

After cloning the repository:

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd Beyond_Entropy_Research
```

Create their own environment:

```powershell
py -3.14 -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install requests pandas trafilatura
```

Then inspect the repository:

```powershell
dir
```

Run the appropriate Phase 1 script:

```powershell
python collect_gdelt.py
```

The teammate should read this README before modifying the collector.

---

# 19. Data Integrity Rules

These rules should be followed as the project grows.

### Do not manually invent article counts

Only record an article count after a successful API response.

### Do not treat HTTP 429 as zero results

A 429 is an access/rate-limit issue.

### Keep raw data

Successful raw API responses should be retained for reproducibility.

### Keep the original URL

Every article record should preserve its source URL.

### Keep event identity

Every collected article must remain associated with its event ID.

### Keep collection dates and query information

This will help document how the dataset was constructed.

### Do not silently change the event definition

If an event's anchor date or query changes, document the change.

---

# 20. Planned Work — Next Steps

## Step 1 — Finish Phase 1 pilot

First establish a reliable way to collect the 10 pilot events.

The immediate problem is the GDELT rate limiting.

Do not scale to 100 events until the pilot collection process is stable.

---

## Step 2 — Validate all pilot data

For each event:

- verify relevance
- filter non-English results
- inspect duplicates
- check publication dates
- retrieve article text
- record extraction failures
- check source diversity

---

## Step 3 — Expand the event set

After the pilot:

```text
10 events
   ↓
25 events
   ↓
50–100 events
```

The eventual target is a corpus of several thousand usable items.

---

## Step 4 — Add other modalities

The original research design includes:

```text
Social
Online/Print
TV
```

The availability and coverage of each modality must be tested rather than assumed.

---

## Step 5 — Human Annotation

Create an annotation codebook for the reliability-related dimensions.

A representative subset will be annotated by multiple annotators.

Inter-annotator agreement will then be measured.

---

## Step 6 — Develop ABS and RS

The planned research pipeline contains:

**ABS — a score intended to capture aspects such as sensationalism/framing/structural distortion**

and

**RS — a reasoning-related score based on linguistic/source-related features.**

The exact operational definitions and feature construction must be finalized and validated against annotated data.

---

## Step 7 — Statistical Analysis

Investigate relationships between:

- ABS
- RS
- engagement
- medium
- topic
- event

Use appropriate statistical methods and report effect sizes, not only p-values.

---

## Step 8 — Fake-News Detection Baseline

Build and evaluate the base fake-news detection model.

---

## Step 9 — Entropy Baseline

Implement an entropy-based test-time sample-selection strategy.

Conceptually:

```text
Input sample
     ↓
Fake-news model
     ↓
Prediction probabilities
     ↓
Entropy
     ↓
Select low/high uncertainty samples according to the defined baseline
     ↓
Test-time adaptation
```

The exact selection rule will be finalized based on the experimental design and literature.

---

## Step 10 — Proposed Reliability-Aware Selection

Compare the entropy baseline with a method that incorporates reliability information.

Conceptually:

```text
Input sample
     ↓
Fake-news model
     ↓
Prediction uncertainty
     +
Reliability information
     ↓
Sample selection
     ↓
Test-time adaptation
     ↓
Evaluation
```

---

## Step 11 — Ablation Studies

Remove individual reliability components and repeat the experiment.

This will help determine which components actually contribute to the final result.

---

## Step 12 — Robustness and Final Evaluation

Use held-out evaluation data and test whether the findings remain stable under alternative settings.

Finally:

```text
Results
  ↓
Analysis
  ↓
Discussion
  ↓
Limitations
  ↓
Conclusion
  ↓
Research Paper
```

---

# 21. Evidence Summary

The strongest evidence completed so far is:

### Evidence 1 — Event dataset

A 10-event `event_list.csv` was created.

### Evidence 2 — GDELT retrieval

The E005 Cebu earthquake query successfully returned **20 articles**.

### Evidence 3 — Article diversity

The 20 articles contained different coverage types and multiple source domains.

### Evidence 4 — Text extraction

Three real news articles were successfully processed with Trafilatura:

```text
6,634 characters
1,670 characters
1,660 characters
```

### Evidence 5 — Rate-limit diagnosis

Repeated HTTP 429 responses were observed during multi-event collection, and different request intervals were tested.

### Evidence 6 — Partial successful multi-event collection

Five events in the latest 10-event run eventually produced successful results, while other requests remained rate-limited or timed out.

---

# 22. Important Boundary: What We Have NOT Claimed

We have **not** yet demonstrated:

- that 50–100 events can be collected reliably
- that the final corpus will contain 3,000–5,000 usable articles
- that ABS is predictive
- that RS is predictive
- that ABS and RS are independent/weakly correlated
- that entropy is insufficient
- that reliability-aware selection improves test-time adaptation
- that the proposed method beats an entropy baseline

Those are **research hypotheses and planned experiments**, not completed findings.

This distinction must be maintained in the final paper.

---

# 23. One-Line Project Status

> **We have completed the initial Phase 1 feasibility work: the 10-event event-based dataset structure is established, GDELT online-news discovery has been validated with real results, article-text extraction using Trafilatura has been successfully tested across multiple outlets, and the main remaining Phase 1 issue is establishing a reliable collection strategy under GDELT's rate limits.**

---

## For New Team Members

Start with these files:

```text
README.md
event_list.csv
collect_gdelt.py
test_extraction.py
inspect_gdelt.py
```

Then read the **Completed Work**, **Evidence Summary**, and **Planned Work** sections above.

Do not start implementing ABS, RS, entropy, or test-time adaptation yet unless the team agrees that the Phase 1 dataset is sufficiently stable.
