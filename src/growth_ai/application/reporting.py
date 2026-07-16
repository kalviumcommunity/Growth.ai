from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from growth_ai.domain.models import KPIResult


def build_kpi_summary_frame(report: KPIResult) -> pd.DataFrame:
    summary_rows = [
        ("total_users", report.total_users),
        ("trial_users", report.trial_users),
        ("paid_users", report.paid_users),
        ("conversion_rate_pct", report.conversion_rate),
        ("retention_rate_pct", report.retention_rate),
        ("average_session_duration_minutes", report.average_session_duration_minutes),
        ("daily_active_users", report.daily_active_users),
        ("weekly_active_users", report.weekly_active_users),
        ("monthly_active_users", report.monthly_active_users),
    ]
    return pd.DataFrame(summary_rows, columns=["metric", "value"])


def _write_pdf(report: KPIResult, output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("Growth.ai KPI Summary", styles["Title"]), Spacer(1, 12)]

    table_data = [["Metric", "Value"]]
    for metric, value in build_kpi_summary_frame(report).itertuples(index=False):
        table_data.append([metric, str(value)])

    table = Table(table_data, colWidths=[220, 220])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.whitesmoke, colors.HexColor("#f3f4f6")],
                ),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    doc.build(story)


def export_kpi_report(
    report: KPIResult,
    output_directory: Path,
    formats: tuple[str, ...] = ("csv", "xlsx", "pdf"),
) -> list[Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    exported_files: list[Path] = []
    summary_frame = build_kpi_summary_frame(report)

    for file_format in formats:
        file_path = output_directory / f"kpi_summary.{file_format}"
        if file_format == "csv":
            summary_frame.to_csv(file_path, index=False)
        elif file_format == "xlsx":
            summary_frame.to_excel(file_path, index=False)
        elif file_format == "pdf":
            _write_pdf(report, file_path)
        else:
            raise ValueError(f"Unsupported export format: {file_format}")
        exported_files.append(file_path)

    return exported_files
