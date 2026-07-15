from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


@dataclass(slots=True)
class AnalyticsBundle:
    """Raw or cleaned tabular datasets used by the analytics pipeline."""

    users: pd.DataFrame
    sessions: pd.DataFrame
    feature_usage: pd.DataFrame
    subscriptions: pd.DataFrame


class AnalyticsRepository(Protocol):
    def load_users(self) -> pd.DataFrame: ...

    def load_sessions(self) -> pd.DataFrame: ...

    def load_feature_usage(self) -> pd.DataFrame: ...

    def load_subscriptions(self) -> pd.DataFrame: ...

    def load_bundle(self) -> AnalyticsBundle: ...
