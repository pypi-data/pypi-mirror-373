"""
Data handling module for stock analysis.

This package provides functionality for fetching and storing stock market data.
"""

from .fetcher import DataFetcher
from .storage import DataStorage

__all__ = ["DataFetcher", "DataStorage"]
