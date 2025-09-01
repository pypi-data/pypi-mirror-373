"""
Screener.in data fetcher for stock market data validation.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from ..utils.api_client import create_screener_client

logger = logging.getLogger(__name__)


class ScreenerFetcher:
    """Fetches and validates stock market data from Screener.in."""

    def __init__(self):
        """Initialize the Screener.in fetcher."""
        self.client = create_screener_client()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )

    def _get_csrf_token(self) -> Optional[str]:
        """Get CSRF token required for Screener.in requests.

        Returns:
            CSRF token or None if the request failed
        """
        try:
            response = self.session.get("https://www.screener.in/", timeout=10)
            response.raise_for_status()

            # Extract CSRF token from HTML
            soup = BeautifulSoup(response.text, "html.parser")
            meta_tag = soup.find("meta", {"name": "csrf-token"})

            if meta_tag and "content" in meta_tag.attrs:
                return meta_tag["content"]

        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")

        return None

    def search_company(self, query: str) -> List[Dict]:
        """Search for companies on Screener.in.

        Args:
            query: Search query (company name or symbol)

        Returns:
            List of matching companies with details
        """
        try:
            csrf_token = self._get_csrf_token()
            if not csrf_token:
                logger.error("Failed to get CSRF token for search")
                return []

            headers = {
                "X-CSRFToken": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.screener.in/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            }

            data = {
                "q": query,
                "filters": "company",
                "limit": "10",
                "csrfmiddlewaretoken": csrf_token,
            }

            response = self.session.post(
                "https://www.screener.in/api/company/search/",
                headers=headers,
                data=data,
                timeout=15,
            )
            response.raise_for_status()

            results = response.json()
            return results if isinstance(results, list) else []

        except Exception as e:
            logger.error(f"Error searching for company '{query}': {e}")
            return []

    def get_company_details(self, company_url: str) -> Optional[Dict]:
        """Get detailed company information from Screener.in.

        Args:
            company_url: Company URL or URL path (e.g., '/company/RELIANCE/')

        Returns:
            Dictionary with company details or None if the request failed
        """
        try:
            # Ensure we have a full URL
            if not company_url.startswith("http"):
                company_url = f"https://www.screener.in{company_url}"

            response = self.session.get(company_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract key metrics
            metrics = {}
            for row in soup.select("#peers + .company-ratios li"):
                try:
                    name = row.find("span", class_="name").text.strip()
                    value = row.find("span", class_="number").text.strip()
                    metrics[name] = value
                except (AttributeError, ValueError) as e:
                    logging.debug(f"Error extracting metrics: {e}")
                    continue

            # Extract current price
            price_elem = soup.select_one(
                "#main-content .company-info .company-price-small"
            )
            current_price = None
            if price_elem:
                price_text = price_elem.text.strip()
                match = re.search(r"[\d,]+\.\d+", price_text)
                if match:
                    current_price = float(match.group().replace(",", ""))

            # Extract 52-week high/low
            week_high_low = {}
            for item in soup.select("#price-info li"):
                text = item.get_text().strip()
                if "52w H" in text:
                    try:
                        week_high_low["52w_high"] = float(
                            text.split(" ")[0].replace(",", "")
                        )
                    except (ValueError, IndexError):
                        pass
                elif "52w L" in text:
                    try:
                        week_high_low["52w_low"] = float(
                            text.split(" ")[0].replace(",", "")
                        )
                    except (ValueError, IndexError):
                        pass

            # Extract company name and ticker
            header = soup.select_one("#main-content h1")
            company_name = ticker = None
            if header:
                header_text = header.get_text().strip()
                parts = [p.strip() for p in header_text.split("\n") if p.strip()]
                if len(parts) >= 2:
                    company_name = parts[0]
                    ticker_match = re.search(r"\((\w+)\)", parts[1])
                    if ticker_match:
                        ticker = ticker_match.group(1)

            # Extract sector and industry
            sector = industry = None
            for li in soup.select("#peers li"):
                text = li.get_text().strip()
                if text.startswith("Sector:"):
                    sector = text.replace("Sector:", "").strip()
                elif text.startswith("Industry:"):
                    industry = text.replace("Industry:", "").strip()

            # Extract financial ratios
            ratios = {}
            for row in soup.select(
                "#ratios .responsive-holder table.data-table tbody tr"
            ):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    ratios[key] = value

            # Extract quarterly results
            quarterly_results = []
            table = soup.select_one("#quarters table.data-table")
            if table:
                headers = [th.get_text().strip() for th in table.select("thead th")]
                for row in table.select("tbody tr"):
                    cells = row.find_all("td")
                    if len(cells) == len(headers):
                        result = {}
                        for i, header in enumerate(headers):
                            result[header] = cells[i].get_text().strip()
                        quarterly_results.append(result)

            return {
                "company_name": company_name,
                "ticker": ticker,
                "sector": sector,
                "industry": industry,
                "current_price": current_price,
                "metrics": metrics,
                "ratios": ratios,
                "quarterly_results": quarterly_results,
                "52w_high": week_high_low.get("52w_high"),
                "52w_low": week_high_low.get("52w_low"),
                "url": company_url,
            }

        except Exception as e:
            logger.error(f"Error fetching company details from {company_url}: {e}")
            return None

    def validate_stock_data(
        self, symbol: str, price_data: Dict[str, float], tolerance: float = 0.05
    ) -> Tuple[bool, Dict]:
        """Validate stock price data against Screener.in.

        Args:
            symbol: Stock symbol
            price_data: Dictionary with price data (Open, High, Low, Close, Volume)
            tolerance: Allowed percentage difference (0-1)

        Returns:
            Tuple of (is_valid, validation_details)
        """
        try:
            # Search for the company
            results = self.search_company(symbol)
            if not results:
                logger.warning(f"No results found for {symbol} on Screener.in")
                return False, {"error": "Company not found on Screener.in"}

            # Get company details
            company = self.get_company_details(results[0].get("url", ""))
            if not company:
                return False, {"error": "Failed to fetch company details"}

            # Get current price from Screener
            screener_price = company.get("current_price")
            if not screener_price:
                return False, {"error": "Current price not available on Screener.in"}

            # Get latest price from input data
            latest_close = price_data.get("Close")
            if not latest_close:
                return False, {"error": "No close price in input data"}

            # Calculate price difference
            price_diff = abs(screener_price - latest_close)
            price_diff_pct = price_diff / screener_price

            is_valid = price_diff_pct <= tolerance

            validation_details = {
                "screener_price": screener_price,
                "input_price": latest_close,
                "price_difference": price_diff,
                "price_difference_pct": price_diff_pct,
                "within_tolerance": is_valid,
                "tolerance": tolerance,
                "company_name": company.get("company_name"),
                "ticker": company.get("ticker"),
                "sector": company.get("sector"),
                "industry": company.get("industry"),
                "52w_high": company.get("52w_high"),
                "52w_low": company.get("52w_low"),
                "metrics": company.get("metrics", {}),
                "ratios": company.get("ratios", {}),
            }

            return is_valid, validation_details

        except Exception as e:
            logger.error(f"Error validating stock data for {symbol}: {e}")
            return False, {"error": str(e)}
