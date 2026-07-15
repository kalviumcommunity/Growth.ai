from __future__ import annotations

import pandas as pd

from growth_ai.application.cleaning import clean_analytics_bundle
from growth_ai.application.ports import AnalyticsBundle


def test_clean_analytics_bundle_standardizes_and_deduplicates() -> None:
    bundle = AnalyticsBundle(
        users=pd.DataFrame(
            {
                "user_id": ["u1", "u1", "u2"],
                "signup_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
                "country": ["US", "US", "DE"],
                "plan": ["Trial", "Paid", "trial"],
            }
        ),
        sessions=pd.DataFrame(
            {
                "session_id": ["s1", "s1"],
                "user_id": ["u1", "u1"],
                "login_time": ["2026-01-05 10:00:00", "2026-01-05 10:00:00"],
                "logout_time": ["2026-01-05 10:25:00", "2026-01-05 10:25:00"],
            }
        ),
        feature_usage=pd.DataFrame(
            {
                "feature_id": ["f1"],
                "user_id": ["u1"],
                "feature_name": ["Reports"],
                "timestamp": ["2026-01-05 11:00:00"],
            }
        ),
        subscriptions=pd.DataFrame(
            {
                "subscription_id": ["sub1"],
                "user_id": ["u1"],
                "upgrade_date": ["2026-01-10"],
                "plan": ["Paid"],
            }
        ),
    )

    cleaned = clean_analytics_bundle(bundle)

    assert len(cleaned.users) == 2
    assert cleaned.users.loc[0, "plan"] == "paid"
    assert pd.api.types.is_datetime64_any_dtype(cleaned.sessions["login_time"])
    assert len(cleaned.sessions) == 1
