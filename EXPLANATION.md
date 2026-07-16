# Growth.ai Codebase Explanation & Developer Walkthrough

This document serves as a complete technical guide to the **Growth.ai** codebase. It covers the system architecture, code modules, the data ingestion pipeline, KPI mathematics, testing strategies, and troubleshooting guides to help you explain the system and debug it in the future.

### Reference Dataset
* **Source Dataset:** [SaaS subscription and churn analytics dataset](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset)

---

## 1. Project Directory Structure

```text
Growth.ai/
├── data/
│   └── growth_ai.db               # SQLite database populated with analytical data
├── docs/                          # Architectural and schema documentation
├── src/
│   └── growth_ai/
│       ├── __init__.py
│       ├── config.py              # Configuration manager using Pydantic Settings
│       ├── domain/
│       │   ├── __init__.py
│       │   └── models.py          # Domain model / dataclass representing KPI results
│       ├── application/
│       │   ├── __init__.py
│       │   ├── cleaning.py        # Pandas cleaning & deduplication logic
│       │   ├── metrics.py         # NumPy / Pandas core KPI calculation algorithms
│       │   ├── ports.py           # Inbound/outbound port interfaces (e.g., AnalyticsBundle)
│       │   └── reporting.py       # Excel & PDF report exporting scripts
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database.py        # SQLAlchemy engine creation & connection check
│       │   └── repositories.py    # SQL repository pattern wrapping Pandas read_sql_table
│       └── presentation/
│           ├── __init__.py
│           └── streamlit_app.py   # Streamlit UI dashboard
├── tests/                         # Pytest unit tests
├── process_kaggle_data.py         # Kaggle SaaS dataset ingestion pipeline
├── seed_db.py                     # Synthetic database seeder (alternative script)
├── pyproject.toml                 # Dependencies, package settings, and ruff lint configuration
└── EXPLANATION.md                 # This file
```

---

## 2. Ingestion Pipeline (`process_kaggle_data.py`)

Since the synthetic Kaggle dataset (`rivalytics/saas-subscription-and-churn-analytics-dataset`) does not match our specific SQL database schema directly, we use `process_kaggle_data.py` to ingest, transform, and map the raw files.

### Mapping Strategy

1. **Users (`users` table)**
   - **Source:** `ravenstack_accounts.csv`
   - **Fields Mapped:**
     - `user_id` $\leftarrow$ `account_id`
     - `signup_date` $\leftarrow$ `signup_date` (normalized to `%Y-%m-%d %H:%M:%S`)
     - `country` $\leftarrow$ `country`
     - `plan` $\leftarrow$ Derived from `is_trial` (`True` $\rightarrow$ `"trial"`, `False` $\rightarrow$ `"paid"`)

2. **Subscriptions (`subscriptions` table)**
   - **Source:** `ravenstack_subscriptions.csv`
   - **Logic:** The `subscriptions` table tracks upgrades to paid tiers. We filter where `is_trial == False` to only load actual paid conversion entries.
   - **Fields Mapped:**
     - `subscription_id` $\leftarrow$ `subscription_id`
     - `user_id` $\leftarrow$ `account_id`
     - `upgrade_date` $\leftarrow$ `start_date`
     - `plan` $\leftarrow$ `"paid"`

3. **Feature Usage (`feature_usage` table)**
   - **Source:** `ravenstack_feature_usage.csv` joined with `ravenstack_subscriptions.csv` to map `subscription_id` back to the account's `user_id` (`account_id`).
   - **Fields Mapped:**
     - `feature_id` $\leftarrow$ `usage_id`
     - `user_id` $\leftarrow$ `account_id`
     - `feature_name` $\leftarrow$ `feature_name`
     - `timestamp` $\leftarrow$ `usage_date`

4. **Sessions (`sessions` table)**
   - **Source:** Not provided in the Kaggle CSVs, but required by our KPI module.
   - **Simulation Logic:**
     - We group all usage events by `(user_id, usage_date)`.
     - For each group, we sum the `usage_duration_secs`. The session duration is calculated by converting the duration to minutes, bounded between 2 and 120 minutes.
     - We select a random hour on that date to represent `login_time`, and set `logout_time = login_time + duration`.
     - For users who registered but never logged any feature usage, we generate a fallback session of 5–20 minutes starting at 10:00 AM on their `signup_date`.

---

## 3. Data Cleaning Module (`src/growth_ai/application/cleaning.py`)

Raw database extraction is cleaned systematically before KPIs are calculated:

