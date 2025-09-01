"""
Application settings and configuration.

This module handles loading and validating application settings
from environment variables and configuration files.
"""

from pathlib import Path
from typing import Any, List, Optional, Union
from pydantic import field_validator, EmailStr, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Top BSE (Bombay Stock Exchange) stocks by market capitalization
TOP_BSE_STOCKS = [
    "RELIANCE.BO",  # Reliance Industries
    "TCS.BO",  # Tata Consultancy Services
    "HDFCBANK.BO",  # HDFC Bank
    "ICICIBANK.BO",  # ICICI Bank
    "HINDUNILVR.BO",  # Hindustan Unilever
    "INFY.BO",  # Infosys
    "ITC.BO",  # ITC Limited
    "KOTAKBANK.BO",  # Kotak Mahindra Bank
    "HDFC.BO",  # HDFC Limited
    "BHARTIARTL.BO",  # Bharti Airtel
]


class Settings(BaseSettings):
    """Application settings."""

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="STOCK_ANALYSIS_",
        extra="ignore",  # Ignore extra fields in .env file
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "Stock Analysis Tool"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Data
    CACHE_DIR: Path = Path(".cache")
    DATA_DIR: Path = Path("data")
    REPORTS_DIR: Path = Path("reports")
    MAX_WORKERS: int = 4

    # Yahoo Finance
    YFINANCE_TIMEOUT: int = 10
    YFINANCE_RETRIES: int = 3

    # Alpha Vantage API
    ALPHA_VANTAGE_API_KEY: Optional[str] = None

    # Email
    EMAIL_ENABLED: bool = False
    SENDER_EMAIL: Optional[EmailStr] = None
    SENDER_PASSWORD: Optional[str] = None
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    USE_TLS: bool = True
    EMAIL_FROM: Optional[str] = None
    EMAIL_TO: List[str] = []

    # Timezone
    TIMEZONE: str = "Asia/Kolkata"

    # Cache Settings
    CACHE_EXPIRY_DAYS: int = 1

    # Report Settings
    REPORT_DIR: str = "reports"
    CHART_DIR: str = "reports/charts"

    # Default Analysis Parameters
    DEFAULT_DAYS: int = 365
    DEFAULT_TOP_STOCKS: int = 10

    # Market Hours
    MARKET_OPEN: str = "09:15"
    MARKET_CLOSE: str = "15:30"

    # Data Sources
    DATA_SOURCES: str = "googlefinance,yfinance,alpha_vantage"

    # Scheduler
    SCHEDULER_ENABLED: bool = False
    SCHEDULE_TIME: str = "09:00"  # Default to 9 AM

    # Debug Mode
    DEBUG_MODE: bool = False

    # Technical Analysis
    DEFAULT_INDICATORS: List[str] = [
        "sma_20",
        "sma_50",
        "sma_200",
        "rsi",
        "macd",
        "bollinger_bands",
        "atr",
        "obv",
        "adx",
    ]

    @field_validator("CACHE_DIR", "DATA_DIR", "REPORTS_DIR", mode="before")
    @classmethod
    def ensure_paths_exist(cls, v: Any, info: ValidationInfo) -> Path:
        """Ensure directories exist and return Path objects."""
        if v is None:
            field_name = info.field_name
            raise ValueError(f"{field_name} cannot be None")
        path = Path(v) if isinstance(v, str) else v
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator("EMAIL_TO", mode="before")
    @classmethod
    def parse_email_list(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated email list."""
        if not v:
            return []
        if isinstance(v, str):
            return [email.strip() for email in v.split(",") if email.strip()]
        return v


# Create a singleton instance
_settings = None


def get_settings() -> Settings:
    """Get the application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
