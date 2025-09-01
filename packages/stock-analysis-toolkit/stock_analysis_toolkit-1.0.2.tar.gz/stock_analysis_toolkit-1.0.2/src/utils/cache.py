"""
Cache module for storing and retrieving API responses and reports.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import pandas as pd

# Cache directory (will be created in the project root)
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# Cache expiration time in hours
CACHE_EXPIRY_HOURS = 20


def get_cache_key(symbol: str, data_type: str) -> str:
    """Generate a cache key based on symbol and data type."""
    return f"{symbol.lower().replace('.', '_')}_{data_type}"


def get_cache_path(symbol: str, data_type: str) -> Path:
    """Get the full path to a cache file."""
    return CACHE_DIR / f"{get_cache_key(symbol, data_type)}.json"


def is_cache_valid(cache_path: Path) -> bool:
    """Check if a cache file exists and is still valid."""
    if not cache_path.exists():
        return False

    # Get file modification time
    mod_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    cache_age = datetime.now() - mod_time

    # Check if cache is older than expiry time
    return cache_age < timedelta(hours=CACHE_EXPIRY_HOURS)


def save_to_cache(symbol: str, data_type: str, data: Any) -> None:
    """
    Save data to cache with proper handling for pandas DataFrames.

    Args:
        symbol: Stock symbol
        data_type: Type of data being cached
        data: Data to cache (can be DataFrame, Series, or other JSON-serializable data)
    """
    cache_path = get_cache_path(symbol, data_type)

    # Create cache directory if it doesn't exist
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    cache_data = {"timestamp": time.time(), "data": None, "dtype": None}

    # Handle pandas DataFrames
    if isinstance(data, pd.DataFrame):
        # Ensure we have the required columns
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(
                f"DataFrame is missing required columns: {required_columns}"
            )

        # Prepare data for serialization
        cache_data.update(
            {
                "data": {
                    "index": data.index.astype(str).tolist(),
                    "values": data[required_columns].to_dict(orient="list"),
                    "dtypes": {col: str(data[col].dtype) for col in required_columns},
                },
                "dtype": "dataframe",
            }
        )
    # Handle pandas Series
    elif isinstance(data, pd.Series):
        cache_data.update(
            {
                "data": {
                    "index": data.index.astype(str).tolist(),
                    "values": data.tolist(),
                    "name": data.name,
                    "dtype": str(data.dtype),
                },
                "dtype": "series",
            }
        )
    # Handle other JSON-serializable data
    else:
        cache_data["data"] = data

    # Save to file
    try:
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2, default=str)
    except Exception as e:
        import logging

        logging.error(f"Error saving cache for {symbol}/{data_type}: {str(e)}")
        raise


def load_from_cache(symbol: str, data_type: str) -> Optional[Any]:
    """
    Load data from cache if it exists and is valid.

    Args:
        symbol: Stock symbol
        data_type: Type of data to load

    Returns:
        The cached data (DataFrame, Series, or other) if found and valid, else None
    """
    cache_path = get_cache_path(symbol, data_type)

    if not is_cache_valid(cache_path):
        return None

    try:
        with open(cache_path, "r") as f:
            cached = json.load(f)

        if not isinstance(cached, dict) or "data" not in cached:
            return None

        data = cached["data"]

        # Reconstruct DataFrame if that's what we have
        if cached.get("dtype") == "dataframe" and isinstance(data, dict):
            try:
                df = pd.DataFrame(
                    data=data["values"],
                    index=pd.DatetimeIndex(pd.to_datetime(data["index"])),
                )
                # Convert dtypes if available
                if "dtypes" in data:
                    for col, dtype_str in data["dtypes"].items():
                        if col in df.columns:
                            try:
                                df[col] = df[col].astype(dtype_str)
                            except (ValueError, TypeError) as e:
                                logging.warning(
                                    f"Could not convert column {col} to {dtype_str}: {e}"
                                )
                return df
            except Exception as e:
                logging.error(f"Error reconstructing DataFrame from cache: {e}")
                return None

        # Reconstruct Series if that's what we have
        elif cached.get("dtype") == "series" and isinstance(data, dict):
            try:
                series = pd.Series(
                    data=data["values"],
                    index=pd.DatetimeIndex(pd.to_datetime(data["index"])),
                    name=data.get("name"),
                )
                if "dtype" in data:
                    try:
                        series = series.astype(data["dtype"])
                    except (ValueError, TypeError) as e:
                        logging.warning(
                            f"Could not convert series to {data['dtype']}: {e}"
                        )
                return series
            except Exception as e:
                logging.error(f"Error reconstructing Series from cache: {e}")
                return None

        # Return as-is for other data types
        return data

    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        logging.error(f"Error loading cache for {symbol}/{data_type}: {e}")
        return None


def clear_old_cache() -> None:
    """Clear cache files older than the expiration time."""
    now = datetime.now()
    for cache_file in CACHE_DIR.glob("*.json"):
        mod_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if now - mod_time > timedelta(hours=CACHE_EXPIRY_HOURS):
            cache_file.unlink()


def clear_cache() -> None:
    """Clear all cache files."""
    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()