* **Column Standardization (`_standardize_columns`):** Converts all DataFrame headers to lowercase and strips whitespaces.
* **Timestamp Parsing (`_parse_timestamp_columns`):** Parses date fields (`signup_date`, `login_time`, etc.) to UTC datetime objects, and converts them to timezone-naive datetimes to avoid timezone mismatch warnings/errors during comparisons.
* **Plan Normalization (`_normalize_plan_values`):** Normalizes the `plan` field to string values, strips and lowercases them. Plan values not in `{"trial", "paid"}` are set to `pd.NA`.
* **Deduplication:**
  - `users`: Deduped by `user_id` keeping the last entry. Null `user_id` entries are removed.
  - `sessions`: Deduped on all columns. Sessions where `logout_time < login_time` (invalid sessions) are discarded.
  - `feature_usage`: Deduped on all columns. Rows with null values in primary keys or feature names are removed.
  - `subscriptions`: Deduped by `subscription_id` keeping the last entry.

---

## 4. Analytics & KPIs Module (`src/growth_ai/application/metrics.py`)

This file contains the core formulas and logical calculations computed using Pandas and NumPy:

1. **Total Users:** Distinct count of users in the users dataframe.
2. **Trial Users:** Distinct count of users where `plan == "trial"`.
3. **Paid Users:** Distinct count of users present in the subscriptions dataframe.
4. **Conversion Rate (%):**
   $$\text{Conversion Rate} = \left(\frac{\text{Paid Users}}{\text{Trial Users}}\right) \times 100$$
5. **Average Session Duration (min):** Mean of the differences `(logout_time - login_time)` converted to seconds, then divided by 60, rounded to 2 decimal places.
6. **DAU / WAU / MAU:**
   - Evaluated relative to the `latest_timestamp` (the most recent date recorded across all tables).
   - Counts unique active users in a window of 1 day (DAU), 7 days (WAU), and 30 days (MAU).
7. **Retention Rate (%):**
   - Finds the cohort of users active in the very first 30 days of the dataset.
   - Measures what percentage of those same users are active in the last 30 days of the dataset.
8. **Feature Adoption & Pre-Upgrade Adoption (%):**
   - **Feature Adoption:** Unique users of a feature divided by total users.
   - **Pre-Upgrade Feature Adoption:** Merges feature usages with subscriptions. Counts unique users of a feature whose usage timestamp is $\le$ their upgrade date, divided by total users.

---

## 5. Repository Layer & Streamlit Dashboard

* **Infrastructure (`src/growth_ai/infrastructure/repositories.py`):**
  Uses SQLAlchemy to execute and load data tables directly into memory as Pandas DataFrames.
* **Presentation (`src/growth_ai/presentation/streamlit_app.py`):**
  Renders the layout, config options in the sidebar, metric grids, summary tables, and feature adoption bar charts. It also features a button to export Excel (xlsx) and PDF summaries of calculated KPIs to the reports directory.

---

## 6. How to Identify and Debug Future Bugs

If a bug arises, follow this triage flow:

### A. Mismatched or Invalid Datetime Parsing
* **Symptom:** DAU/WAU/MAU are all 0, or retention calculations return NaN.
* **Explanation:** In Python, comparing a timezone-aware datetime (e.g. UTC) with a timezone-naive datetime causes a `TypeError`.
* **Fix/Prevention:** Ensure the columns in `TIMESTAMP_COLUMNS` inside `cleaning.py` are processed correctly using:
  ```python
  pd.to_datetime(series, errors="coerce", utc=True).dt.tz_convert(None)
  ```

### B. Missing SQL Tables
* **Symptom:** Streamlit dashboard fails with `Table not found` errors.
* **Fix/Prevention:** Ensure that the database contains the 4 essential tables (`users`, `sessions`, `feature_usage`, `subscriptions`). Check your `.env` database connection path. If using SQLite, run:
  ```bash
  /home/scatterzz/Documents/Growth.ai/.venv/bin/python process_kaggle_data.py
  ```
  to recreate the database and tables.

### C. Low Conversion Rates or NaN Rates
* **Symptom:** Conversion rate displays as `0.0%` or is extremely low.
* **Explanation:** Ensure that the `plan` field in `users` contains lowercased `"trial"` values, and that `subscriptions` contains rows matching the same `user_id`s in `users`. If there's a case discrepancy (e.g. `"Trial"` vs `"trial"`), the query filtering in `metrics.py` will fail to count trial users.

---

## 7. Useful Verification Commands

* **Run Tests:** `python -m pytest`
* **Run Linter:** `ruff check .`
* **Format Code:** `ruff format .`
* **Type Checker:** `mypy src tests`
