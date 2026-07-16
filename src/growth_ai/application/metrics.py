from __future__ import annotations

from datetime import timedelta

import pandas as pd

from growth_ai.application.ports import AnalyticsBundle
from growth_ai.domain.models import KPIResult

WINDOW_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


def _empty_result() -> KPIResult:
    return KPIResult()


def _average_session_duration_minutes(sessions: pd.DataFrame) -> float:
    if sessions.empty or not {"login_time", "logout_time"}.issubset(sessions.columns):
        return 0.0

    duration = sessions["logout_time"] - sessions["login_time"]
    duration = duration.dropna()
    if duration.empty:
        return 0.0
    return round(duration.dt.total_seconds().mean() / 60.0, 2)


def _latest_timestamp(bundle: AnalyticsBundle) -> pd.Timestamp | None:
    timestamps: list[pd.Timestamp] = []
    for frame, column in (
        (bundle.sessions, "login_time"),
        (bundle.feature_usage, "timestamp"),
        (bundle.subscriptions, "upgrade_date"),
        (bundle.users, "signup_date"),
    ):
        if column in frame.columns and not frame.empty:
            series = pd.to_datetime(frame[column], errors="coerce").dropna()
            if not series.empty:
                timestamps.append(series.max())
    return max(timestamps) if timestamps else None


def _distinct_users_in_window(
    frame: pd.DataFrame, column: str, window_end: pd.Timestamp, days: int
) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    window_start = window_end - timedelta(days=days)
    active = frame[(frame[column] >= window_start) & (frame[column] <= window_end)]
    return int(active["user_id"].nunique())


def _retention_rate(sessions: pd.DataFrame, latest_timestamp: pd.Timestamp | None) -> float:
    if sessions.empty or latest_timestamp is None or "login_time" not in sessions.columns:
        return 0.0

    first_window_start = sessions["login_time"].min()
    if pd.isna(first_window_start):
        return 0.0

    first_window_end = first_window_start + timedelta(days=30)
    last_window_start = latest_timestamp - timedelta(days=30)

    first_users = set(
        sessions[
            (sessions["login_time"] >= first_window_start)
            & (sessions["login_time"] <= first_window_end)
        ]["user_id"]
        .dropna()
        .astype(str)
    )
    last_users = set(
        sessions[
            (sessions["login_time"] >= last_window_start)
            & (sessions["login_time"] <= latest_timestamp)
        ]["user_id"]
        .dropna()
        .astype(str)
    )
    if not first_users:
        return 0.0
    return round((len(first_users & last_users) / len(first_users)) * 100.0, 2)


def _feature_adoption(feature_usage: pd.DataFrame, total_users: int) -> dict[str, float]:
    if feature_usage.empty or total_users == 0 or "feature_name" not in feature_usage.columns:
        return {}
    adoption = (
        feature_usage.groupby("feature_name")["user_id"].nunique().sort_values(ascending=False)
        / total_users
    )
    return {feature: round(rate * 100.0, 2) for feature, rate in adoption.items()}


def _pre_upgrade_feature_adoption(bundle: AnalyticsBundle, total_users: int) -> dict[str, float]:
    if bundle.feature_usage.empty or bundle.subscriptions.empty or total_users == 0:
        return {}
    if not {"user_id", "feature_name", "timestamp"}.issubset(bundle.feature_usage.columns):
        return {}
    if not {"user_id", "upgrade_date"}.issubset(bundle.subscriptions.columns):
        return {}

    merged = bundle.feature_usage.merge(
        bundle.subscriptions[["user_id", "upgrade_date"]],
        on="user_id",
        how="inner",
    )
    pre_upgrade = merged[merged["timestamp"] <= merged["upgrade_date"]]
    if pre_upgrade.empty:
        return {}

    adoption = (
        pre_upgrade.groupby("feature_name")["user_id"].nunique().sort_values(ascending=False)
        / total_users
    )
    return {feature: round(rate * 100.0, 2) for feature, rate in adoption.items()}


def calculate_kpis(bundle: AnalyticsBundle) -> KPIResult:
    if bundle.users.empty:
        return _empty_result()

    users = bundle.users.copy()
    sessions = bundle.sessions.copy()
    feature_usage = bundle.feature_usage.copy()
    subscriptions = bundle.subscriptions.copy()

    total_users = int(users["user_id"].nunique()) if "user_id" in users.columns else 0
    trial_users = (
        int(users.loc[users["plan"] == "trial", "user_id"].nunique())
        if "plan" in users.columns
        else 0
    )
    paid_users = (
        int(subscriptions["user_id"].nunique()) if "user_id" in subscriptions.columns else 0
    )

    conversion_rate = round((paid_users / trial_users) * 100.0, 2) if trial_users else 0.0
    average_session_duration_minutes = _average_session_duration_minutes(sessions)

    latest_timestamp = _latest_timestamp(bundle)
    if latest_timestamp is None:
        latest_timestamp = pd.Timestamp.utcnow().tz_localize(None)

    daily_active_users = _distinct_users_in_window(
        sessions, "login_time", latest_timestamp, WINDOW_DAYS["daily"]
    )
    weekly_active_users = _distinct_users_in_window(
        sessions, "login_time", latest_timestamp, WINDOW_DAYS["weekly"]
    )
    monthly_active_users = _distinct_users_in_window(
        sessions, "login_time", latest_timestamp, WINDOW_DAYS["monthly"]
    )

    retention_rate = _retention_rate(sessions, latest_timestamp)
    feature_adoption = _feature_adoption(feature_usage, total_users)
    pre_upgrade_feature_adoption = _pre_upgrade_feature_adoption(bundle, total_users)

    return KPIResult(
        total_users=total_users,
        trial_users=trial_users,
        paid_users=paid_users,
        conversion_rate=conversion_rate,
        retention_rate=retention_rate,
        average_session_duration_minutes=average_session_duration_minutes,
        daily_active_users=daily_active_users,
        weekly_active_users=weekly_active_users,
        monthly_active_users=monthly_active_users,
        feature_adoption=feature_adoption,
        pre_upgrade_feature_adoption=pre_upgrade_feature_adoption,
    )
