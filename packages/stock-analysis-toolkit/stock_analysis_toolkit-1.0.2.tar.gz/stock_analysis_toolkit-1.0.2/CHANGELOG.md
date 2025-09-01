# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-08-30
### Added
- Type checking support with mypy configuration
- Type stubs for better code quality (pandas-stubs, types-requests, types-seaborn)
- GitHub Actions workflow improvements for better CI/CD

### Changed
- Updated dependencies to latest stable versions
- Improved error handling in data fetching components
- Enhanced documentation and type hints

### Fixed
- Resolved workflow issues with unsupported command-line arguments
- Fixed type checking errors throughout the codebase
- Improved handling of optional dependencies
- Fixed issues with email reporting and chart generation

## [1.0.0] - 2025-08-27
### Added
- Initial stable release of Stock Analysis Toolkit
- Core functionality for stock data fetching and analysis
- Support for multiple data sources including yfinance and Alpha Vantage
- Technical analysis indicators and visualization tools
- Email reporting capabilities
- GitHub Actions workflow for automated testing and deployment
- Comprehensive test suite for data fetching and analysis

### Changed
- Migrated to Pydantic v2 with updated validator syntax
- Improved error handling and logging throughout the codebase
- Better documentation and type hints for all public APIs
- Enhanced data validation and error messages
- Updated dependencies to their latest stable versions
- Improved handling of missing or incomplete market data

### Fixed
- Resolved SSL/TLS handshake issues with yfinance
- Fixed NIFTY 50 PE ratio fetching with proper error handling
- Addressed various bugs and performance issues
- Fixed test functions to use proper assertions
- Resolved deprecation warnings in yfinance integration
- Improved handling of edge cases in data processing

### Security
- Secured GitHub Actions workflow to handle sensitive data
- Removed hardcoded credentials and API keys
- Added input validation for all external data sources
- Improved error handling for API rate limiting and timeouts
