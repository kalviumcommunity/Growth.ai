from __future__ import annotations

import pandas as pd
import streamlit as st

from growth_ai.application.cleaning import clean_analytics_bundle
from growth_ai.application.metrics import calculate_kpis
from growth_ai.application.reporting import build_kpi_summary_frame, export_kpi_report
from growth_ai.config import get_settings
from growth_ai.infrastructure.repositories import SqlAnalyticsRepository

APP_STYLE = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
</style>
"""


def _render_kpi_grid(report) -> None:
    metric_columns = st.columns(4)
    metrics = [
        ("Total Users", report.total_users),
        ("Trial Users", report.trial_users),
        ("Paid Users", report.paid_users),
        ("Conversion Rate", f"{report.conversion_rate:.2f}%"),
        ("Retention Rate", f"{report.retention_rate:.2f}%"),
        ("Avg. Session Duration", f"{report.average_session_duration_minutes:.2f} min"),
        ("DAU", report.daily_active_users),
        ("WAU", report.weekly_active_users),
    ]
    for index, (label, value) in enumerate(metrics):
        metric_columns[index % len(metric_columns)].metric(label, value)


def _render_feature_chart(feature_adoption: dict[str, float]) -> None:
    if not feature_adoption:
        st.info("No feature-usage data is available yet.")
        return

    frame = pd.DataFrame(
        feature_adoption.items(), columns=["feature", "adoption_rate_pct"]
    ).sort_values("adoption_rate_pct", ascending=False)
    st.bar_chart(frame.set_index("feature"))


def _render_summary_table(report) -> None:
    st.dataframe(build_kpi_summary_frame(report), use_container_width=True, hide_index=True)


def main() -> None:
    settings = get_settings()
    st.set_page_config(page_title=settings.app_name, layout="wide")
    st.markdown(APP_STYLE, unsafe_allow_html=True)
    st.title(settings.app_name)
    st.caption("User behavior analytics and subscription conversion dashboard.")

    st.sidebar.header("Configuration")
    st.sidebar.write(f"Database URL: {settings.database_url}")
    st.sidebar.write(f"Reports directory: {settings.reports_directory}")
    st.sidebar.write(f"Demo mode: {settings.demo_mode}")

    try:
        repository = SqlAnalyticsRepository(settings.database_url)
        raw_bundle = repository.load_bundle()
    except Exception as exc:  # pragma: no cover - streamlit rendering path
        st.error("Unable to load the analytics dataset from the configured database.")
        st.exception(exc)
        st.stop()

    cleaned_bundle = clean_analytics_bundle(raw_bundle)
    report = calculate_kpis(cleaned_bundle)

    if st.button("Export KPI Report"):
        exported = export_kpi_report(report, settings.reports_directory)
        st.success(f"Exported {len(exported)} report files to {settings.reports_directory}")

    _render_kpi_grid(report)
    st.subheader("Summary")
    _render_summary_table(report)

    left, right = st.columns(2)
    with left:
        st.subheader("Feature Adoption")
        _render_feature_chart(report.feature_adoption)
    with right:
        st.subheader("Pre-upgrade Feature Adoption")
        _render_feature_chart(report.pre_upgrade_feature_adoption)


if __name__ == "__main__":
    main()
