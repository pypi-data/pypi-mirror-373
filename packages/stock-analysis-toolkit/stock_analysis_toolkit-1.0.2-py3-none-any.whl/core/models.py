"""
Data models for stock analysis.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import pandas as pd


@dataclass
class StockData:
    """Container for stock market data and metadata."""

    symbol: str
    data: pd.DataFrame
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Container for analysis results of a single stock."""

    symbol: str
    technical_indicators: Dict[str, Union[float, pd.Series]]
    fundamental_metrics: Dict[str, Optional[float]]
    visualization_paths: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def all_metrics(self) -> Dict[str, Union[float, str, None]]:
        """Combine technical and fundamental metrics into a single dictionary."""
        return {**self.technical_indicators, **self.fundamental_metrics}


@dataclass
class Recommendation:
    """Stock recommendation with reasoning."""

    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD', etc.
    confidence: float  # 0.0 to 1.0
    reasoning: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReportData:
    """Container for report generation data."""

    analysis_results: List[AnalysisResult]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
