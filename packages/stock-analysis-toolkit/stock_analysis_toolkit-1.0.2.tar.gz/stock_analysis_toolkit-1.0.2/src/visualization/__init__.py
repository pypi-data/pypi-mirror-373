"""
Visualization module for stock analysis.

This package provides functionality for creating and managing
financial charts and visualizations.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

# Import visualization components
from .charts import (
    create_candlestick_chart,
    create_technical_indicators_chart,
    create_sector_performance_chart,
    save_chart,
)
from .dashboard import create_stock_dashboard  # noqa: F401

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("visualization.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Set style
plt.style.use("ggplot")
sns.set_theme(style="whitegrid")


class StockVisualizer:
    """Class for creating visualizations of stock data and indicators."""

    def __init__(self, data: pd.DataFrame, symbol: str):
        """
        Initialize the StockVisualizer.

        Args:
            data: DataFrame containing stock data and indicators
            symbol: Stock symbol (e.g., 'RELIANCE.BO')
        """
        self.data = data.copy()
        self.symbol = symbol
        self.company_name = self._get_company_name(symbol)
        self.output_dir = Path("reports") / "charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def formatted_company_name(self) -> str:
        """Get the formatted company name with exchange suffix."""
        return self.company_name

    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol with exchange suffix.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.BO', 'TCS.NS')

        Returns:
            Formatted company name with exchange
            (e.g., 'Reliance (BSE)', 'TCS (NSE)')
        """
        # Remove any existing exchange suffix
        base_symbol = symbol.split(".")[0]

        # Get the exchange from the suffix
        if symbol.upper().endswith(".BO"):
            exchange = "BSE"
        elif symbol.upper().endswith(".NS"):
            exchange = "NSE"
        else:
            # For indices or symbols without exchange suffix
            return base_symbol

        # Map of base symbols to company names (title case)
        company_map = {
            "RELIANCE": "Reliance",
            "TCS": "TCS",
            "HDFCBANK": "HDFC Bank",
            "INFY": "Infosys",
            "ICICIBANK": "ICICI Bank",
            "HINDUNILVR": "Hindustan Unilever",
            "ITC": "ITC",
            "BHARTIARTL": "Bharti Airtel",
            "SBIN": "SBI",
            "KOTAKBANK": "Kotak Bank",
            "HCLTECH": "HCL Tech",
            "BAJFINANCE": "Bajaj Finance",
            "LT": "L&T",
            "ASIANPAINT": "Asian Paints",
            "AXISBANK": "Axis Bank",
            "MARUTI": "Maruti",
            "SUNPHARMA": "Sun Pharma",
            "TITAN": "Titan",
            "ULTRACEMCO": "UltraTech Cement",
            "NESTLEIND": "Nestle",
            "HDFC": "HDFC",
            "BAJAJFINSV": "Bajaj Finserv",
            "TATAMOTORS": "Tata Motors",
            "POWERGRID": "Power Grid",
            "NTPC": "NTPC",
            "ONGC": "ONGC",
            "COALINDIA": "Coal India",
            "IOC": "IOC",
            "GRASIM": "Grasim",
            "JSWSTEEL": "JSW Steel",
            "TATASTEEL": "Tata Steel",
            "HINDALCO": "Hindalco",
            "CIPLA": "Cipla",
            "DRREDDY": "Dr. Reddy's",
            "WIPRO": "Wipro",
            "TECHM": "Tech Mahindra",
            "HEROMOTOCO": "Hero MotoCorp",
            "EICHERMOT": "Eicher Motors",
            "BAJAJ-AUTO": "Bajaj Auto",
            "BRITANNIA": "Britannia",
            "DIVISLAB": "Divi's Labs",
            "SHREECEM": "Shree Cement",
            "UPL": "UPL",
            "ADANIPORTS": "Adani Ports",
            "TATACONSUM": "Tata Consumer",
            "BPCL": "BPCL",
            "HINDZINC": "Hindustan Zinc",
            "INDUSINDBK": "IndusInd Bank",
            "SBILIFE": "SBI Life",
            "HDFCLIFE": "HDFC Life",
            "BAJAJHLDNG": "Bajaj Holdings",
            "TATAPOWER": "Tata Power",
            "COLPAL": "Colgate",
            "BERGEPAINT": "Berger Paints",
            "PAGEIND": "Page Industries",
            "PIDILITIND": "Pidilite",
            "DABUR": "Dabur",
            "GODREJCP": "Godrej Consumer",
            "HAVELLS": "Havells",
            "JUBLFOOD": "Jubilant Food",
            "M&M": "M&M",
            "MCDOWELL-N": "United Spirits",
            "NESTLE": "Nestle",
            "PEL": "Piramal Enterprises",
            "TATACHEM": "Tata Chemicals",
            "TATACOMM": "Tata Communications",
            "VEDL": "Vedanta",
            "ZEEL": "Zee Entertainment",
        }

        # Get the company name or use the base symbol
        company_name = company_map.get(base_symbol, base_symbol.title())

        # Format as "Company (Exchange)" or just "Company" for well-known ones
        return f"{company_name} ({exchange})" if exchange else company_name

    def _save_plot(
        self, fig, filename: str, width: int = 1200, height: int = 800
    ) -> str:
        """Save plot to file and return the file path."""
        # Generate a clean filename from the symbol
        clean_symbol = self.symbol.replace(".", "_").lower()
        filepath = self.output_dir / f"{clean_symbol}_{filename}.html"

        # Save as HTML for interactive visualization
        fig.write_html(
            filepath,
            full_html=False,
            include_plotlyjs="cdn",
            default_width=f"{width}px",
            default_height=f"{height}px",
        )

        logger.info(f"Saved plot to {filepath}")
        return str(filepath)

    def _save_plot_image(
        self, fig, filename: str, width: int = 1200, height: int = 800
    ) -> str:
        """Save plot as PNG image and return the file path."""
        # Generate a clean filename from the symbol
        clean_symbol = self.symbol.replace(".", "_").lower()
        filepath = self.output_dir / f"{clean_symbol}_{filename}.png"

        # Update layout for better image export
        fig.update_layout(
            width=width,
            height=height,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        # Save as PNG image
        fig.write_image(
            filepath,
            format="png",
            scale=2,  # Higher scale for better quality
            engine="kaleido",  # Required for image export
        )

        logger.info(f"Saved plot image to {filepath}")
        return str(filepath)

    def plot_candlestick(self, days: int = 90) -> str:
        """
        Create an interactive candlestick chart with volume.

        Args:
            days: Number of days to display (default: 90)

        Returns:
            Path to the saved HTML file
        """
        logger.info(f"Creating candlestick chart for {self.symbol}")

        # Get the most recent data
        df = self.data.tail(days).copy()

        # Create subplots with shared x-axis
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"{self.company_name} ({self.symbol}) - Price", "Volume"),
        )

        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price",
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
            ),
            row=1,
            col=1,
        )

        # Add volume bars
        colors = [
            "#26a69a" if close >= open_ else "#ef5350"
            for close, open_ in zip(df["close"], df["open"])
        ]

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["volume"],
                name="Volume",
                marker_color=colors,
                opacity=0.7,
            ),
            row=2,
            col=1,
        )

        # Update layout
        fig.update_layout(
            title=f"{self.company_name} ({self.symbol}) - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            showlegend=False,
            template="plotly_white",
            hovermode="x unified",
            height=800,
            margin=dict(l=50, r=50, t=80, b=50),
            xaxis2_title="Date",
            yaxis2_title="Volume",
        )

        # Update y-axes
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        # Add moving averages if they exist
        for ma in ["ma_20", "ma_50", "ma_200"]:
            if ma in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[ma],
                        name=ma.upper(),
                        line=dict(width=1.5),
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )

        # Save and return
        return self._save_plot(fig, f"candlestick_{days}d")

    def plot_candlestick_image(self, days: int = 90) -> str:
        """
        Create a candlestick chart image for email.

        Args:
            days: Number of days to display (default: 90)

        Returns:
            Path to the saved PNG file
        """
        logger.info(f"Creating candlestick chart image for {self.symbol}")

        # Get the most recent data
        df = self.data.tail(days).copy()

        # Create subplots with shared x-axis
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"{self.company_name} ({self.symbol}) - Price", "Volume"),
        )

        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price",
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
            ),
            row=1,
            col=1,
        )

        # Add volume bars
        colors = [
            "#26a69a" if close >= open_ else "#ef5350"
            for close, open_ in zip(df["close"], df["open"])
        ]

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["volume"],
                name="Volume",
                marker_color=colors,
                opacity=0.7,
            ),
            row=2,
            col=1,
        )

        # Update layout for better image export
        fig.update_layout(
            title=f"{self.company_name} ({self.symbol}) - Price Chart",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            yaxis2_title="Volume",
            height=600,
            showlegend=True,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        # Update y-axes
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        # Add moving averages if they exist
        for ma in ["ma_20", "ma_50", "ma_200"]:
            if ma in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[ma],
                        name=ma.upper(),
                        line=dict(width=1.5),
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )

        # Save as PNG image
        return self._save_plot_image(fig, f"candlestick_{days}d")

    def plot_technical_indicators(self, days: int = 180) -> str:
        """
        Create a chart with technical indicators.

        Args:
            days: Number of days to display (default: 180)

        Returns:
            Path to the saved HTML file
        """
        try:
            # Filter data for the specified number of days
            df = self.data.tail(days).copy()

            # Create subplots with 3 rows for price, volume, and indicators
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=(
                    f"{self.company_name} ({self.symbol}) - " "Technical Indicators",
                    "Volume",
                    "RSI & MACD",
                ),
            )

            # Add candlestick trace
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Price",
                    increasing_line_color="#2ecc71",
                    decreasing_line_color="#e74c3c",
                ),
                row=1,
                col=1,
            )

            # Add moving averages if they exist
            for ma in ["ma_20", "ma_50", "ma_200"]:
                if ma in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[ma],
                            name=ma.upper(),
                            line=dict(width=1.5),
                            opacity=0.7,
                        ),
                        row=1,
                        col=1,
                    )

            # Add Bollinger Bands if they exist
            bb_cols = ["bb_upper", "bb_middle", "bb_lower"]
            if all(col in df.columns for col in bb_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["bb_upper"],
                        name="BB Upper",
                        line=dict(width=1, dash="dash"),
                        line_color="#3498db",
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["bb_middle"],
                        name="BB Middle",
                        line=dict(width=1, dash="dash"),
                        line_color="#7f8c8d",
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["bb_lower"],
                        name="BB Lower",
                        line=dict(width=1, dash="dash"),
                        line_color="#3498db",
                        opacity=0.7,
                        fill="tonexty",
                        fillcolor="rgba(52, 152, 219, 0.1)",
                    ),
                    row=1,
                    col=1,
                )

            # Add volume
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["volume"],
                    name="Volume",
                    marker_color="#7f8c8d",
                    opacity=0.7,
                ),
                row=2,
                col=1,
            )

            # Add RSI if it exists
            if "rsi" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["rsi"],
                        name="RSI",
                        line=dict(color="#9b59b6", width=2),
                    ),
                    row=3,
                    col=1,
                )

                # Add RSI levels
                fig.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="#e74c3c",
                    opacity=0.5,
                    row=3,
                    col=1,
                    annotation_text="Overbought",
                    annotation_position="top right",
                )
                fig.add_hline(
                    y=30,
                    line_dash="dash",
                    line_color="#2ecc71",
                    opacity=0.5,
                    row=3,
                    col=1,
                    annotation_text="Oversold",
                    annotation_position="bottom right",
                )

            # Add MACD if it exists
            if all(col in df.columns for col in ["macd", "macd_signal"]):
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df["macd"] - df["macd_signal"],
                        name="MACD Histogram",
                        marker_color=np.where(
                            (df["macd"] - df["macd_signal"]) > 0, "#2ecc71", "#e74c3c"
                        ),
                        opacity=0.7,
                    ),
                    row=3,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["macd"],
                        name="MACD",
                        line=dict(color="#3498db", width=2),
                    ),
                    row=3,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["macd_signal"],
                        name="Signal",
                        line=dict(color="#f39c12", width=2),
                    ),
                    row=3,
                    col=1,
                )

            # Update layout
            fig.update_layout(
                title=(
                    f"{self.company_name} ({self.symbol}) - " "Technical Indicators"
                ),
                xaxis_rangeslider_visible=False,
                showlegend=True,
                height=1200,
                template="plotly_white",
                hovermode="x unified",
                margin=dict(t=100, b=100, l=50, r=50),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
            )

            # Update y-axis titles
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI / MACD", row=3, col=1)

            # Save and return the plot
            return self._save_plot(fig, f"technical_indicators_{days}d")

        except Exception as e:
            logger.error(
                f"Error generating technical indicators chart for "
                f"{self.symbol}: {str(e)}"
            )
            return ""

    def plot_technical_indicators_image(self, days: int = 180) -> str:
        """
        Create a technical indicators chart image for email.

        Args:
            days: Number of days to display (default: 180)

        Returns:
            Path to the saved PNG file
        """
        try:
            # Filter data for the specified number of days
            df = self.data.tail(days).copy()

            # Create subplots with 3 rows for price, volume, and indicators
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=(
                    f"{self.company_name} ({self.symbol}) - Technical Indicators",
                    "Volume",
                    "RSI & MACD",
                ),
            )

            # Add candlestick trace
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Price",
                    increasing_line_color="#2ecc71",
                    decreasing_line_color="#e74c3c",
                ),
                row=1,
                col=1,
            )

            # Add moving averages if they exist
            for ma in ["ma_20", "ma_50", "ma_200"]:
                if ma in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[ma],
                            name=ma.upper(),
                            line=dict(width=1.5),
                            opacity=0.7,
                        ),
                        row=1,
                        col=1,
                    )

            # Add Bollinger Bands if they exist
            bb_cols = ["bb_upper", "bb_middle", "bb_lower"]
            if all(col in df.columns for col in bb_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["bb_upper"],
                        name="BB Upper",
                        line=dict(width=1, dash="dash"),
                        line_color="#3498db",
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["bb_middle"],
                        name="BB Middle",
                        line=dict(width=1, dash="dash"),
                        line_color="#7f8c8d",
                        opacity=0.7,
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["bb_lower"],
                        name="BB Lower",
                        line=dict(width=1, dash="dash"),
                        line_color="#3498db",
                        opacity=0.7,
                        fill="tonexty",
                        fillcolor="rgba(52, 152, 219, 0.1)",
                    ),
                    row=1,
                    col=1,
                )

            # Add volume
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["volume"],
                    name="Volume",
                    marker_color="#7f8c8d",
                    opacity=0.7,
                ),
                row=2,
                col=1,
            )

            # Add RSI if it exists
            if "rsi" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["rsi"],
                        name="RSI",
                        line=dict(color="#9b59b6", width=2),
                    ),
                    row=3,
                    col=1,
                )

                # Add RSI levels
                fig.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="#e74c3c",
                    opacity=0.5,
                    row=3,
                    col=1,
                    annotation_text="Overbought",
                    annotation_position="top right",
                )
                fig.add_hline(
                    y=30,
                    line_dash="dash",
                    line_color="#2ecc71",
                    opacity=0.5,
                    row=3,
                    col=1,
                    annotation_text="Oversold",
                    annotation_position="bottom right",
                )

            # Add MACD if it exists
            if all(col in df.columns for col in ["macd", "macd_signal"]):
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df["macd"] - df["macd_signal"],
                        name="MACD Histogram",
                        marker_color=np.where(
                            (df["macd"] - df["macd_signal"]) > 0, "#2ecc71", "#e74c3c"
                        ),
                        opacity=0.7,
                    ),
                    row=3,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["macd"],
                        name="MACD",
                        line=dict(color="#3498db", width=2),
                    ),
                    row=3,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["macd_signal"],
                        name="Signal",
                        line=dict(color="#f39c12", width=2),
                    ),
                    row=3,
                    col=1,
                )

            # Update layout for better image export
            fig.update_layout(
                title=f"{self.company_name} ({self.symbol}) - Technical Indicators",
                xaxis_rangeslider_visible=False,
                showlegend=True,
                height=1200,
                template="plotly_white",
                hovermode="x unified",
                margin=dict(t=100, b=100, l=50, r=50),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                paper_bgcolor="white",
                plot_bgcolor="white",
            )

            # Update y-axis titles
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI / MACD", row=3, col=1)

            # Save as PNG image
            return self._save_plot_image(fig, f"technical_indicators_{days}d")

        except Exception as e:
            logger.error(
                f"Error generating technical indicators image for "
                f"{self.symbol}: {str(e)}"
            )
            return ""

    def generate_all_visualizations(
        self, fundamentals: Optional[Dict] = None, for_email: bool = False
    ) -> Dict[str, str]:
        """
        Generate all visualizations for the stock.

        Returns:
            Dictionary mapping visualization names to file paths
        """
        visualizations = {}

        try:
            if for_email:
                # For email, generate PNG images
                visualizations["candlestick"] = self.plot_candlestick_image(days=90)
                visualizations["technical_indicators"] = (
                    self.plot_technical_indicators_image(days=180)
                )
            else:
                # For web, generate HTML files
                visualizations["candlestick"] = self.plot_candlestick(days=90)
                visualizations["technical_indicators"] = self.plot_technical_indicators(
                    days=180
                )

            logger.info(f"Generated all visualizations for {self.symbol}")
            return visualizations

        except Exception as e:
            logger.error(
                f"Error generating visualizations for {self.symbol}: " f"{str(e)}"
            )
            return {}

    @staticmethod
    def create_sector_performance_chart(
        sector_data: pd.DataFrame, output_path: str
    ) -> str:
        """
        Create a bar chart showing performance by sector.

        Args:
            sector_data: DataFrame with sector performance data
            output_path: Directory to save the chart

        Returns:
            Path to the saved chart file
        """
        try:
            # Sort by performance
            sector_data = sector_data.sort_values("change_pct", ascending=False)

            # Create figure
            fig = px.bar(
                sector_data,
                x="sector",
                y="change_pct",
                color="change_pct",
                color_continuous_scale="RdYlGn",
                title="Sector Performance",
                labels={"change_pct": "Change (%)", "sector": "Sector"},
            )

            # Update layout
            fig.update_layout(
                template="plotly_white",
                xaxis_tickangle=-45,
                coloraxis_showscale=False,
                height=600,
                margin=dict(l=50, r=50, t=80, b=150),
                xaxis_title="",
                yaxis_title="Change (%)",
                title_x=0.5,
                title_y=0.95,
                title_font=dict(size=20),
                xaxis_tickfont=dict(size=12),
                yaxis_tickfont=dict(size=12),
            )

            # Add value annotations
            fig.update_traces(
                texttemplate="%{y:.1f}%", textposition="outside", textfont_size=12
            )

            # Ensure output directory exists
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save the chart
            chart_path = output_dir / "sector_performance.html"
            fig.write_html(
                chart_path,
                full_html=False,
                include_plotlyjs="cdn",
                default_width="100%",
                default_height="100%",
            )

            logger.info(f"Saved sector performance chart to {chart_path}")
            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating sector performance chart: {str(e)}")
            return ""


# Backward compatibility exports

__all__ = [
    "StockVisualizer",
    "create_candlestick_chart",
    "create_technical_indicators_chart",
    "create_sector_performance_chart",
    "create_stock_dashboard",
    "save_chart",
]
