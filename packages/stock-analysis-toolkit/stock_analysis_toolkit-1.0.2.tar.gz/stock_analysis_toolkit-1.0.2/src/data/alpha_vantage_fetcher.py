"""
Alpha Vantage data fetcher for stock market data.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
from ..utils.api_client import create_alpha_vantage_client

logger = logging.getLogger(__name__)


class AlphaVantageFetcher:
    """Fetches stock market data from Alpha Vantage API."""

    def __init__(self, api_key: str):
        """Initialize the Alpha Vantage fetcher.

        Args:
            api_key: Alpha Vantage API key
        """
        self.client = create_alpha_vantage_client(api_key)

    def get_stock_data(
        self, symbol: str, interval: str = "1d", output_size: str = "compact"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical stock data for a symbol.

        Args:
            symbol: Stock symbol (with or without exchange suffix)
            interval: Data interval ('1d', '1w', '1m')
            output_size: 'compact' (last 100 data points) or 'full' (full-length time series)

        Returns:
            DataFrame with OHLCV data or None if the request failed
        """
        # Clean and prepare the symbol
        symbol = symbol.upper()

        # Handle NSE symbols (remove .NS or add .BSE for Alpha Vantage)
        if symbol.endswith(".NS"):
            symbol = symbol.replace(".NS", ".BSE")
        elif symbol.endswith(".BO"):
            symbol = symbol.replace(".BO", ".BSE")
        elif not any(ext in symbol for ext in [".BSE", ".NSE", ".BO", ".NS"]):
            symbol = f"{symbol}.BSE"  # Default to BSE for Indian stocks

        # Map interval to Alpha Vantage format
        interval_map = {
            "1d": "TIME_SERIES_DAILY",
            "1w": "TIME_SERIES_WEEKLY",
            "1m": "TIME_SERIES_MONTHLY",
            "1h": "TIME_SERIES_INTRADAY",
            "5m": "TIME_SERIES_INTRADAY",
            "15m": "TIME_SERIES_INTRADAY",
            "30m": "TIME_SERIES_INTRADAY",
            "60m": "TIME_SERIES_INTRADAY",
        }

        function = interval_map.get(interval, "TIME_SERIES_DAILY")

        params = {
            "function": function,
            "symbol": symbol,
            "outputsize": "full" if output_size == "full" else "compact",
            "datatype": "json",
        }

        # Add interval parameter for intraday data
        if function == "TIME_SERIES_INTRADAY":
            interval_param = {
                "1h": "60min",
                "5m": "5min",
                "15m": "15min",
                "30m": "30min",
            }.get(interval, "60min")
            params["interval"] = interval_param

        logger.debug(f"Fetching {interval} data for {symbol} from Alpha Vantage")
        data = self.client.request("GET", "", params=params)

        if not data:
            logger.error(f"Failed to fetch data for {symbol} from Alpha Vantage")
            return None

        # Extract the time series data
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break

        if not time_series_key:
            logger.error(
                f"No time series data found in Alpha Vantage response for {symbol}"
            )
            return None

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(data[time_series_key], orient="index")

        # Convert index to datetime
        df.index = pd.to_datetime(df.index)

        # Rename columns to standard format
        column_mapping = {
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume",
        }

        df = df.rename(columns=column_mapping)

        # Convert data types
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").astype("int64")

        # Sort by date
        df = df.sort_index()

        return df

    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """Get company overview and key metrics.

        Args:
            symbol: Stock symbol (without exchange suffix)

        Returns:
            Dictionary with company overview data or None if the request failed
        """
        params = {
            "function": "OVERVIEW",
            "symbol": f"{symbol}.BSE",  # Use BSE for Indian stocks
        }

        logger.debug(f"Fetching company overview for {symbol} from Alpha Vantage")
        return self.client.request("GET", "", params=params)

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get the latest price and volume information.

        Args:
            symbol: Stock symbol (without exchange suffix)

        Returns:
            Dictionary with quote data or None if the request failed
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": f"{symbol}.BSE",  # Use BSE for Indian stocks
        }

        logger.debug(f"Fetching quote for {symbol} from Alpha Vantage")
        data = self.client.request("GET", "", params=params)

        if not data or "Global Quote" not in data:
            return None

        return data["Global Quote"]

    def search_symbols(self, keywords: str) -> List[Dict]:
        """Search for symbols matching the given keywords.

        Args:
            keywords: Search keywords

        Returns:
            List of matching symbols with details
        """
        params = {"function": "SYMBOL_SEARCH", "keywords": keywords, "datatype": "json"}

        logger.debug(f"Searching Alpha Vantage for symbols matching: {keywords}")
        data = self.client.request("GET", "", params=params)

        if not data or "bestMatches" not in data:
            return []

        return data["bestMatches"]
