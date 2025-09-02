# Fund Insight Engine

A Python package providing utility functions for fund code management and analysis. This package helps streamline the process of handling fund-related data and provides insights into fund operations.

## Features

- Fund code retrieval and validation
  - Support for various fund types (equity, mixed, bond, etc.)
  - Fund class categorization (mother fund, general, class fund)
  - Division-based fund code management
- Integration with financial dataset preprocessing
- AWS S3 integration for data storage

## Installation

You can install the package using pip:

```bash
pip install fund-insight-engine
```

## Requirements

- financial_dataset_preprocessor>=0.3.7
- aws_s3_controller>=0.7.5
- mongodb_controller>=0.2.5
- universal_timeseries_transformer>=0.1.6

## Usage

```python
from fund_insight_engine import fund_codes_retriever

# Get fund codes by type
equity_funds = fund_codes_retriever.get_fund_codes_equity_type()
mixed_funds = fund_codes_retriever.get_fund_codes_equity_mixed_type()

# Get fund codes by class
mother_funds = fund_codes_retriever.get_fund_codes_mother()
class_funds = fund_codes_retriever.get_fund_codes_class()

# Get fund names mapping
fund_names = fund_codes_retriever.get_mapping_fund_names_main()
```

## Version History

### 0.8.1 (2025-07-03)

- Added additional market indices (Asia, ETC1) for benchmark comparison
- Added compound indices functionality
- Added trust fund codes module
- Updated dependencies to support enhanced index operations

### 0.8.0 (2025-06-26)

- Added fund_utils.py with enhanced fund data processing utilities
- Improved date reference handling in fund configuration modules
- Updated benchmark names in API utilities
- Enhanced timeseries data processing

### 0.7.9 (2025-06-23)

- Fixed date reference selection logic to use fund-specific data
- Updated benchmark names in API utilities
- Improved data retrieval efficiency

### 0.7.8 (2025-06-21)

- Fixed function naming in server_api module to prevent confusion
- Improved API function clarity

### 0.7.7 (2025-06-21)

- Added legacy web server API functions in server_api module
- Added utility functions for API data transformation

### 0.7.6 (2025-06-20)

- Fixed package installation issue by including requirements.txt in the package
- Same features as 0.7.5

### 0.7.5 (2025-06-20)

- Updated dependency version for universal_timeseries_transformer to 0.2.7
- Updated dependency version for timeseries_performance_calculator to 0.2.2
- Enhanced data output modules for future feature additions

### 0.7.4 (2025-06-01)

- Fixed critical issue with package structure
- Reverted unintended code additions

### 0.7.3 (2025-06-01)

- [DEPRECATED] This version contains errors and should not be used

### 0.7.2 (2025-05-30)

- Updated dependency version for universal_timeseries_transformer to 0.1.5
- Added columns_ref property to Fund class for convenient column reference

### 0.7.1 (2025-05-30)

- Enhanced timeseries functionality with price extension to previous date
- Added constants for fund price column name and initial default price
- Improved import structure for better code organization

### 0.7.0 (2025-05-30)

- Major architectural update with Fund class implementation
- Comprehensive API for accessing all fund-related data
- Streamlined data pipeline for efficient fund data retrieval
- Enhanced integration between different data sources
- Improved code structure and organization

### 0.6.3 (2025-05-28)

- Added market data retrieval functionality with Bloomberg tickers
- Implemented global currency, bond, and index data retrieval
- Reorganized benchmark retrieval into market_retriever module

### 0.6.2 (2025-05-27)

- Added portfolio snapshot retrieval functionality
- Implemented functions to get all fund portfolios at a specific date

### 0.6.1 (2025-05-27)

- Fixed portfolio customizer to preserve original DataFrame
- Corrected parameter naming in portfolio fetcher functions

### 0.6.0 (2025-05-27)

- Enhanced portfolio data retrieval with new data source (menu2206)
- Added stock portion retrieval functionality
- Improved portfolio customization capabilities
- Updated dependency requirements

### 0.5.10 (2025-05-26)

- Modified fund price retrieval to maintain string date format
- Optimized data processing for better compatibility with existing systems
- Removed unnecessary data transformation

### 0.5.9 (2025-05-26)

- Added fund price retrieval functionality
- Enhanced time series data processing with datetime conversion
- Added multi-fund price retrieval capability

### 0.5.8 (2025-05-26)

- Added benchmark retrieval functionality (KOSPI, KOSDAQ, KOSPI200)
- Restructured fund mapping modules for better organization
- Improved fund division constants and mapping structure

### 0.5.7 (2025-05-20)

- Enhanced fund mapping functionality with priority-based mappings
- Added new utility function for filtering mappings
- Improved mapping organization for better code maintainability

### 0.5.6 (2025-05-20)

- Refactored timeseries data transformation logic
- Improved code organization in timeseries_manager module
- Enhanced data processing efficiency

### 0.5.5 (2025-05-20)

- Fixed minor bugs in portfolio module
- Improved error handling in timeseries_manager
- Enhanced code stability and performance

### 0.5.4 (2025-05-19)

