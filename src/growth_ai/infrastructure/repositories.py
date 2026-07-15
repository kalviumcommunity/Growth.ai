from __future__ import annotations

import pandas as pd

from growth_ai.application.ports import AnalyticsBundle
from growth_ai.infrastructure.database import create_engine_from_url


class SqlAnalyticsRepository:
    """Load analytics tables from a relational database."""

    def __init__(self, database_url: str) -> None:
        self._engine = create_engine_from_url(database_url)

    def load_users(self) -> pd.DataFrame:
        return pd.read_sql_table("users", self._engine)

    def load_sessions(self) -> pd.DataFrame:
        return pd.read_sql_table("sessions", self._engine)

    def load_feature_usage(self) -> pd.DataFrame:
        return pd.read_sql_table("feature_usage", self._engine)

    def load_subscriptions(self) -> pd.DataFrame:
        return pd.read_sql_table("subscriptions", self._engine)

    def load_bundle(self) -> AnalyticsBundle:
        return AnalyticsBundle(
            users=self.load_users(),
            sessions=self.load_sessions(),
            feature_usage=self.load_feature_usage(),
            subscriptions=self.load_subscriptions(),
        )
