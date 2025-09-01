"""
Dashboard generation module.

This module provides functions to create comprehensive dashboards
combining multiple charts and visualizations.
"""

import logging
from typing import Dict, Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .charts import create_candlestick_chart

logger = logging.getLogger(__name__)


def create_stock_dashboard(
    data: pd.DataFrame,
    symbol: str,
    indicators: Optional[Dict[str, dict]] = None,
    layout: Optional[Dict] = None,
    **kwargs,
) -> go.Figure:
    """
    Create a comprehensive stock dashboard with price and indicators.

    Args:
        data: DataFrame with OHLCV and indicator data
        symbol: Stock symbol
        indicators: Dictionary of indicators to include with their parameters
        layout: Custom layout settings
        **kwargs: Additional arguments to pass to subplots

    Returns:
        Plotly Figure object with the dashboard
    """
    # Default indicators if none provided
    if indicators is None:
        indicators = {
            "RSI": {"window": 14},
            "MACD": {"fast": 12, "slow": 26, "signal": 9},
            "BBANDS": {"window": 20, "num_std": 2},
        }

    # Default layout
    default_layout = {
        "title": f"{symbol} - Stock Analysis Dashboard",
        "height": 1200,
        "showlegend": True,
        "template": "plotly_dark",
        "hovermode": "x unified",
    }

    # Create subplots: 1 row for each indicator + 1 for price
    num_indicators = len(indicators)
    fig = make_subplots(
        rows=num_indicators + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5] + [0.5 / num_indicators] * num_indicators,
        **kwargs,
    )

    # Add price chart (candlesticks)
    price_fig = create_candlestick_chart(data, symbol, show_volume=True)

    for trace in price_fig.data:
        fig.add_trace(trace, row=1, col=1)

    # Add indicators
    for i, (indicator, params) in enumerate(indicators.items(), 2):
        if indicator.upper() == "RSI" and "RSI" in data.columns:
            # RSI
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["RSI"],
                    name="RSI",
                    line=dict(color="#2196F3", width=2),
                ),
                row=i,
                col=1,
            )

            # Add RSI levels
            fig.add_hline(
                y=70, line_dash="dash", line_color="red", opacity=0.5, row=i, col=1
            )
            fig.add_hline(
                y=30, line_dash="dash", line_color="green", opacity=0.5, row=i, col=1
            )

        elif indicator.upper() == "MACD" and all(
            col in data.columns for col in ["MACD", "Signal", "MACD_Hist"]
        ):
            # MACD
            # MACD line
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MACD"],
                    name="MACD",
                    line=dict(color="#2196F3", width=2),
                ),
                row=i,
                col=1,
            )

            # Signal line
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Signal"],
                    name="Signal",
                    line=dict(color="#FF5722", width=1.5),
                ),
                row=i,
                col=1,
            )

            # MACD Histogram
            colors = ["#26a69a" if val >= 0 else "#ef5350" for val in data["MACD_Hist"]]

            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data["MACD_Hist"],
                    name="Histogram",
                    marker_color=colors,
                    opacity=0.6,
                ),
                row=i,
                col=1,
            )

        elif indicator.upper() == "BBANDS" and all(
            col in data.columns for col in ["BB_upper", "BB_middle", "BB_lower"]
        ):
            # Bollinger Bands
            # Upper band
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_upper"],
                    name="Upper Band",
                    line=dict(color="#888", width=1),
                ),
                row=i,
                col=1,
            )

            # Middle band
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_middle"],
                    name="Middle Band",
                    line=dict(color="#888", width=1, dash="dash"),
                ),
                row=i,
                col=1,
            )

            # Lower band
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_lower"],
                    name="Lower Band",
                    line=dict(color="#888", width=1),
                ),
                row=i,
                col=1,
            )

            # Fill between bands
            fig.add_trace(
                go.Scatter(
                    x=data.index.tolist() + data.index[::-1].tolist(),
                    y=data["BB_upper"].tolist() + data["BB_lower"][::-1].tolist(),
                    fill="toself",
                    fillcolor="rgba(33, 150, 243, 0.1)",
                    line=dict(width=0),
                    showlegend=False,
                ),
                row=i,
                col=1,
            )

    # Update layout
    fig.update_layout(**{**default_layout, **(layout or {})})

    # Update y-axis titles
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    # Update x-axis ranges
    fig.update_xaxes(rangeslider_visible=False)

    return fig


def create_sector_dashboard(
    sector_data: Dict[str, float],
    top_stocks: Dict[str, Dict[str, float]],
    layout: Optional[Dict] = None,
    **kwargs,
) -> go.Figure:
    """
    Create a dashboard showing sector performance and top stocks.

    Args:
        sector_data: Dictionary mapping sector names to performance values
        top_stocks: Dictionary mapping sector names to top stocks data
        layout: Custom layout settings
        **kwargs: Additional arguments to pass to subplots

    Returns:
        Plotly Figure object with the dashboard
    """
    from .charts import create_sector_performance_chart

    # Create subplots: 1 for sector performance, 1 for each sector's top stocks
    num_sectors = len(sector_data)
    fig = make_subplots(
        rows=num_sectors + 1,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.1,
        row_heights=[0.3] + [0.7 / num_sectors] * num_sectors,
        subplot_titles=["Sector Performance"] + list(sector_data.keys()),
        **kwargs,
    )

    # Add sector performance chart
    sector_fig = create_sector_performance_chart(sector_data)
    for trace in sector_fig.data:
        fig.add_trace(trace, row=1, col=1)

    # Add top stocks for each sector
    for i, (sector, stocks) in enumerate(top_stocks.items(), 2):
        if not stocks:
            continue

        # Sort stocks by performance
        sorted_stocks = sorted(stocks.items(), key=lambda x: x[1], reverse=True)
        stock_names = [s[0] for s in sorted_stocks]
        stock_perf = [s[1] for s in sorted_stocks]

        # Define colors based on performance
        colors = ["#26a69a" if p >= 0 else "#ef5350" for p in stock_perf]

        # Add bar chart for top stocks
        fig.add_trace(
            go.Bar(
                x=stock_names,
                y=stock_perf,
                name=sector,
                marker_color=colors,
                text=[f"{p:.2f}%" for p in stock_perf],
                textposition="auto",
            ),
            row=i,
            col=1,
        )

    # Update layout
    default_layout = {
        "title": "Sector Performance Dashboard",
        "height": 1000,
        "showlegend": False,
        "template": "plotly_dark",
    }

    fig.update_layout(**{**default_layout, **(layout or {})})

    return fig
