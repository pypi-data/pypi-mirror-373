"""
Application constants.

This module contains constants used throughout the application.
"""

from pathlib import Path
from typing import Dict

# Top BSE stocks by market capitalization (example symbols)
TOP_BSE_STOCKS = [
    "RELIANCE.NS",  # Reliance Industries
    "TCS.NS",  # Tata Consultancy Services
    "HDFCBANK.NS",  # HDFC Bank
    "ICICIBANK.NS",  # ICICI Bank
    "HINDUNILVR.NS",  # Hindustan Unilever
    "INFY.NS",  # Infosys
    "ITC.NS",  # ITC Limited
    "BHARTIARTL.NS",  # Bharti Airtel
    "KOTAKBANK.NS",  # Kotak Mahindra Bank
    "LT.NS",  # Larsen & Toubro
]

# Default technical indicators to calculate
DEFAULT_INDICATORS = {
    "sma_20": {"window": 20},
    "sma_50": {"window": 50},
    "sma_200": {"window": 200},
    "rsi": {"window": 14},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "bollinger_bands": {"window": 20, "num_std": 2},
    "atr": {"window": 14},
    "obv": {},
    "adx": {"window": 14},
}


# Email configuration
def get_email_config() -> Dict:
    """Get email configuration with environment variables."""
    from .settings import get_settings
    import os

    settings = get_settings()

    return {
        "enabled": settings.EMAIL_ENABLED,
        "server": settings.SMTP_SERVER,
        "port": settings.SMTP_PORT,
        "use_tls": settings.USE_TLS,
        "username": settings.SENDER_EMAIL or os.getenv("STOCK_ANALYSIS_SENDER_EMAIL"),
        "password": settings.SENDER_PASSWORD
        or os.getenv("STOCK_ANALYSIS_SENDER_PASSWORD"),
        "from_addr": settings.EMAIL_FROM or settings.SENDER_EMAIL,
        "to_addrs": settings.EMAIL_TO or [],
    }


EMAIL_CONFIG = get_email_config()

# Report configuration
REPORTS_DIR = Path("reports")
REPORT_TEMPLATES_DIR = Path(__file__).parent / "templates"

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "filename": "logs/app.log",
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
}

# API endpoints (if any)
API_ENDPOINTS = {
    "nse": "https://www.nseindia.com/api",
    "bse": "https://api.bseindia.com/BseIndiaAPI/api",
    "yfinance": "https://query1.finance.yahoo.com/v8/finance/chart",
}

# Time intervals in seconds
TIME_INTERVALS = {
    "1m": 60,  # 1 minute
    "5m": 300,  # 5 minutes
    "15m": 900,  # 15 minutes
    "30m": 1800,  # 30 minutes
    "1h": 3600,  # 1 hour
    "1d": 86400,  # 1 day
    "1wk": 604800,  # 1 week
    "1mo": 2629746,  # 1 month (average)
}

# Market hours (in local time)
MARKET_HOURS = {
    "pre_market_open": "09:00",
    "market_open": "09:15",
    "market_close": "15:30",
    "post_market_close": "16:00",
}

# Risk levels for portfolio allocation
RISK_LEVELS = {
    "conservative": {"equity": 0.3, "debt": 0.6, "gold": 0.1},
    "moderate": {"equity": 0.6, "debt": 0.3, "gold": 0.1},
    "aggressive": {"equity": 0.8, "debt": 0.1, "gold": 0.1},
}
