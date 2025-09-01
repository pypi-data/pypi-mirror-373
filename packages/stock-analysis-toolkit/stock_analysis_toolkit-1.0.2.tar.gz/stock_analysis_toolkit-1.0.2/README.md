# Indian Stock Market Analysis Tool

A comprehensive Python-based tool for analyzing Indian stocks using technical and fundamental analysis. This tool fetches stock data from various sources, performs in-depth analysis, generates visualizations, and creates detailed reports.

## Features

- **Data Collection**: Fetches historical and real-time stock data from multiple sources
  - Supports BSE stocks (e.g., `500325.BO` for RELIANCE)
  - Supports NSE stocks (e.g., `RELIANCE.NS` or `NSE:RELIANCE`)
  - Supports indices (e.g., `^NSEI` for NIFTY 50)
- **Technical Analysis**: Implements various technical indicators (RSI, MACD, Bollinger Bands, Moving Averages, etc.)
- **Fundamental Analysis**: Analyzes key financial metrics (P/E, ROE, Debt/Equity, etc.)
- **Visualization**: Generates interactive charts and dashboards
- **Reporting**: Creates detailed HTML reports with analysis and recommendations
- **Email Notifications**: Option to send reports via email

## Prerequisites

- Python 3.8+
- Required Python packages (see `requirements.txt`)
- Alpha Vantage API key (optional, for additional fundamental data)
- Gmail account (for email functionality)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stock-analysis-tool
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install TA-Lib (required for technical analysis):
   - **macOS**: `brew install ta-lib`
   - **Linux**: `sudo apt-get install -y python3-ta-lib`
   - **Windows**: Download the appropriate wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)

5. Create a `.env` file in the project root and add your API keys:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_specific_password
   ```

## Usage

### Basic Usage

Analyze the top 10 BSE stocks:
```bash
python src/main.py
```

### Command Line Options

```
usage: main.py [-h] [--stocks [STOCKS ...]] [--days DAYS] [--email EMAIL]
              [--report-dir REPORT_DIR] [--top TOP] [--all]

Stock Analysis Tool

optional arguments:
  -h, --help            show this help message and exit
  --stocks [STOCKS ...] List of stock symbols to analyze (e.g., RELIANCE.BO TCS.BO)
  --days DAYS           Number of days of historical data to fetch (default: 365)
  --email EMAIL         Email address to send the report to
  --report-dir REPORT_DIR
                        Directory to save the report (default: reports)
  --top TOP             Analyze top N BSE stocks by market cap
  --all                 Analyze all top BSE stocks
```

### Examples

1. Analyze specific stocks:
   ```bash
   python3 src/main.py --stocks RELIANCE.BO TCS.BO HDFCBANK.BO
   ```

2. Analyze top 5 BSE stocks and email the report:
   ```bash
   python3 src/main.py --top 5 --email your-email@example.com
   ```

3. Analyze all top BSE stocks with 2 years of data:
   ```bash
   python3 src/main.py --all --days 730
   ```

4. Analyze NIFTY50 index:
   ```bash
   python3 src/main.py --stocks ^NSEI --days 365
   python3 src/main.py --stocks ^NSEI --days 365 --email your-email@example.com
   ```

5. Analyze top 10 BSE stocks and email the report:
   ```bash
   python3 src/main.py --top 10 --email your-email@example.com
   ```

6. Analyze top 10 BSE stocks and email the report:
   ```bash
   cd HOME_PATH/stock_analysis && PYTHONPATH=HOME_PATH/stock_analysis python3 -m src.main --email your-email@example.com
   ```


## Project Structure

```
stock-analysis/
├── config/                 # Configuration files
│   └── config.py           # Application configuration
├── data/                   # Data storage
│   └── cache/              # Cached stock data
├── logs/                   # Log files
├── reports/                # Generated reports
│   └── charts/             # Chart visualizations
├── src/                    # Source code
│   ├── data_fetcher.py     # Data collection from APIs
│   ├── technical_analysis.py # Technical indicators and analysis
│   ├── visualization.py    # Data visualization
│   └── main.py             # Main application and CLI
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Supported Stock Exchanges

- **BSE (Bombay Stock Exchange)**: Use `.BO` suffix (e.g., `RELIANCE.BO`)
- **NSE (National Stock Exchange)**: Use `.NS` suffix (e.g., `RELIANCE.NS`)

## Data Sources

- Primary: Google Finance
- Fallback: Yahoo Finance
- Additional: Alpha Vantage (for fundamental data, requires API key)

## Email Configuration

To enable email notifications:

1. Enable "Less secure app access" in your Gmail account settings or generate an App Password
2. Set the following environment variables in your `.env` file:
   ```
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_specific_password
   ```

## Limitations

- Free API tiers may have rate limits
- Some fundamental data may not be available for all stocks
- Analysis should be used for informational purposes only

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with a licensed financial advisor before making investment decisions.
