"""Enumerations for shared project configuration."""

from __future__ import annotations

from enum import Enum


class RebalanceFrequency(str, Enum):
    """Frequency for portfolio rebalancing."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ScoreStyle(str, Enum):
    """Style used for scoring stocks in the screener."""

    VALUE = "value"
    QUALITY = "quality"
    GROWTH = "growth"
    COMPOSITE = "composite"


class ValuationMethod(str, Enum):
    """Supported valuation methods."""

    PE = "pe"
    PFCF = "pfcf"
    DCF = "dcf"


class ReturnFrequency(str, Enum):
    """Frequency for return calculations."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
