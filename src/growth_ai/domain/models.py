from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class KPIResult:
    """Structured dashboard metrics produced by the analytics pipeline."""

    total_users: int = 0
    trial_users: int = 0
    paid_users: int = 0
    conversion_rate: float = 0.0
    retention_rate: float = 0.0
    average_session_duration_minutes: float = 0.0
    daily_active_users: int = 0
    weekly_active_users: int = 0
    monthly_active_users: int = 0
    feature_adoption: Mapping[str, float] = field(default_factory=dict)
    pre_upgrade_feature_adoption: Mapping[str, float] = field(default_factory=dict)
