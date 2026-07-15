from __future__ import annotations

import pandas as pd

from growth_ai.application.metrics import calculate_kpis
from growth_ai.application.ports import AnalyticsBundle


def test_calculate_kpis_produces_expected_summary() -> None:
    bundle = AnalyticsBundle(
        users=pd.DataFrame(
            {
                "user_id": ["u1", "u2"],
                "signup_date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "country": ["US", "DE"],
                "plan": ["trial", "trial"],
            }
        ),
        sessions=pd.DataFrame(
            {
                "session_id": ["s1", "s2"],
                "user_id": ["u1", "u2"],
                "login_time": pd.to_datetime(["2026-01-10 10:00:00", "2026-01-12 10:00:00"]),
                "logout_time": pd.to_datetime(["2026-01-10 10:30:00", "2026-01-12 10:45:00"]),
            }
        ),
        feature_usage=pd.DataFrame(
            {
                "feature_id": ["f1", "f2"],
                "user_id": ["u1", "u2"],
                "feature_name": ["Reports", "Insights"],
                "timestamp": pd.to_datetime(["2026-01-10 11:00:00", "2026-01-12 11:00:00"]),
            }
        ),
        subscriptions=pd.DataFrame(
            {
                "subscription_id": ["sub1"],
                "user_id": ["u1"],
                "upgrade_date": pd.to_datetime(["2026-01-15"]),
                "plan": ["paid"],
            }
        ),
    )

    report = calculate_kpis(bundle)

    assert report.total_users == 2
    assert report.trial_users == 2
    assert report.paid_users == 1
    assert report.conversion_rate == 50.0
    assert report.average_session_duration_minutes == 37.5
    assert report.daily_active_users == 0
    assert "Reports" in report.feature_adoption
