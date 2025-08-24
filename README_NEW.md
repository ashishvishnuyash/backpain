# Bloomberg Terminal-like Backend

A comprehensive financial data API for Indian markets built with FastAPI and yfinance, providing real-time stock data, technical analysis, market screening, and portfolio tracking capabilities.

## 🚀 Features

### Core Features
- **Real-time Stock Quotes**: Get live stock prices, changes, and key metrics
- **Historical Data Analysis**: Access historical price data with customizable periods
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, and more
- **Fundamentals Analysis**: Comprehensive financial metrics and ratios
- **Financial Statements**: Income statements, balance sheets, and cash flow
- **Holdings Analysis**: Institutional and insider ownership data
- **Market Analysis**: Sector performance and market breadth
- **Search & Lookup**: Find stocks by name or symbol
- **Sector Analysis**: Sector-wise performance and metrics
- **Advanced Screening**: Multi-criteria stock filtering
- **Portfolio Tracking**: Monitor multiple stocks simultaneously
- **News & Sentiment**: Get latest news and sentiment analysis for stocks
- **WebSocket Real-time Updates**: Live market data streaming
- **Indian Market Focus**: Optimized for NSE and BSE stocks

### Technical Features
- **Flexible API Design**: All endpoints use *args and **kwargs for maximum flexibility
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Caching**: Intelligent caching for improved performance
- **Error Handling**: Comprehensive error handling and logging
- **Async Support**: Full async/await support for high concurrency
- **Multiple Request Support**: Handle multiple concurrent requests efficiently

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend3
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Core Endpoints

#### 1. Health Check
```http
GET /health
```

#### 2. Get Indian Stock Symbols
```http
GET /symbols/indian-stocks
```

#### 3. Stock Quote
```http
POST /stock/quote
Content-Type: application/json

# Using kwargs
{
    "symbol": "RELIANCE"
}

# Using args
["RELIANCE"]
```

#### 4. Historical Data
```http
POST /stock/historical
Content-Type: application/json

# Using kwargs
{
    "symbol": "TCS",
    "period": "1y",
    "interval": "1d"
}

# Using args
["TCS", "1y", "1d"]
```

#### 5. Technical Indicators
```http
POST /stock/technical-indicators
Content-Type: application/json

# Using kwargs
{
    "symbol": "HDFC",
    "period": "6mo",
    "interval": "1d"
}

# Using args
["HDFC", "6mo", "1d"]
```

#### 6. Fundamentals Analysis
```http
POST /stock/fundamentals
Content-Type: application/json

{
    "symbol": "RELIANCE"
}
```

#### 7. Financial Statements
```http
POST /stock/financials
Content-Type: application/json

{
    "symbol": "TCS",
    "period": "annual"
}
```

#### 8. Holdings Analysis
```http
POST /stock/holdings
Content-Type: application/json

{
    "symbol": "HDFC"
}
```

#### 9. Stock News
```http
POST /stock/news
Content-Type: application/json

{
    "symbol": "INFY",
    "count": 10
}
```

#### 10. Market Analysis
```http
POST /market/analysis
Content-Type: application/json

{
    "market": "NSE"
}
```

#### 11. Market Screener
```http
POST /market/screener
Content-Type: application/json

{
    "market_cap_min": 1000000000,
    "pe_max": 25,
    "sector": "IT"
}
```

#### 12. Advanced Screener
```http
POST /screener/advanced
Content-Type: application/json

{
    "market_cap_min": 1000000000,
    "pe_max": 25,
    "pb_max": 3,
    "dividend_yield_min": 0.02,
    "sector": "IT",
    "return_on_equity_min": 0.15
}
```

#### 13. Search Stocks
```http
POST /search/stocks
Content-Type: application/json

{
    "query": "BANK",
    "limit": 10
}
```

#### 14. Sector Analysis
```http
POST /sector/analysis
Content-Type: application/json

{
    "sector": "IT",
    "limit": 20
}
```

#### 15. Portfolio Tracking
```http
POST /portfolio/track
Content-Type: application/json

{
    "symbols": ["RELIANCE", "TCS", "HDFC", "INFY"]
}
```

#### 16. Market Indices
```http
GET /market/indices
```

#### 17. WebSocket Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/real-time');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time data:', data);
};
```

## 📊 Supported Indian Stocks

The API supports major Indian stocks including:

### NIFTY 50 Stocks
- RELIANCE, TCS, HDFC, INFY, ICICI
- HINDUNILVR, ITC, SBIN, BHARTIARTL
- KOTAKBANK, AXISBANK, ASIANPAINT
- MARUTI, SUNPHARMA, TATAMOTORS
- WIPRO, ULTRACEMCO, TECHM, NESTLEIND
- POWERGRID, HCLTECH, BAJFINANCE
- ADANIENT, JSWSTEEL, TATACONSUM
- BAJAJFINSV, ONGC, COALINDIA

### Market Indices
- NIFTY50 (^NSEI)
- SENSEX (^BSESN)
- NIFTYBANK (^NSEBANK)
- NIFTYIT (^CNXIT)
- NIFTYPHARMA (^CNXPHARMA)

## 🔧 Configuration

The application can be configured through `config.py`:

```python
# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# Rate Limiting
DEFAULT_RATE_LIMIT = 100
DEFAULT_RATE_WINDOW = 60

