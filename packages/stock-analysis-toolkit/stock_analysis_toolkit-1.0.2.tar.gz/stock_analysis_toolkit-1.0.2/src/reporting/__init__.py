"""
Reporting module for stock analysis.

This package provides functionality for generating reports and sending notifications.
"""

from .reporter import ReportGenerator
from .email_sender import EmailSender
from .templates import get_template, render_template, save_report

__all__ = [
    "ReportGenerator",
    "EmailSender",
    "get_template",
    "render_template",
    "save_report",
]
