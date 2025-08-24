# Bloomberg Terminal-like Backend API

A comprehensive financial data API for Indian markets built with FastAPI and yfinance, providing real-time stock data, technical analysis, and market insights.

## 🚀 Features

- **Real-time Stock Data**: Live quotes, historical data, and technical indicators
- **Fundamental Analysis**: Valuation metrics, financial ratios, and balance sheet data
- **Financial Statements**: Income statements, balance sheets, and cash flow data
- **Holdings Analysis**: Institutional and insider ownership information
- **Market Analysis**: Sector performance, market breadth, and index tracking
- **Stock Search & Lookup**: Search stocks by name or symbol
- **Advanced Screener**: Multi-criteria stock screening with 20+ filters
- **Portfolio Tracking**: Track multiple stocks and calculate portfolio metrics
- **News & Sentiment**: Latest news and sentiment analysis
- **WebSocket Support**: Real-time data streaming
- **Rate Limiting**: Built-in request throttling for API protection
- **Caching**: Intelligent caching for improved performance
- **Indian Market Focus**: Optimized for Indian stock markets (NSE/BSE)

## 📋 Requirements

- Python 3.8+
- FastAPI
- yfinance
- pandas
- numpy
- uvicorn

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend3
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Core Endpoints

#### 1. Stock Quote
```http
POST /stock/quote
```
**Parameters:**
- `symbol` (string, required): Stock symbol (e.g., "RELIANCE", "TCS")

**Example:**
```json
{
  "symbol": "RELIANCE"
}
```

#### 2. Historical Data
```http
POST /stock/historical
```
**Parameters:**
- `symbol` (string, required): Stock symbol
- `period` (string, optional): Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
- `interval` (string, optional): Data interval ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")

**Example:**
```json
{
  "symbol": "TCS",
  "period": "1mo",
  "interval": "1d"
}
```

#### 3. Technical Indicators
```http
POST /stock/technical-indicators
```
**Parameters:**
- `symbol` (string, required): Stock symbol
- `period` (string, optional): Time period (default: "6mo")
- `interval` (string, optional): Data interval (default: "1d")

**Returns:** SMA, EMA, RSI, MACD, Bollinger Bands

#### 4. Stock News
```http
POST /stock/news
```
**Parameters:**
- `symbol` (string, required): Stock symbol
- `count` (integer, optional): Number of news articles (default: 10)

### Analysis Endpoints

#### 5. Fundamentals Analysis
```http
POST /stock/fundamentals
```
**Parameters:**
- `symbol` (string, required): Stock symbol

**Returns:** Valuation metrics, financial ratios, balance sheet data, trading info

#### 6. Financial Statements
```http
POST /stock/financials
```
**Parameters:**
- `symbol` (string, required): Stock symbol
- `period` (string, optional): "annual" or "quarterly" (default: "annual")

**Returns:** Income statement, balance sheet, cash flow

#### 7. Holdings Analysis
```http
POST /stock/holdings
```
**Parameters:**
- `symbol` (string, required): Stock symbol

**Returns:** Ownership summary, major holders, institutional holders

### Market Endpoints

#### 8. Market Analysis
```http
POST /market/analysis
```
**Parameters:**
- `market` (string, optional): Market identifier (default: "NSE")

**Returns:** Market indices, sector performance, market breadth

#### 9. Market Screener
```http
POST /market/screener
```
**Parameters:**
- `market_cap_min` (float, optional): Minimum market cap
- `market_cap_max` (float, optional): Maximum market cap
- `pe_min` (float, optional): Minimum P/E ratio
- `pe_max` (float, optional): Maximum P/E ratio
- `volume_min` (integer, optional): Minimum volume
- `sector` (string, optional): Sector filter

#### 10. Advanced Screener
```http
POST /screener/advanced
```
**Parameters:**
- `market_cap_min/max` (float, optional): Market cap range
- `pe_min/max` (float, optional): P/E ratio range
- `pb_min/max` (float, optional): P/B ratio range
- `dividend_yield_min/max` (float, optional): Dividend yield range
- `volume_min` (integer, optional): Minimum volume
- `price_min/max` (float, optional): Price range
- `sector` (string, optional): Sector filter
- `industry` (string, optional): Industry filter
- `beta_min/max` (float, optional): Beta range
- `debt_to_equity_max` (float, optional): Maximum debt-to-equity
- `current_ratio_min` (float, optional): Minimum current ratio
- `return_on_equity_min` (float, optional): Minimum ROE
- `profit_margin_min` (float, optional): Minimum profit margin

### Search & Lookup

#### 11. Search Stocks
```http
POST /search/stocks
```
**Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Maximum results (default: 10)

#### 12. Sector Analysis
```http
POST /sector/analysis
```
**Parameters:**
- `sector` (string, required): Sector name
- `limit` (integer, optional): Maximum stocks (default: 20)

### Portfolio & Tracking

#### 13. Portfolio Tracking
```http
POST /portfolio/track
```
**Parameters:**
- `symbols` (array, required): List of stock symbols

**Example:**
```json
{
  "symbols": ["RELIANCE", "TCS", "INFY", "HDFC"]
}
```

