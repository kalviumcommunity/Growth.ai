# Conversion-IQ

Growth.ai is a Python analytics foundation for studying six months of SaaS trial activity, feature usage, and subscription conversion data. The goal is to turn raw operational data into clean datasets, reliable KPIs, and a dashboard that helps product teams understand what drives upgrades.

## Project Analysis

### Core objective
Connect user behavior with subscription conversion outcomes so product managers can move from intuition to evidence-based decisions.

### Major features
- SQL-based ingestion of user, session, feature usage, and subscription data
- Deterministic data cleaning and normalization with Pandas
- KPI calculation with NumPy and Pandas
- Feature-adoption and pre-upgrade analysis
- CSV, Excel, and PDF report export
- Streamlit dashboard for KPI visualization

### Logical modules
- `domain`: immutable business metrics and report models
- `application`: cleaning, transformation, KPI calculation, and report generation
- `infrastructure`: SQLAlchemy-based database access and repository adapters
- `presentation`: Streamlit dashboard

### Best-fit technology choices
- Python for data processing and orchestration
- Pandas for tabular cleaning and transformation
- NumPy for numerical calculations
- SQLAlchemy for database access abstraction
- Streamlit for the interactive dashboard
- Pydantic Settings for configuration management
- Ruff and Pytest for code quality and verification

### Ambiguities and assumptions
- The source database schema was only partially defined, so the implementation standardizes table names to `users`, `sessions`, `feature_usage`, and `subscriptions`.
- The docs require dashboards but do not specify a UI framework, so Streamlit is used as the simplest production-friendly dashboard layer.
- The docs mention PostgreSQL/MySQL, but the foundation uses SQLAlchemy so any supported database can be configured later through `DATABASE_URL`.
- The reporting scope includes PDF export, but no report template was specified, so the initial PDF is a KPI summary rather than a branded report.

## Architecture

The project follows clean architecture principles:

- `domain` contains the business data model and avoids infrastructure concerns.
- `application` owns the analytics rules and pipeline logic.
- `infrastructure` handles external systems such as the database.
- `presentation` renders the dashboard and user-facing outputs.

This separation keeps the analytics rules testable, makes it easy to swap databases or dashboard layers later, and avoids coupling product logic to Streamlit or SQLAlchemy internals.

## Dependency Rationale

Runtime dependencies:
- `pandas`: data cleaning, transformation, aggregation, and export support
- `numpy`: numerical analytics and ratio calculations
- `SQLAlchemy`: database abstraction and connection management
- `streamlit`: dashboard UI
- `pydantic` and `pydantic-settings`: validated configuration and environment management
- `python-dotenv`: local `.env` loading support
- `openpyxl`: Excel report export
- `reportlab`: PDF report export
- `matplotlib`: optional charting support for future report views

Development dependencies:
- `ruff`: linting and formatting
- `pytest`: automated testing
- `pytest-cov`: coverage reporting
- `mypy`: static type checking

## Folder Structure

```text
Growth.ai/
├── artifacts/
├── data/
├── docs/
├── src/
│   └── growth_ai/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── presentation/
├── tests/
├── .editorconfig
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Environment Setup

1. Create a copy of `.env.example` as `.env`.
2. Set `DATABASE_URL` to your SQL database connection string.
3. Adjust `REPORTS_DIRECTORY` if you want exports stored somewhere else.
4. Install dependencies with `pip` inside the configured virtual environment.

## Installation

```bash
/home/scatterzz/Documents/Growth.ai/.venv/bin/python -m pip install -e .
/home/scatterzz/Documents/Growth.ai/.venv/bin/python -m pip install -e ".[dev]"
```

## Running the Dashboard

```bash
streamlit run src/growth_ai/presentation/streamlit_app.py
```

## Available Scripts and Commands

- `streamlit run src/growth_ai/presentation/streamlit_app.py`: launch the dashboard
- `python -m pytest`: run the test suite
- `ruff check .`: lint the project
- `ruff format .`: format the codebase
- `python -m pip install -e .`: install runtime dependencies
- `python -m pip install -e ".[dev]"`: install runtime plus developer tooling

## Development Workflow

1. Ingest historical data from the configured database.
2. Clean and normalize the raw tables.
3. Compute KPI summaries.
4. Review dashboard output and export reports.
5. Extend the application layer first when adding new metrics.
6. Add or update tests whenever analytics rules change.

## Code Quality Strategy

- Input validation happens through Pydantic settings and explicit DataFrame cleanup.
- Analytics calculations are isolated from the dashboard so they can be tested independently.
- SQL access is abstracted behind a repository adapter.
- Report generation is deterministic and file-based.
- Error handling is explicit in the dashboard layer so configuration problems are visible immediately.

## Contribution Guidelines

- Keep business logic in `application`, not in the dashboard layer.
- Prefer typed, pure functions for analytics rules.
- Add tests for every new KPI or transformation rule.
- Keep dependencies lean and only add packages with a clear product need.
- Preserve the layered architecture when extending the project.

## Validation

The initial foundation includes focused unit tests for cleaning, KPI calculation, and report export. After installing dependencies, run:

```bash
python -m pytest
ruff check .
```

## Next Steps

- Wire the repository adapter to the real production schema.
- Replace the initial KPI summary PDF with a branded report template if needed.
- Add sample data or fixtures for end-to-end dashboard previewing.
