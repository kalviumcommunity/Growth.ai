from __future__ import annotations

import pandas as pd

from growth_ai.application.ports import AnalyticsBundle

EXPECTED_PLAN_VALUES = {"trial", "paid"}
TIMESTAMP_COLUMNS = ("signup_date", "login_time", "logout_time", "timestamp", "upgrade_date")


def _standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    standardized = frame.copy()
    standardized.columns = [str(column).strip().lower() for column in standardized.columns]
    return standardized


def _parse_timestamp_columns(frame: pd.DataFrame) -> pd.DataFrame:
    parsed = frame.copy()
    for column in TIMESTAMP_COLUMNS:
        if column in parsed.columns:
            parsed[column] = pd.to_datetime(parsed[column], errors="coerce", utc=True).dt.tz_convert(None)
    return parsed


def _normalize_plan_values(frame: pd.DataFrame) -> pd.DataFrame:
    if "plan" not in frame.columns:
        return frame

    normalized = frame.copy()
    normalized["plan"] = normalized["plan"].astype("string").str.strip().str.lower()
    normalized.loc[~normalized["plan"].isin(EXPECTED_PLAN_VALUES), "plan"] = pd.NA
    return normalized


def clean_users(users: pd.DataFrame) -> pd.DataFrame:
    cleaned = _normalize_plan_values(_parse_timestamp_columns(_standardize_columns(users)))
    if "user_id" in cleaned.columns:
        cleaned = cleaned.drop_duplicates(subset=["user_id"], keep="last")
    return cleaned.dropna(subset=["user_id"]).reset_index(drop=True)


def clean_sessions(sessions: pd.DataFrame) -> pd.DataFrame:
    cleaned = _parse_timestamp_columns(_standardize_columns(sessions))
    cleaned = cleaned.drop_duplicates()
    if {"login_time", "logout_time"}.issubset(cleaned.columns):
        cleaned = cleaned[cleaned["logout_time"].isna() | (cleaned["logout_time"] >= cleaned["login_time"])]
    return cleaned.dropna(subset=["user_id", "session_id"]).reset_index(drop=True)


def clean_feature_usage(feature_usage: pd.DataFrame) -> pd.DataFrame:
    cleaned = _parse_timestamp_columns(_standardize_columns(feature_usage)).drop_duplicates()
    return cleaned.dropna(subset=["user_id", "feature_name", "timestamp"]).reset_index(drop=True)


def clean_subscriptions(subscriptions: pd.DataFrame) -> pd.DataFrame:
    cleaned = _normalize_plan_values(_parse_timestamp_columns(_standardize_columns(subscriptions)))
    cleaned = cleaned.drop_duplicates(subset=["subscription_id"], keep="last") if "subscription_id" in cleaned.columns else cleaned.drop_duplicates()
    return cleaned.dropna(subset=["user_id", "upgrade_date"]).reset_index(drop=True)


def clean_analytics_bundle(bundle: AnalyticsBundle) -> AnalyticsBundle:
    return AnalyticsBundle(
        users=clean_users(bundle.users),
        sessions=clean_sessions(bundle.sessions),
        feature_usage=clean_feature_usage(bundle.feature_usage),
        subscriptions=clean_subscriptions(bundle.subscriptions),
    )
