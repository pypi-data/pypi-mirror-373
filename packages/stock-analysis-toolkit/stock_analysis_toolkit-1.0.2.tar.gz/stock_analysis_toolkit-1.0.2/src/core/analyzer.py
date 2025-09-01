"""
Core stock analysis functionality.

This module contains the main StockAnalyzer class that orchestrates
the analysis of stocks using technical and fundamental analysis.
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

from src.data.models import AnalysisResult, StockData
from src.core.models import Recommendation
from src.data.fetcher import DataFetcher
from src.analysis.technical import TechnicalAnalysis
from src.analysis.fundamental import calculate_fundamental_metrics

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """
    Main class for performing stock analysis.

    This class coordinates data fetching, technical analysis, and fundamental
    analysis to provide comprehensive stock analysis.
    """

    def __init__(self, symbols: Optional[List[str]] = None, days: int = 365):
        """
        Initialize the StockAnalyzer.

        Args:
            symbols: List of stock symbols to analyze (default: top BSE stocks)
            days: Number of days of historical data to fetch (default: 365)
        """
        from src.config.settings import TOP_BSE_STOCKS  # Avoid circular import
        from src.utils.cache import load_from_cache, save_to_cache

        self.symbols = symbols or TOP_BSE_STOCKS
        self.days = days
        self.data_fetcher = DataFetcher()
        self.analysis_results: Dict[str, AnalysisResult] = {}

        # Setup cache functions
        self._load_from_cache = load_from_cache
        self._save_to_cache = save_to_cache

        # Load any cached results
        self._load_cached_results()

    def _load_cached_results(self) -> None:
        """Load any cached analysis results."""
        for symbol in self.symbols:
            cache_key = f"{symbol}_analysis"
            cached_result = self._load_from_cache(symbol, cache_key)
            if cached_result:
                self.analysis_results[symbol] = cached_result
                logger.debug(f"Loaded cached analysis for {symbol}")

    def fetch_data(self) -> Dict[str, StockData]:
        """
        Fetch data for all symbols.

        Returns:
            Dictionary mapping symbols to StockData objects
        """
        logger.info(f"Fetching data for {len(self.symbols)} stocks...")
        stock_data = {}

        # Process each symbol individually to isolate issues
        for symbol in self.symbols:
            try:
                # Fetch data for this symbol
                logger.debug(f"Fetching data for {symbol}...")
                df = self.data_fetcher.fetch_stock_data(symbol, days=self.days)

                if df is None or df.empty:
                    logger.warning(f"No data returned for {symbol}")
                    continue

                # Debug: Print the raw data structure
                logger.debug("\n" + "=" * 50)
                logger.debug(f"RAW DATA STRUCTURE FOR {symbol}")
                logger.debug("=" * 50)
                logger.debug(f"Type: {type(df)}")
                if hasattr(df, "__dict__"):
                    logger.debug(f"Attributes: {dir(df)}")
                if hasattr(df, "shape"):
                    logger.debug(f"Shape: {df.shape}")
                if hasattr(df, "columns"):
                    logger.debug(f"Columns: {list(df.columns)}")
                    for col in df.columns:
                        logger.debug(f"  - {col} (type: {type(col).__name__})")
                if hasattr(df, "iloc") and len(df) > 0:
                    logger.debug("\nFirst row values:")
                    first_row = df.iloc[0]
                    for col in df.columns:
                        logger.debug(
                            f"  {col}: {first_row[col]} (type: {type(first_row[col]).__name__})"
                        )
                logger.debug("=" * 50 + "\n")

                # Debug: Log the raw data structure in detail
                logger.debug(f"\n{'='*50}")
                logger.debug(f"Processing data for {symbol}")
                logger.debug(f"{'='*50}")

                # Log DataFrame type and basic info
                logger.debug(f"DataFrame type: {type(df)}")
                logger.debug(f"Shape: {df.shape if hasattr(df, 'shape') else 'N/A'}")

                # Log column information
                if hasattr(df, "columns"):
                    columns = df.columns.tolist()
                    logger.debug(f"\nOriginal columns ({len(columns)}): {columns}")
                    logger.debug(f"Column types: {[type(col) for col in df.columns]}")

                    # Log detailed column information
                    logger.debug("\nColumn details:")
                    for i, col in enumerate(df.columns):
                        col_type = type(col)
                        col_str = str(col)
                        logger.debug(
                            f"  {i}. {col} (type: {col_type.__name__}, str: '{col_str}')"
                        )

                # Log first few rows of data if available
                if hasattr(df, "head") and not df.empty:
                    logger.debug("\nFirst 2 rows of data:")
                    for i, (idx, row) in enumerate(df.head(2).iterrows(), 1):
                        logger.debug(f"Row {i} (index: {idx}):")
                        for col in df.columns:
                            val = row[col]
                            logger.debug(f"  {col}: {val} (type: {type(val).__name__})")
                else:
                    logger.debug("\nNo data rows available")

                # Ensure we have a DataFrame
                if not isinstance(df, pd.DataFrame):
                    logger.warning(f"Expected DataFrame for {symbol}, got {type(df)}")
                    continue

                # Ensure we have the required columns (case-insensitive check)
                required_columns = ["Open", "High", "Low", "Close", "Volume"]

                # Convert all column names to strings, handling both string and tuple column names
                column_mapping = {}
                for col in df.columns:
                    if isinstance(col, tuple):
                        # Join tuple elements with underscore and convert to string
                        new_col = "_".join(str(c) for c in col if c)
                        column_mapping[col] = new_col
                    else:
                        # Ensure it's a string
                        new_col = str(col)
                        if new_col != col:  # Only add to mapping if it changed
                            column_mapping[col] = new_col

                # Apply column name conversions if any
                if column_mapping:
                    df = df.rename(columns=column_mapping)

                # Now check for required columns (case-insensitive)
                available_columns = []
                for col in df.columns:
                    col_str = str(col).capitalize()
                    if col_str in required_columns:
                        available_columns.append(col)

                if len(available_columns) < len(required_columns):
                    missing = set(required_columns) - set(
                        str(col).capitalize() for col in available_columns
                    )
                    logger.warning(f"Missing required columns {missing} for {symbol}")
                    logger.debug(f"Available columns: {df.columns.tolist()}")
                    continue

                # Standardize column names (capitalize first letter)
                df = df.rename(
                    columns={col: str(col).capitalize() for col in df.columns}
                )

                # Ensure all required columns are present and numeric
                for col in required_columns:
                    if col not in df.columns:
                        logger.warning(f"Column {col} not found in data for {symbol}")
                        continue

                    try:
                        # Convert to numeric, coercing errors to NaN
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    except Exception as e:
                        logger.warning(
                            f"Failed to convert {col} to numeric for {symbol}: {str(e)}"
                        )
                        df[col] = None

                # Drop rows with any missing values
                df = df.dropna(subset=required_columns)

                if df.empty:
                    logger.warning(
                        f"No valid data remaining after cleaning for {symbol}"
                    )
                    continue

                # Ensure the index is a DatetimeIndex
                if not isinstance(df.index, pd.DatetimeIndex):
                    try:
                        df.index = pd.to_datetime(df.index)
                    except Exception as e:
                        logger.warning(
                            f"Could not convert index to datetime for {symbol}: {str(e)}"
                        )
                        continue

                # Sort by date (ascending)
                df = df.sort_index()

                # Create StockData object
                stock_data[symbol] = StockData(
                    symbol=symbol,
                    data=df[required_columns],
                    metadata={
                        "days": len(df),
                        "first_date": df.index.min().strftime("%Y-%m-%d"),
                        "last_date": df.index.max().strftime("%Y-%m-%d"),
                    },
                )

                logger.info(
                    f"Successfully processed data for {symbol} with {len(df)} rows"
                )

            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}", exc_info=True)
                continue

        return stock_data

    def analyze_stock(self, symbol: str, stock_data: StockData) -> AnalysisResult:
        """
        Analyze a single stock's data with caching.

        Args:
            symbol: Stock symbol
            stock_data: StockData object containing the stock's data

        Returns:
            AnalysisResult containing all analysis data
        """
        cache_key = f"{symbol}_analysis"

        # Try to load from cache first
        cached_result = self._load_from_cache(symbol, cache_key)
        if cached_result:
            logger.info(f"Using cached analysis for {symbol}")
            self.analysis_results[symbol] = cached_result
            return cached_result

        try:
            logger.info(f"Analyzing {symbol} (not in cache or cache expired)...")

            # Perform technical analysis
            ta = TechnicalAnalysis(stock_data.data)
            indicators = ta.calculate_all_indicators()

            # Get fundamental data
            fundamentals = calculate_fundamental_metrics(symbol)

            # Store results
            result = AnalysisResult(
                symbol=symbol,
                technical_indicators=indicators,
                fundamental_metrics=fundamentals,
                metadata={
                    "analysis_date": datetime.utcnow().isoformat(),
                    "data_points": len(stock_data.data),
                },
            )

            # Save to cache
            self._save_to_cache(symbol, cache_key, result)
            self.analysis_results[symbol] = result
            return result

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return AnalysisResult(symbol=symbol)

    def analyze_all(self) -> Dict[str, AnalysisResult]:
        """
        Run analysis for all symbols.

        Returns:
            Dictionary mapping symbols to their AnalysisResults
        """
        stock_data = self.fetch_data()

        for symbol, data in stock_data.items():
            try:
                self.analysis_results[symbol] = self.analyze_stock(symbol, data)
                logger.info(f"Completed analysis for {symbol}")
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                continue

        return self.analysis_results

    def generate_recommendation(self, analysis: AnalysisResult) -> Recommendation:
        """
        Generate a recommendation based on analysis results.

        Args:
            analysis: AnalysisResult to base the recommendation on

        Returns:
            Recommendation object with action and reasoning
        """
        # This is a simplified version - expand with actual recommendation logic
        reasoning = []

        # Example recommendation logic
        rsi = analysis.technical_indicators.get("rsi")
        if rsi is not None:
            if rsi < 30:
                reasoning.append("RSI indicates oversold conditions")
            elif rsi > 70:
                reasoning.append("RSI indicates overbought conditions")

        pe = analysis.fundamental_metrics.get("pe_ratio")
        if pe is not None:
            if pe < 15:
                reasoning.append("Low P/E ratio suggests good value")
            elif pe > 25:
                reasoning.append("High P/E ratio suggests overvaluation")

        # Default to HOLD if no strong signals
        if not reasoning:
            reasoning.append("No strong buy/sell signals detected")
            return Recommendation(
                symbol=analysis.symbol,
                action="HOLD",
                confidence=0.5,
                reasoning=reasoning,
            )

        # Simple decision logic - expand based on your strategy
        if any("oversold" in r.lower() or "low" in r.lower() for r in reasoning):
            action = "BUY"
            confidence = 0.7
        elif any("overbought" in r.lower() or "high" in r.lower() for r in reasoning):
            action = "SELL"
            confidence = 0.6
        else:
            action = "HOLD"
            confidence = 0.5

        return Recommendation(
            symbol=analysis.symbol,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
        )
