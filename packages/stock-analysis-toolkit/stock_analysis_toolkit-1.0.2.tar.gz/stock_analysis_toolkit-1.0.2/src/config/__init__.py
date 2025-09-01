"""
Configuration module for the stock analysis application.

This package provides configuration management for the application,
including settings, constants, and environment variables.
"""

from .settings import Settings, get_settings
from .constants import TOP_BSE_STOCKS, DEFAULT_INDICATORS, EMAIL_CONFIG, REPORTS_DIR

__all__ = [
    "Settings",
    "get_settings",
    "TOP_BSE_STOCKS",
    "DEFAULT_INDICATORS",
    "EMAIL_CONFIG",
    "REPORTS_DIR",
]
