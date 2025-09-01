"""
Report generation module.

This module provides functionality to generate comprehensive
stock analysis reports in various formats.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from src.config import get_settings, REPORTS_DIR
from src.visualization import (
    create_candlestick_chart,
    create_technical_indicators_chart,
    create_sector_performance_chart,
    save_chart,
)

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates stock analysis reports in various formats.

    This class handles the creation of comprehensive stock analysis
    reports including price charts, technical indicators, and
    fundamental analysis.
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the ReportGenerator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.settings = get_settings()
        self.output_dir = Path(output_dir) if output_dir else REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up template environment
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def _get_template(self, template_name: str):
        """
        Get a template by name.

        Args:
            template_name: Name of the template file

        Returns:
            Jinja2 template object

        Raises:
            FileNotFoundError: If template file is not found
            Exception: For other template loading errors
        """
        try:
            # Try to load from the templates directory first
            return self.env.get_template(template_name)
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            raise

    def _prepare_chart_data(self, data: pd.DataFrame, symbol: str) -> Dict[str, str]:
        """
        Prepare chart data for the report.

        Args:
            data: Stock data with indicators
            symbol: Stock symbol

        Returns:
            Dictionary with chart file paths or base64 data
        """
        try:
            # Create charts directory
            charts_dir = self.output_dir / "charts"
            charts_dir.mkdir(exist_ok=True, parents=True)

            # Generate charts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_paths = {}

            # Price chart
            price_chart_path = charts_dir / f"{symbol}_price_{timestamp}.html"
            try:
                price_fig = create_candlestick_chart(data, symbol)
                save_chart(price_fig, price_chart_path)
                chart_paths["price_chart"] = str(
                    price_chart_path.relative_to(self.output_dir)
                )
                logger.debug(f"Saved price chart to {price_chart_path}")
            except Exception as e:
                logger.error(f"Failed to generate price chart: {e}")
                chart_paths["price_chart"] = None

            # Technical indicators chart
            tech_chart_path = charts_dir / f"{symbol}_indicators_{timestamp}.html"
            try:
                tech_fig = create_technical_indicators_chart(
                    data, symbol, indicators=["RSI", "MACD", "BBANDS"]
                )
                save_chart(tech_fig, tech_chart_path)
                chart_paths["tech_chart"] = str(
                    tech_chart_path.relative_to(self.output_dir)
                )
                logger.debug(f"Saved technical indicators chart to {tech_chart_path}")
            except Exception as e:
                logger.error(f"Failed to generate technical indicators chart: {e}")
                chart_paths["tech_chart"] = None

            return chart_paths

        except Exception as e:
            logger.error(f"Error in _prepare_chart_data: {e}")
            return {"price_chart": None, "tech_chart": None}

    def generate_stock_report(
        self,
        symbol: str,
        data: pd.DataFrame,
        analysis: Dict[str, Any],
        template_name: str = "stock_report.html",
        output_file: Optional[Union[str, Path]] = None,
        include_charts: bool = True,
    ) -> Tuple[str, Path]:
        """
        Generate a stock analysis report using the new template system.

        Args:
            symbol: Stock symbol
            data: Stock data with indicators
            analysis: Analysis results dictionary containing:
                - price: Dict with current price, change, etc.
                - technical: Dict with technical indicators
                - fundamentals: Dict with fundamental analysis
                - recommendation: Dict with buy/sell recommendation
                - news: List of recent news items
                - company_info: Dict with company information
            template_name: Name of the template to use (default: stock_report.html)
            output_file: Path to save the report (default: auto-generated)
            include_charts: Whether to generate and include charts

        Returns:
            Tuple of (HTML content, output file path)
        """
        try:
            # Prepare output file path
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"{symbol}_report_{timestamp}.html"
            else:
                output_file = Path(output_file)

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Generate charts if requested
            chart_paths = {}
            if include_charts and not data.empty:
                chart_paths = self._prepare_chart_data(data, symbol)

            # Prepare context for the template
            context = {
                "symbol": symbol,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "analysis": {
                    "price": analysis.get("price", {}),
                    "technical": analysis.get("technical", {}),
                    "fundamentals": analysis.get("fundamentals", {}),
                    "recommendation": analysis.get("recommendation", {}),
                    "news": analysis.get("news", []),
                    "company_info": analysis.get("company_info", {}),
                },
                "charts": chart_paths,
                "is_index": symbol.startswith("^"),
            }

            # Add some helper functions to the context
            def format_currency(value, symbol="$", places=2):
                try:
                    if value is None:
                        return "N/A"
                    return f"{symbol}{value:,.{places}f}"
                except (ValueError, TypeError):
                    return str(value)

            def format_percent(value, places=2):
                try:
                    if value is None:
                        return "N/A"
                    return f"{value:,.{places}f}%"
                except (ValueError, TypeError):
                    return str(value)

            # Add helpers to context
            context["helpers"] = {
                "format_currency": format_currency,
                "format_percent": format_percent,
            }

            # Render template
            template = self._get_template(template_name)
            html_content = template.render(**context)

            # Save report
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Generated report: {output_file}")
            return html_content, output_file

        except Exception as e:
            logger.error(f"Error generating stock report: {e}", exc_info=True)
            raise

    def generate_sector_report(
        self,
        sector_data: Dict[str, Dict[str, Any]],
        top_stocks: Dict[str, List[Dict[str, Any]]],
        template_name: str = "sector_report.html",
        output_file: Optional[Union[str, Path]] = None,
        include_charts: bool = True,
        **additional_context: Any,
    ) -> Tuple[str, Path]:
        """
        Generate a sector performance report using the new template system.

        Args:
            sector_data: Dictionary mapping sector names to performance data:
                - performance: Dictionary with time period keys
                  ('1D', '1W', '1M', 'YTD', '1Y')
                - change: Overall change percentage
                - trend: Overall trend ('up', 'down', 'neutral')
            top_stocks: Dictionary mapping sector names to lists of top stocks:
                - symbol: Stock symbol
                - company: Company name
                - price: Current price
                - change: Price change percentage
            template_name: Name of the template to use (default: sector_report.html)
            output_file: Path to save the report (default: auto-generated)
            include_charts: Whether to generate and include charts
            **additional_context: Additional context to pass to the template

        Returns:
            Tuple of (HTML content, output file path)
        """
        try:
            # Prepare output file path
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"sector_report_{timestamp}.html"
            else:
                output_file = Path(output_file)

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Generate sector performance chart
            chart_path = None
            if include_charts and sector_data:
                try:
                    charts_dir = self.output_dir / "charts"
                    charts_dir.mkdir(exist_ok=True, parents=True)

                    chart_filename = f"sector_performance_{timestamp}.html"
                    chart_path = charts_dir / chart_filename

                    # Create a simplified version of sector data for the chart
                    chart_data = {
                        sector: data.get("change", 0)
                        for sector, data in sector_data.items()
                    }

                    sector_fig = create_sector_performance_chart(chart_data)
                    save_chart(sector_fig, chart_path)
                    chart_path = str(chart_path.relative_to(self.output_dir))
                    logger.debug(f"Saved sector chart to {chart_path}")
                except Exception as e:
                    logger.error(f"Failed to generate sector chart: {e}")
                    chart_path = None

            # Calculate sector overview
            sector_overview = {
                "trend": "neutral",
                "top_performer": {"name": "N/A", "change": 0},
                "worst_performer": {"name": "N/A", "change": 0},
                "average_change": 0,
            }

            if sector_data:
                changes = [
                    (sector, data.get("change", 0))
                    for sector, data in sector_data.items()
                    if data.get("change") is not None
                ]

                if changes:
                    # Sort by performance
                    sorted_sectors = sorted(changes, key=lambda x: x[1], reverse=True)

                    sector_overview.update(
                        {
                            "top_performer": {
                                "name": sorted_sectors[0][0],
                                "change": sorted_sectors[0][1],
                            },
                            "worst_performer": {
                                "name": sorted_sectors[-1][0],
                                "change": sorted_sectors[-1][1],
                            },
                            "average_change": (
                                sum(c[1] for c in changes) / len(changes)
                                if changes
                                else 0
                            ),
                            "trend": (
                                "up"
                                if sum(1 for c in changes if c[1] > 0)
                                > len(changes) / 2
                                else "down"
                            ),
                        }
                    )

            # Prepare context
            context = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sector_data": sector_data,
                "top_stocks": top_stocks,
                "sector_chart": chart_path,
                "sector_overview": sector_overview,
                "sector_comparison": {
                    sector: {
                        "1D": data.get("1D", 0),
                        "1W": data.get("1W", 0),
                        "1M": data.get("1M", 0),
                        "YTD": data.get("YTD", 0),
                        "1Y": data.get("1Y", 0),
                    }
                    for sector, data in sector_data.items()
                },
                "sector_insights": additional_context.get("insights", []),
            }

            # Add any additional context
            context.update(additional_context)

            # Add helper functions
            def format_percent(value, places=2):
                try:
                    if value is None:
                        return "N/A"
                    prefix = "+" if value > 0 else ""
                    return f"{prefix}{value:,.{places}f}%"
                except (ValueError, TypeError):
                    return str(value)

            context["helpers"] = {"format_percent": format_percent}

            # Render template
            template = self._get_template(template_name)
            html_content = template.render(**context)

            # Save report
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Generated sector report: {output_file}")
            return html_content, output_file

        except Exception as e:
            logger.error(f"Error generating sector report: {e}", exc_info=True)
            raise

    def generate_dashboard(
        self,
        symbol: str,
        data: pd.DataFrame,
        analysis: Dict[str, Any],
        template_name: str = "dashboard.html",
        output_file: Optional[Union[str, Path]] = None,
        include_charts: bool = True,
        **dashboard_options: Any,
    ) -> Tuple[str, Path]:
        """
        Generate an interactive dashboard for stock analysis
        using the new template system.

        Args:
            symbol: Stock symbol
            data: Stock data with indicators
            analysis: Analysis results
            template_name: Name of the template to use (default: dashboard.html)
            output_file: Path to save the dashboard (default: auto-generated)
            include_charts: Whether to generate and include charts
            **dashboard_options: Additional options for the dashboard:
                - indicators: Dict of indicators to include
                - width: Dashboard width in pixels
                - height: Dashboard height in pixels
                - theme: Color theme ('light', 'dark', etc.)
                - show_sidebar: Whether to show the sidebar
                - show_export: Whether to show export options

        Returns:
            Tuple of (HTML content, output file path)
        """
        try:
            # Prepare output file path
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"{symbol}_dashboard_{timestamp}.html"
            else:
                output_file = Path(output_file)

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Default dashboard options
            default_options = {
                "indicators": {
                    "RSI": {"window": 14},
                    "MACD": {"fast": 12, "slow": 26, "signal": 9},
                    "BBANDS": {"window": 20, "num_std": 2},
                },
                "width": 1400,
                "height": 1000,
                "theme": "dark",
                "show_sidebar": True,
                "show_export": True,
            }

            # Merge with provided options
            dashboard_options = {**default_options, **dashboard_options}

            # Generate dashboard
            from ..visualization.dashboard import create_stock_dashboard

            dashboard_fig = create_stock_dashboard(
                data,
                symbol,
                indicators=dashboard_options["indicators"],
                layout={
                    "width": dashboard_options["width"],
                    "height": dashboard_options["height"],
                    "template": (
                        "plotly_dark"
                        if dashboard_options["theme"] == "dark"
                        else "plotly_white"
                    ),
                },
            )

            # Prepare context for the template
            context = {
                "symbol": symbol,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dashboard_options": dashboard_options,
                "analysis": analysis,
                "show_sidebar": dashboard_options["show_sidebar"],
                "show_export": dashboard_options["show_export"],
            }

            # If we have a custom template, use it
            if template_name != "dashboard.html":
                template = self._get_template(template_name)
                html_content = template.render(**context)
            else:
                # Otherwise, just use the Plotly figure
                html_content = dashboard_fig.to_html(
                    full_html=True,
                    include_plotlyjs="cdn",
                    config={
                        "displayModeBar": True,
                        "scrollZoom": True,
                        "responsive": True,
                    },
                )

            # Save dashboard
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Generated dashboard: {output_file}")
            return html_content, output_file

        except Exception as e:
            logger.error(f"Error generating dashboard: {e}", exc_info=True)
            raise
