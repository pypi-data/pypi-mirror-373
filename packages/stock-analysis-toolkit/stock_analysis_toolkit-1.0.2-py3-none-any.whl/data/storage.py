"""
Data storage and caching module.

This module provides functionality for caching stock data to reduce API calls
and improve performance.
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Generic

import pandas as pd

T = TypeVar("T")


class DataStorage(Generic[T]):
    """
    Generic data storage with caching capabilities.

    This class provides methods to store and retrieve data with optional
    expiration times.
    """

    def __init__(self, cache_dir: str, ttl: Optional[timedelta] = None):
        """
        Initialize the DataStorage.

        Args:
            cache_dir: Directory to store cached data
            ttl: Time-to-live for cached items (None for no expiration)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl or timedelta(days=1)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get the filesystem path for a cache key."""
        return self.cache_dir / f"{key}.pkl"

    def _get_metadata_path(self, key: str) -> Path:
        """Get the filesystem path for metadata."""
        return self.cache_dir / f"{key}.meta.json"

    def _is_expired(self, metadata: Dict[str, Any]) -> bool:
        """Check if cached data is expired."""
        if self.ttl is None:
            return False

        cached_time = datetime.fromisoformat(metadata["timestamp"])
        return datetime.utcnow() > cached_time + self.ttl

    def get(self, key: str, default: Any = None) -> Optional[T]:
        """
        Retrieve an item from the cache.

        Args:
            key: Cache key
            default: Default value to return if key not found or expired

        Returns:
            The cached item or default if not found/expired
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        if not (cache_path.exists() and meta_path.exists()):
            return default

        try:
            # Load metadata
            with open(meta_path, "r") as f:
                metadata = json.load(f)

            # Check if expired
            if self._is_expired(metadata):
                return default

            # Load the actual data
            with open(cache_path, "rb") as f:
                return pickle.load(f)

        except (IOError, json.JSONDecodeError, pickle.PickleError):
            return default

    def set(self, key: str, value: T, **metadata) -> None:
        """
        Store an item in the cache.

        Args:
            key: Cache key
            value: Value to cache (must be picklable)
            **metadata: Additional metadata to store
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        # Prepare metadata
        metadata.update({"timestamp": datetime.utcnow().isoformat(), "key": key})

        try:
            # Save the data
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)

            # Save metadata
            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=2)

        except (IOError, TypeError):
            # Clean up potentially corrupted files
            for path in [cache_path, meta_path]:
                if path.exists():
                    try:
                        path.unlink()
                    except OSError:
                        pass

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cached items.

        Args:
            key: Specific key to clear (None to clear all)
        """
        if key is not None:
            # Remove specific key
            for path in [self._get_cache_path(key), self._get_metadata_path(key)]:
                if path.exists():
                    path.unlink()
        else:
            # Clear all cached files
            for path in self.cache_dir.glob("*"):
                if path.is_file():
                    path.unlink()


class StockDataStorage(DataStorage[pd.DataFrame]):
    """Specialized storage for stock market data."""

    def __init__(self, cache_dir: str = ".cache/stock_data"):
        """
        Initialize the StockDataStorage.

        Args:
            cache_dir: Directory to store cached stock data
        """
        super().__init__(cache_dir, ttl=timedelta(hours=1))  # 1 hour TTL for stock data

    def get_stock_data(self, symbol: str, days: int = 365) -> Optional[pd.DataFrame]:
        """
        Get cached stock data.

        Args:
            symbol: Stock symbol
            days: Number of days of data

        Returns:
            DataFrame with stock data or None if not in cache/expired
        """
        return self.get(f"{symbol}_{days}")

    def set_stock_data(self, symbol: str, data: pd.DataFrame, days: int = 365) -> None:
        """
        Cache stock data.

        Args:
            symbol: Stock symbol
            data: Stock data to cache
            days: Number of days of data
        """
        self.set(
            f"{symbol}_{days}", data, symbol=symbol, days=days, data_points=len(data)
        )
