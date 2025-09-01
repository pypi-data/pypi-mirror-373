"""
Data fetching module for stock market data.

This module provides functionality to fetch stock market data from multiple sources
with fallback mechanisms and data validation.
"""

import logging
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

from config.config import APIConfig
from src.data.alpha_vantage_fetcher import AlphaVantageFetcher
from src.data.screener_fetcher import ScreenerFetcher
from src.utils.cache import clear_old_cache, load_from_cache, save_to_cache

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches stock market data from multiple sources with fallback mechanisms.

    This class provides methods to fetch historical and real-time stock data
    from multiple sources with data validation and cross-verification.

    Data Sources:
    - Yahoo Finance (Primary)
    - Alpha Vantage (Fallback)
    - Screener.in (Validation)
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the DataFetcher with multiple data sources.

        Args:
            cache_dir: Directory to cache fetched data (optional)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("cache")
        self._setup_cache()

        # Initialize cache utilities
        self._load_from_cache = load_from_cache
        self._save_to_cache = save_to_cache
        self._clear_old_cache = clear_old_cache

        # Initialize data sources
        self.alpha_vantage = None
        self.screener = None

        # Initialize Alpha Vantage if API key is available
        alpha_vantage_key = APIConfig.ALPHA_VANTAGE["api_key"]
        if alpha_vantage_key and alpha_vantage_key != "YOUR_ALPHA_VANTAGE_API_KEY":
            self.alpha_vantage = AlphaVantageFetcher(alpha_vantage_key)

        # Initialize Screener.in fetcher
        self.screener = ScreenerFetcher()

        # Clear any old cache entries on init
        self._clear_old_cache()

    def _setup_cache(self) -> None:
        """Set up the cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _validate_dataframe(self, df: pd.DataFrame, symbol: str) -> bool:
        """Validate that a DataFrame has the required columns and data.

        Args:
            df: DataFrame to validate
            symbol: Stock symbol for logging

        Returns:
            bool: True if the DataFrame is valid, False otherwise
        """
        if not isinstance(df, pd.DataFrame) or df.empty:
            logger.warning(f"Invalid DataFrame for {symbol}")
            return False

        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            logger.warning(f"Missing required columns {missing_columns} for {symbol}")
            return False

        # Check for missing values in required columns
        for col in required_columns:
            if df[col].isnull().all():
                logger.warning(f"All values are null for column {col} in {symbol}")
                return False

        return True

    def _validate_with_screener(
        self, symbol: str, df: pd.DataFrame, tolerance: float = 0.05
    ) -> bool:
        """Validate stock data with Screener.in.

        Args:
            symbol: Stock symbol
            df: DataFrame with price data
            tolerance: Allowed percentage difference (0-1)

        Returns:
            bool: True if data is valid, False otherwise
        """
        if not hasattr(self, "screener") or not self.screener:
            logger.warning("Screener.in fetcher not available for validation")
            return True  # Skip validation if screener is not available

        try:
            # Get the latest price from the DataFrame
            latest_data = df.iloc[-1].to_dict()

            # Validate with Screener.in
            is_valid, details = self.screener.validate_stock_data(
                symbol.split(".")[0],  # Remove exchange suffix
                latest_data,
                tolerance=tolerance,
            )

            if not is_valid:
                logger.warning(f"Data validation failed for {symbol}: {details}")

            return is_valid

        except Exception as e:
            logger.error(f"Error validating data with Screener.in for {symbol}: {e}")
            return True  # Skip validation on error

    def _fetch_from_yfinance(
        self, symbol: str, days: int, interval: str, **kwargs
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance.

        Args:
            symbol: Stock symbol with exchange suffix (e.g., 'RELIANCE.NS')
            days: Number of days of historical data
            interval: Data interval ('1d', '1h', etc.)

        Returns:
            DataFrame with OHLCV data or None if fetch failed
        """
        try:
            logger.debug(
                f"Fetching {days}d of {interval} data for {symbol} from Yahoo Finance"
            )

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(
                days=days * 1.5
            )  # Add buffer for weekends/holidays

            # For NSE symbols, ensure we have the correct suffix
            if not symbol.endswith((".NS", ".BO", ".NSE")) and not symbol.startswith(
                "^"
            ):
                symbol = f"{symbol}.NS"

            # Remove ^ from index symbols as yfinance doesn't need it
            clean_symbol = symbol.replace("^", "")

            # Fetch data
            ticker = yf.Ticker(clean_symbol)

            # Prepare history arguments
            history_args = {
                "start": start_date,
                "end": end_date,
                "interval": interval,
                "auto_adjust": True,
                "prepost": False,
                **kwargs,
            }

            # Remove threads parameter if it exists to avoid errors
            if "threads" in history_args:
                del history_args["threads"]

            df = ticker.history(**history_args)

            if df.empty:
                logger.warning(f"No data returned from Yahoo Finance for {symbol}")
                return None

            # Ensure required columns exist
            column_mapping = {
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume",
                # Handle potential column name variations
                "Adj Close": "Close",
                "Adj. Close": "Close",
                "Adj Close*": "Close",
                "Adj. Close**": "Close",
            }

            # Rename columns to standard format
            df = df.rename(
                columns={
                    c: "Close"
                    for c in column_mapping
                    if c in df.columns and c != "Close"
                }
            )

            # Ensure all required columns exist
            required_columns = ["Open", "High", "Low", "Close", "Volume"]
            for col in required_columns:
                if col not in df.columns:
                    logger.warning(
                        f"Missing required column '{col}' in Yahoo Finance data for {symbol}"
                    )
                    return None

            # Convert data types
            for col in ["Open", "High", "Low", "Close"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df["Volume"] = (
                pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype("int64")
            )

            # Sort by date and remove duplicates
            df = df[~df.index.duplicated(keep="first")]
            df = df.sort_index()

            # Filter to requested date range
            df = df.last(f"{days}d")

            if df.empty:
                logger.warning(f"No data in date range for {symbol}")
                return None

            return df

        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
            return None

    def _fetch_from_alpha_vantage(
        self, symbol: str, days: int, interval: str, **kwargs
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage.

        Args:
            symbol: Stock symbol with exchange suffix (e.g., 'RELIANCE.NS')
            days: Number of days of historical data
            interval: Data interval ('1d', '1h', etc.)

        Returns:
            DataFrame with OHLCV data or None if fetch failed
        """
        if not hasattr(self, "alpha_vantage") or not self.alpha_vantage:
            logger.debug("Alpha Vantage fetcher not available")
            return None

        try:
            # Remove exchange suffix for Alpha Vantage
            base_symbol = symbol.split(".")[0]

            # Map interval to Alpha Vantage format
            interval_map = {
                "1d": "1d",
                "1wk": "1w",
                "1mo": "1m",
                "1h": "60min",
                "5m": "5min",
                "15m": "15min",
                "30m": "30min",
            }

            av_interval = interval_map.get(interval, "1d")

            # Fetch data
            df = self.alpha_vantage.get_stock_data(
                symbol=base_symbol,
                interval=av_interval,
                output_size="full" if days > 100 else "compact",
            )

            if df is None or df.empty:
                logger.warning(f"No data returned from Alpha Vantage for {symbol}")
                return None

            # Ensure we have enough data points
            if len(df) < 5:  # Arbitrary minimum number of data points
                logger.warning(
                    f"Insufficient data points from Alpha Vantage for {symbol}"
                )
                return None

            # Filter to requested date range
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df.index >= cutoff_date]

            if df.empty:
                logger.warning(f"No data in date range for {symbol} from Alpha Vantage")
                return None

            return df

        except Exception as e:
            logger.error(f"Error fetching data from Alpha Vantage for {symbol}: {e}")
            return None

    def fetch_stock_data(
        self,
        symbol: str,
        days: int = 365,
        interval: str = "1d",
        max_retries: int = 3,
        validate: bool = True,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch historical stock data for a given symbol with caching and fallback mechanisms.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE' for NSE, 'RELIANCE.BO' for BSE)
            days: Number of days of historical data to fetch
            interval: Data interval ('1d', '1h', etc.)
            max_retries: Maximum number of retry attempts for failed requests
            validate: Whether to validate data with Screener.in
            **kwargs: Additional arguments to pass to data sources

        Returns:
            DataFrame with historical stock data (Open, High, Low, Close, Volume)
        """
        # Ensure symbol has the correct exchange suffix if not provided
        if "." not in symbol:
            symbol = f"{symbol}.NS"  # Default to NSE

        # Generate a cache key
        cache_key = f"{days}d_{interval}"
        cache_file = self.cache_dir / f"{symbol}_{cache_key}.pkl"

        # Try to load from cache first
        if cache_file.exists():
            try:
                # Load the cached data with timestamp
                with open(cache_file, "rb") as f:
                    cache_data = pickle.load(f)

                # Check if cache has the expected structure
                if (
                    not isinstance(cache_data, dict)
                    or "data" not in cache_data
                    or "timestamp" not in cache_data
                ):
                    logger.warning("Invalid cache format, will fetch fresh data")
                else:
                    cache_age = time.time() - cache_data["timestamp"]
                    max_cache_age = 20 * 60 * 60  # 20 hours in seconds

                    if cache_age < max_cache_age:
                        df = cache_data["data"]
                        # Validate cached data
                        if self._validate_dataframe(df, symbol):
                            logger.info(
                                f"Loaded {len(df)} rows from cache for {symbol} (age: {cache_age/3600:.1f} hours)"
                            )
                            return df
                        else:
                            logger.warning(
                                "Cached data validation failed, will fetch fresh data"
                            )
                    else:
                        logger.debug(
                            f"Cache expired (age: {cache_age/3600:.1f} hours > 20 hours) for {symbol}"
                        )
            except Exception as e:
                logger.warning(f"Error loading cache for {symbol}: {str(e)}")

        # Try multiple data sources in order of preference
        data_sources = [self._fetch_from_yfinance, self._fetch_from_alpha_vantage]

        df = None
        source_used = None

        for source in data_sources:
            try:
                df = source(symbol, days, interval, **kwargs)
                if df is not None and not df.empty:
                    source_used = source.__name__.replace("_fetch_from_", "")
                    logger.info(
                        f"Successfully fetched data for {symbol} from {source_used}"
                    )
                    break
            except Exception as e:
                logger.warning(
                    f"Failed to fetch data from {source.__name__} for {symbol}: {str(e)}"
                )

        if df is None or df.empty:
            logger.error(f"Failed to fetch data for {symbol} from any source")
            return pd.DataFrame()

        # Validate data with Screener.in if requested
        if validate and source_used != "screener":
            is_valid = self._validate_with_screener(symbol, df)
            if not is_valid:
                logger.warning(
                    f"Data validation failed for {symbol}, but using the data anyway"
                )

        # Cache the result with timestamp
        try:
            # Ensure cache directory exists
            cache_file.parent.mkdir(parents=True, exist_ok=True)

            # Save data with timestamp
            with open(cache_file, "wb") as f:
                pickle.dump({"data": df, "timestamp": time.time()}, f)
            logger.debug(f"Cached {len(df)} rows for {symbol} at {cache_file}")
        except Exception as e:
            logger.error(f"Error caching data for {symbol}: {str(e)}", exc_info=True)

        return df

    def fetch_multiple_stocks(
        self, symbols: List[str], days: int = 365, interval: str = "1d", **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stock symbols.

        Args:
            symbols: List of stock symbols
            days: Number of days of historical data to fetch
            interval: Data interval ('1d', '1h', etc.)
            **kwargs: Additional arguments to pass to yfinance

        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        results = {}

        for symbol in symbols:
            data = self.fetch_stock_data(symbol, days, interval, **kwargs)
            if not data.empty:
                results[symbol] = data

        return results

    def get_company_info(self, symbol: str) -> Dict[str, str]:
        """
        Get company information for a given symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company information
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "description": info.get("longBusinessSummary", ""),
                "website": info.get("website", ""),
            }
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return {}

    def get_market_index(
        self, index_symbol: str = "^NSEI", days: int = 365
    ) -> pd.DataFrame:
        """
        Fetch market index data.

        Args:
            index_symbol: Index symbol (e.g., '^NSEI' for NIFTY 50)
            days: Number of days of historical data to fetch

        Returns:
            DataFrame with index data
        """
        return self.fetch_stock_data(index_symbol, days=days)