# Cache Settings
DEFAULT_CACHE_TTL = 300  # 5 minutes
QUOTE_CACHE_TTL = 60     # 1 minute
```

## 📈 Technical Indicators

The API provides comprehensive technical analysis including:

### Moving Averages
- Simple Moving Average (SMA) - 20, 50, 200 periods
- Exponential Moving Average (EMA)

### Oscillators
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator
- Williams %R

### Volatility Indicators
- Bollinger Bands
- Average True Range (ATR)

### Volume Indicators
- On-Balance Volume (OBV)
- Volume Price Trend (VPT)
- Volume SMA

### Support & Resistance
- Pivot Point Analysis
- Fibonacci Retracements

## 🚦 Rate Limiting

The API implements intelligent rate limiting:

- **Quote Endpoints**: 200 requests per minute
- **Historical Data**: 100 requests per minute
- **Technical Analysis**: 50 requests per minute
- **Fundamentals**: 50 requests per minute
- **Financials**: 30 requests per minute
- **Holdings**: 30 requests per minute
- **News**: 50 requests per minute
- **Market Analysis**: 50 requests per minute
- **Screener**: 20 requests per minute
- **Search**: 100 requests per minute
- **Sector Analysis**: 30 requests per minute
- **Portfolio**: 100 requests per minute

## 💾 Caching

Built-in caching system for improved performance:

- **Stock Quotes**: 1 minute cache
- **Historical Data**: 5 minutes cache
- **Technical Indicators**: 5 minutes cache
- **Fundamentals**: 10 minutes cache
- **Financials**: 30 minutes cache
- **Holdings**: 30 minutes cache
- **News**: 10 minutes cache
- **Market Analysis**: 5 minutes cache
- **Search**: 10 minutes cache
- **Sector Analysis**: 15 minutes cache
- **Market Screener**: 15 minutes cache

## 🔍 Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Get stock quote
def get_stock_quote(symbol):
    response = requests.post(f"{BASE_URL}/stock/quote", 
                           json={"symbol": symbol})
    return response.json()

# Get historical data
def get_historical_data(symbol, period="1y"):
    response = requests.post(f"{BASE_URL}/stock/historical",
                           json={"symbol": symbol, "period": period})
    return response.json()

# Get technical indicators
def get_technical_indicators(symbol):
    response = requests.post(f"{BASE_URL}/stock/technical-indicators",
                           json={"symbol": symbol})
    return response.json()

# Get fundamentals
def get_fundamentals(symbol):
    response = requests.post(f"{BASE_URL}/stock/fundamentals",
                           json={"symbol": symbol})
    return response.json()

# Advanced screener
def screen_stocks(**filters):
    response = requests.post(f"{BASE_URL}/screener/advanced", json=filters)
    return response.json()

# Usage
if __name__ == "__main__":
    # Get RELIANCE quote
    quote = get_stock_quote("RELIANCE")
    print("RELIANCE Quote:", json.dumps(quote, indent=2))
    
    # Get TCS fundamentals
    fundamentals = get_fundamentals("TCS")
    print("TCS Fundamentals:", json.dumps(fundamentals, indent=2))
    
    # Screen IT stocks with P/E < 25
    it_stocks = screen_stocks(pe_max=25, sector="IT")
    print("IT Stocks:", len(it_stocks["screener_results"]), "matches")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Get stock quote
async function getStockQuote(symbol) {
    try {
        const response = await axios.post(`${BASE_URL}/stock/quote`, {
            symbol: symbol
        });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// Get fundamentals
async function getFundamentals(symbol) {
    try {
        const response = await axios.post(`${BASE_URL}/stock/fundamentals`, {
            symbol: symbol
        });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// Get market analysis
async function getMarketAnalysis() {
    try {
        const response = await axios.post(`${BASE_URL}/market/analysis`, {
            market: "NSE"
        });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// WebSocket connection for real-time data
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8000/ws/real-time');

ws.on('open', function open() {
    console.log('Connected to real-time data stream');
});

ws.on('message', function incoming(data) {
    const marketData = JSON.parse(data);
    console.log('Real-time update:', marketData);
});

// Usage
async function main() {
    const relianceQuote = await getStockQuote('RELIANCE');
    console.log('RELIANCE Quote:', relianceQuote);
    
    const fundamentals = await getFundamentals('TCS');
    console.log('TCS Fundamentals:', fundamentals);
    
    const marketAnalysis = await getMarketAnalysis();
    console.log('Market Analysis:', marketAnalysis);
}

main();
```

## 🏗️ Project Structure

```
backend3/
├── main.py              # Main FastAPI application
├── config.py            # Configuration settings
├── utils.py             # Utility functions and technical analysis
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── test_new_api.py     # Test script for new API structure
└── venv/               # Virtual environment
```

## 🔒 Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Stock symbol not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side errors

## 📊 Performance Optimization

- **Async Processing**: All endpoints are async for better concurrency
- **Intelligent Caching**: Reduces API calls to yfinance
- **Rate Limiting**: Prevents API abuse and ensures fair usage
- **Connection Pooling**: Efficient HTTP connection management
- **Flexible Parameters**: *args and **kwargs support for maximum flexibility

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This is a demo project for educational purposes. The data provided is from Yahoo Finance and may have delays. For real trading, always use official market data sources and consult with financial advisors.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the error messages
3. Check the server logs
4. Open an issue on GitHub

## 🔄 Updates

- **v2.0.0**: Updated API structure with *args and **kwargs support
- **v1.0.0**: Initial release with core features
- Support for major Indian stocks and indices
- Real-time data streaming via WebSocket
- Comprehensive technical analysis
- Market screening capabilities
- Fundamentals and financial analysis
- Holdings and ownership data
- Advanced search and sector analysis

