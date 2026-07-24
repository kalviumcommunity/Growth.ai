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


@dataclass(slots=True, frozen=True)
class ExperimentItem:
    """Active optimization experiment model."""

    name: str
    category: str
    status: str
    confidence: float | str
    lift: float
    trend: str


@dataclass(slots=True, frozen=True)
class SchemaColumnResult:
    """Schema validation column audit result."""

    column_name: str
    inferred_type: str
    detected_nulls_pct: float
    unique_count: int
    status: str
    trend: str


@dataclass(slots=True, frozen=True)
class IngestionLogItem:
    """Pipeline ingestion history record."""

    filename: str
    size: str
    time_ago: str
    status: str


@dataclass(slots=True, frozen=True)
class UserRiskProfile:
    """Predictive analytics user risk profile."""

    user_id: str
    email: str
    initials: str
    score: int
    risk_level: str
    top_feature: str
    last_active: str
