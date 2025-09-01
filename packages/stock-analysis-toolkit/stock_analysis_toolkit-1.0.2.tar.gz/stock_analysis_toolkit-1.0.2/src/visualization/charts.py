"""
Chart generation module.

This module provides functions to create various financial charts
using Plotly.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


def create_candlestick_chart(
    data: pd.DataFrame,
    symbol: str,
    title: Optional[str] = None,
    show_volume: bool = True,
    show_sma: bool = True,
    sma_periods: List[int] = [20, 50, 200],
    **layout_kwargs,
) -> go.Figure:
    """
    Create a candlestick chart with optional volume and moving averages.

    Args:
        data: DataFrame with OHLCV data
        symbol: Stock symbol
        title: Chart title (default: f"{symbol} Price")
        show_volume: Whether to show volume subplot
        show_sma: Whether to show simple moving averages
        sma_periods: List of periods for SMAs
        **layout_kwargs: Additional layout parameters

    Returns:
        Plotly Figure object
    """
    title = title or f"{symbol} Price"

    # Create subplots
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1.0]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="OHLC",
            increasing_line_color="#26a69a",  # green
            decreasing_line_color="#ef5350",  # red
        ),
        row=1,
        col=1,
    )

    # Add moving averages
    if show_sma:
        for period in sma_periods:
            if f"SMA_{period}" in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[f"SMA_{period}"],
                        name=f"SMA {period}",
                        line=dict(width=1.5),
                    ),
                    row=1,
                    col=1,
                )

    # Add volume if requested
    if show_volume and "Volume" in data.columns:
        # Calculate color based on price movement
        colors = [
            "#26a69a" if close >= open_ else "#ef5350"
            for close, open_ in zip(data["Close"], data["Open"])
        ]

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Volume"],
                name="Volume",
                marker_color=colors,
                opacity=0.5,
            ),
            row=2,
            col=1,
        )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        showlegend=True,
        template="plotly_dark",
        hovermode="x unified",
        **layout_kwargs,
    )

    if show_volume:
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def create_technical_indicators_chart(
    data: pd.DataFrame, symbol: str, indicators: List[str] = None, **layout_kwargs
) -> go.Figure:
    """
    Create a chart with multiple technical indicators.

    Args:
        data: DataFrame with indicator data
        symbol: Stock symbol
        indicators: List of indicators to include
        **layout_kwargs: Additional layout parameters

    Returns:
        Plotly Figure object
    """
    indicators = indicators or ["RSI", "MACD", "BBANDS"]

    # Create subplots based on number of indicators
    fig = make_subplots(
        rows=len(indicators),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[f"{indicator} - {symbol}" for indicator in indicators],
    )

    for i, indicator in enumerate(indicators, 1):
        if indicator.upper() == "RSI" and "RSI" in data.columns:
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
            col in data.columns for col in ["MACD", "Signal"]
        ):
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
    fig.update_layout(
        height=300 * len(indicators),
        showlegend=True,
        template="plotly_dark",
        hovermode="x unified",
        **layout_kwargs,
    )

    return fig


def create_sector_performance_chart(
    sector_data: Dict[str, float], title: str = "Sector Performance", **layout_kwargs
) -> go.Figure:
    """
    Create a bar chart showing performance by sector.

    Args:
        sector_data: Dictionary mapping sector names to performance values
        title: Chart title
        **layout_kwargs: Additional layout parameters

    Returns:
        Plotly Figure object
    """
    # Sort sectors by performance
    sectors = sorted(sector_data.items(), key=lambda x: x[1])
    sector_names = [s[0] for s in sectors]
    values = [s[1] for s in sectors]

    # Define colors based on performance
    colors = ["#26a69a" if v >= 0 else "#ef5350" for v in values]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=values,
            y=sector_names,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}%" for v in values],
            textposition="auto",
            opacity=0.8,
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Performance (%)",
        yaxis_title="Sector",
        showlegend=False,
        template="plotly_dark",
        **layout_kwargs,
    )

    return fig


def save_chart(
    fig: go.Figure,
    filepath: Union[str, Path],
    width: int = 1200,
    height: int = 800,
    **kwargs,
) -> None:
    """
    Save a Plotly figure to a file.

    Args:
        fig: Plotly Figure to save
        filepath: Path to save the file to
        width: Width in pixels
        height: Height in pixels
        **kwargs: Additional arguments to fig.write_html
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Default HTML saving options
    default_kwargs = {"full_html": False, "include_plotlyjs": "cdn", "auto_open": False}

    # Update with any user-provided kwargs
    default_kwargs.update(kwargs)

    # Set figure size
    fig.update_layout(
        width=width, height=height, margin=dict(l=50, r=50, b=50, t=50, pad=4)
    )

    # Save based on file extension
    ext = filepath.suffix.lower()

    if ext == ".html":
        fig.write_html(filepath, **default_kwargs)
    elif ext == ".png":
        fig.write_image(filepath, engine="kaleido")
    elif ext in [".jpg", ".jpeg", ".webp", "svg", "pdf", "eps"]:
        fig.write_image(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    logger.info(f"Chart saved to {filepath}")
