"""
Technical analysis module for stock data.
"""

import pandas as pd
from typing import Dict, Any


class TechnicalAnalysis:
    """Class for performing technical analysis on stock data."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the TechnicalAnalysis with stock data.

        Args:
            data: DataFrame containing stock data with columns like 'Open', 'High', 'Low', 'Close', 'Volume'
        """
        self.data = data
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that the input data has the required columns."""
        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        if not required_columns.issubset(self.data.columns):
            missing = required_columns - set(self.data.columns)
            raise ValueError(f"Input data is missing required columns: {missing}")

    def calculate_sma(self, window: int = 20) -> pd.Series:
        """Calculate Simple Moving Average."""
        return self.data["Close"].rolling(window=window).mean()

    def calculate_ema(self, window: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return self.data["Close"].ewm(span=window, adjust=False).mean()

    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = self.data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(
        self, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, pd.Series]:
        """Calculate Moving Average Convergence Divergence."""
        exp1 = self.data["Close"].ewm(span=fast, adjust=False).mean()
        exp2 = self.data["Close"].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()

        return {"macd": macd, "signal": signal_line, "histogram": macd - signal_line}

    def calculate_bollinger_bands(
        self, window: int = 20, num_std: float = 2
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = self.calculate_sma(window)
        rolling_std = self.data["Close"].rolling(window=window).std()

        return {
            "middle": sma,
            "upper": sma + (rolling_std * num_std),
            "lower": sma - (rolling_std * num_std),
        }

    def calculate_all_indicators(self) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        return {
            "sma_20": self.calculate_sma(20).iloc[-1],
            "sma_50": self.calculate_sma(50).iloc[-1],
            "ema_20": self.calculate_ema(20).iloc[-1],
            "ema_50": self.calculate_ema(50).iloc[-1],
            "rsi": self.calculate_rsi().iloc[-1],
            "macd": self.calculate_macd()["macd"].iloc[-1],
            "macd_signal": self.calculate_macd()["signal"].iloc[-1],
            "bollinger": {
                "middle": self.calculate_bollinger_bands()["middle"].iloc[-1],
                "upper": self.calculate_bollinger_bands()["upper"].iloc[-1],
                "lower": self.calculate_bollinger_bands()["lower"].iloc[-1],
            },
            "volume": self.data["Volume"].iloc[-1],
        }
