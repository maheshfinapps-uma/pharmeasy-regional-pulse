# PharmaEasy Regional Pulse

## Assessment Submission

This repository contains the PharmaEasy Regional Pulse capstone assessment covering data generation and cleaning, SQL-verified metrics, insight generation and human review, and a Streamlit stakeholder dashboard.

## Cover Note — 4-Artifact Evaluation Package

### Headline Finding

Guntur regional sales increased from ₹62,442.27 in April 2026 to ₹138,738.93 in May 2026, a +122.19% month-over-month swing, before declining to ₹99,745.18 in June 2026.

### 4-Artifact Package

1. **Streamlit dashboard — `app.py`** — live interactive data exploration.
2. **CII narrative — embedded in `app.py`** — explains what the validated data means.
3. **One-page memo — `memo.md`** — provides the recommendation and next check.
4. **Presentation storyline — `presentation_storyline.md`** — explains how the finding is reframed and defended live.

### Reviewer Consumption Order

1. `app.py` — Streamlit dashboard and embedded CII narrative
2. `memo.md` — one-page recommendation
3. `presentation_storyline.md` — presentation narrative and stakeholder pushback Q&A
4. Part 1–3 supporting scripts and evidence

### Single Unverified Assumption

The analysis assumes that the cleaned order-level data accurately represents the April–June 2026 sales activity and that no unrecorded external business event materially explains the Guntur movement.

## Setup

```bash
pip install -r requirements.txt
```

## Rebuild Part 1

```bash
python generate_dataset.py
python clean_data.py
```

## Build and validate Part 2

```bash
python build_db.py
python queries.py
python metrics_engine.py
```

## Run Part 3

```bash
python draft_report.py
python review_gate.py
```

## Run the dashboard

```bash
streamlit run app.py
```

The dashboard uses local files and does not require an API key or network access for its analytical calculations.

## Key Verified Finding

| Month | Guntur Sales |
|---|---:|
| April 2026 | ₹62,442.27 |
| May 2026 | ₹138,738.93 |
| June 2026 | ₹99,745.18 |

- April → May: **+122.19%**
- May → June: **-28.11%**

The 8% threshold is an operational alert rule, not a statistical significance test.

## Repository Contents

- `generate_dataset.py` — deterministic dataset generation
- `clean_data.py` — cleaning and schema validation
- `data_quality_report.md` — Part 1 quality report
- `build_db.py` — SQLite database build
- `queries.py` — SQL validation and metrics
- `metrics_engine.py` — movement flagging and state persistence
- `draft_report.py` — CII draft generation
- `memo.md` — one-page memo
- `review_gate.py` — human review gate and audit harness
- `audit_log.jsonl` — generated review audit
- `reliability_checklist.md` — reliability controls
- `app.py` — Streamlit dashboard
- `presentation_storyline.md` — SCR, OCD and stakeholder Q&A