- Enhanced timeseries module with additional fund data fields
- Added dedicated timeseries_manager module for improved data management
- Expanded fund data analysis capabilities with more metrics
- Reorganized module structure for better maintainability

### 0.5.3 (2025-05-19)

- Restructured module organization for better extensibility
- Renamed modules to prevent potential naming conflicts
- Improved import paths for cleaner code structure

### 0.5.2 (2025-05-19)

- Added time series query class (timeseries module)
- Added Fund class (integrated time series and portfolio query)

### 0.5.1 (2025-05-16)

- Added `option_verbose` parameter to portfolio-related classes
- Improved logging functionality

### 0.5.0 (2025-05-16)

- Enhanced fund mapping functions (mapping_classes, mapping_types, mappings_divisions, etc.)
- Strengthened fund code and fund name mapping capabilities
- Improved fund mapping module structure

### 0.4.6 (2025-05-16)

- Renamed module: changed `all` module to `all_funds`
- Prevented name collision with Python standard library

### 0.4.5 (2025-05-16)

- Fixed portfolio data fetcher log output bug
- Changed default options for portfolio data loading

### 0.4.4 (2025-05-15)

- Added empty result handling logic to fund information retrieval functions
- Improved exception handling to return None when no data is found

### 0.4.3 (2025-05-15)

- Fixed MongoDB collection import path bug
- Improved stability of fund information retrieval features

### 0.4.2 (2025-05-15)

- Fixed module import bug (added fund_info module)
- Improved code stability

### 0.4.1 (2025-05-15)

- Added fund NAV, price, and AUM retrieval functions (get_fund_price, get_fund_nav, etc.)
- Improved code structure and module reorganization
- Optimized MongoDB data access

### 0.4.0 (2025-05-14)

- Added variable fund code search functionality (get_fund_codes_variable_main)
- Cleaned up code and removed unnecessary comments
- Optimized fund code classification by type

### 0.3.9 (2025-05-14)

- Added fund code classification functions by type (get_fund_codes_equity, get_fund_codes_equity_mixed, etc.)
- Added type-based fund code search functionality combined with main fund filtering
- Improved code structure and optimized inter-module dependencies

### 0.3.8 (2025-05-14)

- Improved fund name filtering functionality (added specific keyword exclusion)
- Enhanced fund code search accuracy

### 0.3.7 (2025-05-14)

- Enhanced fund code management functionality
- Improved code organization and documentation
- Optimized performance for fund code retrieval functions

### 0.3.4 (2025-05-13)

- Added practical unit conversion for AUM data (KRW trillion, USD billion)
- Enhanced firm_aum module with get_firm_aum_since_inception function
- Improved data presentation for financial reporting

### 0.3.3 (2025-05-13)

- Added firm_aum module for company AUM time series analysis
- Implemented currency conversion features (KRW to USD)
- Improved function naming for better code readability
- Enhanced time series data handling capabilities

### 0.3.2 (2025-04-24)

- Added portfolio retrieval functionality with MongoDB integration
- Implemented Portfolio class for easy fund portfolio management
- Enhanced data fetching capabilities for portfolio analysis

### 0.3.1 (2025-04-24)

- Added fund type classification functions for retrieving fund codes by investment type
- Improved code organization with dedicated constants modules
- Refactored class-based fund code functions for better consistency

### 0.3.0 (2025-04-24)

- Fixed critical bug in `get_df_funds_main` function that incorrectly filtered class funds
- Improved stability and reliability of fund classification functions
- Major version bump for API stability

### 0.2.9 (2025-04-24)

- Restructured fund code classification into dedicated submodules
- Added division-based fund code retrieval functions
- Improved organization with constants separation for better maintainability

### 0.2.8 (2025-04-24)

- Added new `fund_data_retriever` module with fund code classification functions
- Enhanced MongoDB utilities with snapshot data retrieval functions
- Added fund code application utilities for better fund classification

### 0.2.7 (2025-04-19)

- Added `get_mapping_fund_names` to top-level imports for easier access
- Improved method accessibility for common mapping functions

### 0.2.6 (2025-04-19)

- requirements.txt is now automatically reflected in setup.py's install_requires (single-source dependency management)
- Expanded transform_data_to_df with new options and flexibility
- Various module enhancements and bug fixes

### 0.1.3

- Added MongoDB integration
  - Added `mongodb_retriever` module for MongoDB data access
  - Added fund name mapping from MongoDB data source
  - Added `menu2205_retriever` module for specific fund data retrieval
  - Added dependency on `mongodb_controller` and `shining_pebbles` packages

### 0.1.2

- Added `get_mapping_fund_names` to top-level imports for easier access

### 0.1.1

- Enhanced fund code utilities
  - Added mapping functions by fund type, class, and division
  - Added FUND_CLASSES and FUND_TYPES constants
  - Added pseudo_consts.py for future use
  - Fixed date_ref parameter handling in division mapping functions
  - Improved code organization and type hints

### 0.1.0 (Initial Release)

- Basic fund code management functionality
  - Fund type-based retrieval
  - Fund class-based retrieval
  - Division-based management
- AWS S3 integration
- Financial dataset preprocessing integration

## License

This project is licensed under the MIT License.

## Author

**June Young Park**
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

## Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