### Information Endpoints

#### 14. Market Indices
```http
GET /market/indices
```
**Returns:** Major Indian market indices (NIFTY50, SENSEX, etc.)

#### 15. Indian Stocks List
```http
GET /symbols/indian-stocks
```
**Returns:** Available Indian stock symbols and indices

#### 16. Health Check
```http
GET /health
```
**Returns:** API health status

## 🏛️ Supported Indian Stocks

The API supports major Indian stocks including:
- **RELIANCE** (Reliance Industries)
- **TCS** (Tata Consultancy Services)
- **HDFC** (HDFC Bank)
- **INFY** (Infosys)
- **ICICI** (ICICI Bank)
- **HINDUNILVR** (Hindustan Unilever)
- **ITC** (ITC Limited)
- **SBIN** (State Bank of India)
- **BHARTIARTL** (Bharti Airtel)
- **KOTAKBANK** (Kotak Mahindra Bank)
- **AXISBANK** (Axis Bank)
- **ASIANPAINT** (Asian Paints)
- **MARUTI** (Maruti Suzuki)
- **SUNPHARMA** (Sun Pharmaceutical)
- **TATAMOTORS** (Tata Motors)
- **WIPRO** (Wipro)
- **ULTRACEMCO** (UltraTech Cement)
- **TECHM** (Tech Mahindra)
- **NESTLEIND** (Nestle India)
- **POWERGRID** (Power Grid Corporation)

## 📊 Supported Indices

- **NIFTY50** (^NSEI)
- **SENSEX** (^BSESN)
- **NIFTYBANK** (^NSEBANK)
- **NIFTYIT** (^CNXIT)
- **NIFTYPHARMA** (^CNXPHARMA)

## ⚡ Performance Features

### Rate Limiting
- **Stock Quote**: 200 requests per minute
- **Historical Data**: 100 requests per minute
- **Technical Indicators**: 50 requests per minute
- **News**: 100 requests per minute
- **Market Screener**: 20 requests per minute
- **Fundamentals**: 50 requests per minute
- **Financials**: 30 requests per minute
- **Holdings**: 30 requests per minute
- **Market Analysis**: 50 requests per minute
- **Search**: 100 requests per minute
- **Sector Analysis**: 30 requests per minute
- **Advanced Screener**: 20 requests per minute

### Caching
- **Stock Quote**: 1 minute cache
- **Historical Data**: 5 minutes cache
- **Technical Indicators**: 5 minutes cache
- **News**: 10 minutes cache
- **Market Screener**: 15 minutes cache
- **Fundamentals**: 10 minutes cache
- **Financials**: 30 minutes cache
- **Holdings**: 30 minutes cache
- **Market Analysis**: 5 minutes cache
- **Search**: 10 minutes cache
- **Sector Analysis**: 15 minutes cache
- **Advanced Screener**: 15 minutes cache

## 🔧 Configuration

The API can be configured through environment variables:

```bash
# Server configuration
HOST=0.0.0.0
PORT=8000

# Rate limiting
DEFAULT_RATE_LIMIT=100
DEFAULT_RATE_WINDOW=60

# Caching
DEFAULT_CACHE_TTL=300
```

## 🧪 Testing

Run the test script to verify API functionality:

```bash
python test_new_api.py
```

## 📈 Usage Examples

### Python Client Example

```python
import requests

# Get stock quote
response = requests.post("http://localhost:8000/stock/quote", 
                        json={"symbol": "RELIANCE"})
data = response.json()
print(f"RELIANCE: ₹{data['current_price']} ({data['change_percent']:.2f}%)")

# Get historical data
response = requests.post("http://localhost:8000/stock/historical",
                        json={"symbol": "TCS", "period": "1mo"})
data = response.json()
print(f"TCS historical data: {len(data['data'])} points")

# Advanced screener
response = requests.post("http://localhost:8000/screener/advanced",
                        json={
                            "market_cap_min": 1000000000,
                            "pe_max": 25,
                            "sector": "Technology"
                        })
data = response.json()
print(f"Found {len(data)} stocks matching criteria")
```

### cURL Examples

```bash
# Get stock quote
curl -X POST "http://localhost:8000/stock/quote" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "RELIANCE"}'

# Get technical indicators
curl -X POST "http://localhost:8000/stock/technical-indicators" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "INFY", "period": "6mo"}'

# Search stocks
curl -X POST "http://localhost:8000/search/stocks" \
     -H "Content-Type: application/json" \
     -d '{"query": "BANK", "limit": 5}'
```

## 🌐 WebSocket Support

For real-time data streaming:

```python
import websockets
import json

async def connect_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"symbol": "RELIANCE"}))
        while True:
            data = await websocket.recv()
            print(f"Real-time data: {data}")
```

## 🔒 Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (missing parameters)
- **404**: Not Found (symbol not found)
- **429**: Rate Limit Exceeded
- **500**: Internal Server Error

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the test examples in `test_new_api.py`

---

**Note**: This API uses yfinance for data retrieval. Please ensure compliance with Yahoo Finance's terms of service and implement appropriate rate limiting for production use.

