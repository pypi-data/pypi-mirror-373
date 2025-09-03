# TuData

A Python library for accessing Tushare financial data through optimized API.

## Features

- 🚀 **Optimized Performance**: Built-in connection pooling and retry mechanisms
- 📊 **Comprehensive Data**: Access to stocks, funds, futures, options, and cryptocurrency data
- 🔧 **Easy to Use**: Simple and intuitive API interface
- 🛡️ **Robust**: Automatic error handling and retry logic
- 📈 **Real-time**: Support for real-time and historical financial data

## Installation

```bash
pip install tudata
```

## Quick Start

### 1. Set Your Token

```python
import tudata as ts

# Set your Tushare token (only need to do this once)
ts.set_token('your_tushare_token_here')
```

### 2. Initialize API Client

```python
# Initialize the API client
api = ts.pro_api()

# Or initialize with token directly
api = ts.pro_api(token='your_token_here')
```

### 3. Fetch Data

```python
# Get stock basic information
stocks = api.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
print(stocks.head())

# Get daily trading data
daily_data = api.daily(ts_code='000001.SZ', start_date='20240101', end_date='20241201')
print(daily_data.head())

# Get trading calendar
cal = api.trade_cal(exchange='', start_date='20240101', end_date='20241201')
print(cal.head())
```

### 4. Use Pro Bar for Time Series Data

```python
# Get historical price data with pro_bar
df = ts.pro_bar(ts_code='000001.SZ', start_date='20240101', end_date='20241201', freq='D')
print(df.head())
```

## API Reference

### Core Classes

#### `pro_api`

The main API client class for accessing Tushare data.

```python
api = ts.pro_api(token=None)
```

**Parameters:**
- `token` (str, optional): Your Tushare API token. If not provided, will use stored token.

#### Main Methods

##### Stock Data
- `stock_basic(**kwargs)` - Get basic stock information
- `daily(**kwargs)` - Get daily trading data
- `weekly(**kwargs)` - Get weekly trading data  
- `monthly(**kwargs)` - Get monthly trading data
- `adj_factor(**kwargs)` - Get adjustment factors
- `daily_basic(**kwargs)` - Get daily basic trading metrics

##### Financial Statements
- `income(**kwargs)` - Get income statement data
- `balancesheet(**kwargs)` - Get balance sheet data  
- `cashflow(**kwargs)` - Get cash flow statement data
- `fina_indicator(**kwargs)` - Get financial indicators

##### Market Data
- `moneyflow(**kwargs)` - Get money flow data
- `top_list(**kwargs)` - Get top gainers/losers
- `limit_list_d(**kwargs)` - Get daily limit up/down stocks

##### Index Data
- `index_basic(**kwargs)` - Get index basic information
- `index_daily(**kwargs)` - Get index daily data
- `index_weight(**kwargs)` - Get index constituent weights

##### Fund Data
- `fund_basic(**kwargs)` - Get fund basic information
- `fund_nav(**kwargs)` - Get fund net asset value
- `fund_daily(**kwargs)` - Get fund daily trading data

##### And many more...

### Utility Functions

#### `set_token(token)`
Store your Tushare API token locally.

**Parameters:**
- `token` (str): Your Tushare API token

#### `get_token()`
Retrieve the stored Tushare API token.

**Returns:**
- `str`: The stored token, or None if not set

#### `pro_bar(ts_code, start_date, end_date, freq='D', **kwargs)`
Get time series data with enhanced functionality.

**Parameters:**
- `ts_code` (str): Stock code (e.g., '000001.SZ')
- `start_date` (str): Start date in 'YYYYMMDD' format
- `end_date` (str): End date in 'YYYYMMDD' format  
- `freq` (str): Data frequency ('D', 'W', 'M', etc.)

## Configuration

### Connection Settings

The library includes optimized connection settings:

- **Connection Pooling**: 10 connections with max 20 connections
- **Retry Logic**: Automatic retry on 500, 502, 503, 504 errors
- **Timeouts**: 5 seconds connection timeout, 30 seconds read timeout

### Error Handling

The library automatically handles:

- Network timeouts and retries
- Invalid token errors
- Rate limiting
- JSON parsing errors

## Examples

### Get Stock List

```python
import tudata as ts

api = ts.pro_api()

# Get all listed stocks
stocks = api.stock_basic(list_status='L')
print(f"Total stocks: {len(stocks)}")
print(stocks[['ts_code', 'name', 'industry']].head())
```

### Get Historical Prices

```python
# Get 1 year of daily data for a specific stock
data = api.daily(
    ts_code='000001.SZ',
    start_date='20230101', 
    end_date='20231231'
)

print(data[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head())
```

### Get Financial Indicators

```python
# Get financial indicators for a stock
indicators = api.fina_indicator(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20231231'
)

print(indicators[['end_date', 'roe', 'roa', 'eps']].head())
```

### Real-time Data

```python
# Get real-time quotes (requires special permission)
quotes = api.realtime_quote(ts_code='000001.SZ,000002.SZ')
print(quotes)
```

## Requirements

- Python 3.7+
- pandas >= 1.0.0
- requests >= 2.25.0
- urllib3 >= 1.26.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.

## Disclaimer

This library is for educational and research purposes. Please ensure you comply with Tushare's terms of service and any applicable financial data regulations. 