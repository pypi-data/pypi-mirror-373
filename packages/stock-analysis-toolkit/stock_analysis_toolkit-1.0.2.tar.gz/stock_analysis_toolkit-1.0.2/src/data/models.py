"""
Data models for the stock analysis application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class StockData:
    """Container for stock price data and metadata."""

    symbol: str
    data: Any  # DataFrame containing the stock data
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Container for stock analysis results."""

    symbol: str
    technical_indicators: Dict[str, Any] = field(default_factory=dict)
    fundamental_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert the analysis result to a dictionary."""
        return {
            "symbol": self.symbol,
            "technical_indicators": self.technical_indicators,
            "fundamental_metrics": self.fundamental_metrics,
            "metadata": self.metadata,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create an AnalysisResult from a dictionary."""
        return cls(
            symbol=data["symbol"],
            technical_indicators=data.get("technical_indicators", {}),
            fundamental_metrics=data.get("fundamental_metrics", {}),
            metadata=data.get("metadata", {}),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
        )
