# Growth.ai Instructions

## Project Summary
Growth.ai is a Python analytics project for cleaning SaaS trial and subscription data, calculating KPIs, exporting reports, and viewing the results in a Streamlit dashboard.

## Requirements
- Python `3.14` or newer
- A relational database or SQLite database containing these tables:
  - `users`
  - `sessions`
  - `feature_usage`
  - `subscriptions`
- Windows PowerShell, Command Prompt, or Bash

## Default Configuration
The application reads settings from a `.env` file if present.

Default values from `src/growth_ai/config.py`:
- `app_name`: `Growth.ai`
- `database_url`: `sqlite:///./data/growth_ai.db`
- `log_level`: `INFO`
- `reports_directory`: `artifacts/reports`
- `demo_mode`: `False`

If you need custom settings, create a `.env` file in the project root.

Example `.env`:
```env
DATABASE_URL=sqlite:///./data/growth_ai.db
REPORTS_DIRECTORY=artifacts/reports
LOG_LEVEL=INFO
DEMO_MODE=false
```

## Setup
### Windows PowerShell
```powershell
cd "C:\Users\rava_\OneDrive\Desktop\WI sem 5\Growth.ai"
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Bash
```bash
cd "/c/Users/rava_/OneDrive/Desktop/WI sem 5/Growth.ai"
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run the Project
### Start the Streamlit dashboard
```powershell
streamlit run src/growth_ai/presentation/streamlit_app.py
```

If Streamlit is not on your PATH, run it through the virtual environment Python:
```powershell
.\.venv\Scripts\python.exe -m streamlit run src/growth_ai/presentation/streamlit_app.py
```

## Validation Commands
### Run tests
```powershell
python -m pytest
```

### Run linting
```powershell
ruff check .
```

### Format code
```powershell
ruff format .
```

### Optional type check
```powershell
mypy src tests
```

## Data and Outputs
- Input data is loaded through SQLAlchemy and pandas from the configured `DATABASE_URL`.
- Exported reports are written to `artifacts/reports` by default.
- The app creates the reports directory automatically if it does not exist.

## Troubleshooting
- If the dashboard says it cannot load the dataset, verify that the configured database exists and includes all four required tables.
- If `.env` values are not being picked up, confirm the file is in the project root and named exactly `.env`.
- If you are using SQLite, make sure the database file path in `DATABASE_URL` is correct.
- If `streamlit` is not recognized, activate `.venv` first or use `.\.venv\Scripts\python.exe -m streamlit run ...`.

## Project Structure
- `src/growth_ai/application`: cleaning, KPI calculation, and report generation
- `src/growth_ai/domain`: core data models
- `src/growth_ai/infrastructure`: SQLAlchemy database access and repositories
- `src/growth_ai/presentation`: Streamlit dashboard
- `tests`: unit tests for the analytics pipeline

## Recommended Workflow
1. Set up the virtual environment.
2. Install the package with dev dependencies.
3. Configure `.env` if you need a non-default database or reports path.
4. Run the Streamlit dashboard.
5. Use `pytest` and `ruff check .` before committing changes.
