"""
Fundamental analysis module for stock data.
"""

from typing import Dict, Any
import yfinance as yf


def get_company_info(symbol: str) -> Dict[str, Any]:
    """
    Get fundamental information about a company.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Dictionary containing company information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get(
                "dividendYield"
            ),  # Already in decimal form from yfinance (e.g., 0.02 for 2%)
            "profit_margins": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsQuarterlyGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "return_on_equity": info.get("returnOnEquity"),
            "beta": info.get("beta"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception as e:
        print(f"Error fetching company info for {symbol}: {e}")
        return {}


def calculate_fundamental_metrics(symbol: str) -> Dict[str, Any]:
    """
    Calculate fundamental analysis metrics for a stock.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Dictionary containing fundamental metrics
    """
    try:
        # Get company info
        company_info = get_company_info(symbol)

        if not company_info:
            return {}

        # Calculate additional metrics if needed
        metrics = {
            "valuation": {
                "pe_ratio": company_info.get("pe_ratio"),
                "pb_ratio": company_info.get("pb_ratio"),
                "market_cap": company_info.get("market_cap"),
                "enterprise_value": company_info.get("enterpriseValue"),
            },
            "profitability": {
                "profit_margins": company_info.get("profit_margins"),
                "return_on_equity": company_info.get("return_on_equity"),
                "return_on_assets": company_info.get("returnOnAssets"),
            },
            "growth": {
                "revenue_growth": company_info.get("revenue_growth"),
                "earnings_growth": company_info.get("earnings_growth"),
                "dividend_growth": company_info.get("dividendRate"),
            },
            "financial_health": {
                "debt_to_equity": company_info.get("debt_to_equity"),
                "current_ratio": company_info.get("currentRatio"),
                "quick_ratio": company_info.get("quickRatio"),
            },
            "dividend": {
                "dividend_yield": company_info.get("dividend_yield"),
                "payout_ratio": company_info.get("payoutRatio"),
                "dividend_rate": company_info.get("dividendRate"),
            },
        }

        return metrics

    except Exception as e:
        print(f"Error calculating fundamental metrics for {symbol}: {e}")
        return {}
