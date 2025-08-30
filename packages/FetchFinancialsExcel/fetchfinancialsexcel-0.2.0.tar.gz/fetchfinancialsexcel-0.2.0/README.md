# FetchFinancialsExcel

A Python package for fetching and analyzing fundamental financial data using the EODHD API in the background. This package allows you to process Excel files containing stock tickers to generate financial analysis reports. It reads ticker symbols from an input Excel sheet, queries the EODHD API for relevant financial data, and outputs a comprehensive analysis report in a new Excel file.

## Features

- **Concurrent Data Fetching**: Efficiently fetches financial data for multiple stocks concurrently.
- **Comprehensive Analysis**: Calculate key financial metrics not directly avaibale in EODHD including:
  - Conservative investment scores
  - Quality scores
  - P/E ratios, ROCE, revenue growth, EPS growth
  - Free cash flow metrics, buyback data, insider ownership
  - Technical indicators and moving averages
- **Excel Integration**: Read ticker lists from Excel file and output results to an file

## Installation

### From PyPI
```bash
pip install FetchFinancialsExcel
```

### Development Installation
```bash
git clone https://github.com/username/FetchFinancialsExcel.git
cd FetchFinancialsExcel
pip install -r requirements.txt
pip install -e .
```

## Prerequisites

1. **EODHD API Key**: You need an API key from [EODHD](https://eodhd.com/) to fetch financial data

## Start

### 1. Prepare Excel File

Create an Excel file (`.xlsx`) with the following format:

<img src="examples/figures/ticker_list_example.png" alt="Alt text" width="200"/>

**Important Notes:**
- First Column: Company names
- Second Column: Ticker symbols
- Note! Make sure to use proper ticker formats (e.g., `DANSKE.CO` for Copenhagen exchange) that are compatible with EODHD. 

### 2. Run the Analysis

```bash
fetch-financials-excel --api-key YOUR_EODHD_API_KEY --input tickers.xlsx --output results.xlsx
```

### 3. View Results

The output Excel file will contain comprehensive financial data and analysis for all tickers.

## Command Line Usage

### Basic Usage
```bash
fetch-financials-excel --api-key YOUR_API_KEY --input input.xlsx --output output.xlsx
```

### Advanced Usage
```bash
# Custom number of concurrent workers (default: 10)
fetch-financials-excel --api-key YOUR_API_KEY --input tickers.xlsx --output results.xlsx --workers 5

# Short form arguments
fetch-financials-excel --api-key YOUR_API_KEY -i tickers.xlsx -o results.xlsx -w 5
```

### Command Line Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--api-key` | | Yes | Your EODHD API key |
| `--input` | `-i` | Yes | Path to input Excel file |
| `--output` | `-o` | YEs | Path to output Excel file |
| `--workers` | `-w` | | Number of concurrent workers (1-50, default: 10) |
| `--version` | | | Show version information |
| `--help` | `-h` | | Show help message |

## Python API Usage

```python
from fetchfinancialsexcel import FundamentalDataFetcher

# Initialize with your API key
fetcher = FundamentalDataFetcher(api_key="YOUR_EODHD_API_KEY")

# Process an Excel file
fetcher.process_excel_file(
    input_file="path/to/tickers.xlsx",
    output_file="path/to/results.xlsx",
    max_workers=10
)

# Or work with data directly
company_list, ticker_list = fetcher.extract_tickers_from_excel("tickers.xlsx")
df, separate_data = fetcher.fetch_all_data(company_list, ticker_list)
analyzed_df = fetcher.analyze_data(df, separate_data)
```

## Output Data

The output Excel file contains the following types of data:

### Financial Metrics
- **Price Information**: Current price, currency, sector
- **Valuation Ratios**: P/E ratios (current and 5-year average), ROCE
- **Growth Metrics**: Revenue growth, EPS growth, asset growth
- **Profitability**: Gross profitability, free cash flow metrics
- **Balance Sheet**: Accruals, total yield, insider ownership percentage

### Analysis Scores
- **Greenblatt Formula**: Magic Formula ranking based on P/E and ROCE
- **Conservative Formula**: Risk-adjusted scoring based on volatility, NPY, and momentum
- **Quality Score**: Overall quality assessment

### Technical Data
- **Moving Averages**: Various period moving averages
- **Volatility Metrics**: Historical volatility measures
- **Price Momentum**: Momentum indicators

## Testing

Before pushing changes, run the test script to validate functionality:

```bash
python test_package.py
```

## Author

**Carl Viggo Gravenhorst-Lövenstierne**