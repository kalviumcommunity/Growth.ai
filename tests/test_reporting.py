from __future__ import annotations

from pathlib import Path

from growth_ai.application.reporting import export_kpi_report
from growth_ai.domain.models import KPIResult


def test_export_kpi_report_writes_multiple_formats(tmp_path: Path) -> None:
    report = KPIResult(total_users=10, trial_users=8, paid_users=2, conversion_rate=25.0)

    exported_files = export_kpi_report(report, tmp_path)

    assert {path.suffix for path in exported_files} == {".csv", ".xlsx", ".pdf"}
    for path in exported_files:
        assert path.exists()
        assert path.stat().st_size > 0
