import os
from typing import Dict, List

# API Configuration
API_TITLE = "Bloomberg Terminal-like Backend"
API_VERSION = "1.0.0"
API_DESCRIPTION = "A comprehensive financial data API for Indian markets using yfinance"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# Rate Limiting Configuration
DEFAULT_RATE_LIMIT = 100
DEFAULT_RATE_WINDOW = 60  # seconds

# Cache Configuration
DEFAULT_CACHE_TTL = 300  # 5 minutes
QUOTE_CACHE_TTL = 60     # 1 minute
NEWS_CACHE_TTL = 600     # 10 minutes
SCREENER_CACHE_TTL = 900 # 15 minutes

# Indian Market Configuration
INDIAN_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS", 
    "HDFC": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICI": "ICICIBANK.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "WIPRO": "WIPRO.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "TECHM": "TECHM.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "POWERGRID": "POWERGRID.NS",
    "HCLTECH": "HCLTECH.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "ADANIENT": "ADANIENT.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "ONGC": "ONGC.NS",
    "COALINDIA": "COALINDIA.NS"
}

INDIAN_INDICES = {
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTYBANK": "^NSEBANK",
    "NIFTYIT": "^CNXIT",
    "NIFTYPHARMA": "^CNXPHARMA",
    "NIFTYAUTO": "^CNXAUTO",
    "NIFTYFMCG": "^CNXFMCG",
    "NIFTYREALTY": "^CNXREALTY",
    "NIFTYENERGY": "^CNXENERGY",
    "NIFTYMETAL": "^CNXMETAL"
}

# Sector Classification
SECTOR_MAPPING = {
    "BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS"],
    "OIL_GAS": ["RELIANCE.NS", "ONGC.NS"],
    "AUTOMOBILES": ["MARUTI.NS", "TATAMOTORS.NS"],
    "PHARMACEUTICALS": ["SUNPHARMA.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "TATACONSUM.NS"],
    "TELECOM": ["BHARTIARTL.NS"],
    "CEMENT": ["ULTRACEMCO.NS"],
    "POWER": ["POWERGRID.NS"],
    "STEEL": ["JSWSTEEL.NS"],
    "FINANCE": ["BAJFINANCE.NS", "BAJAJFINSV.NS"],
    "CONGLOMERATE": ["ADANIENT.NS"],
    "MINING": ["COALINDIA.NS"]
}

# Technical Analysis Configuration
TECHNICAL_INDICATORS = {
    "SMA_PERIODS": [20, 50, 200],
    "RSI_PERIOD": 14,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BOLLINGER_PERIOD": 20,
    "BOLLINGER_STD": 2
}

# WebSocket Configuration
WEBSOCKET_UPDATE_INTERVAL = 30  # seconds
WEBSOCKET_MAX_CONNECTIONS = 100

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Error Messages
ERROR_MESSAGES = {
    "STOCK_NOT_FOUND": "Stock symbol not found",
    "NO_DATA": "No data available for the requested symbol",
    "RATE_LIMIT": "Rate limit exceeded. Please try again later.",
    "INVALID_SYMBOL": "Invalid stock symbol provided",
    "API_ERROR": "Error fetching data from external API",
    "CACHE_ERROR": "Error accessing cached data"
}

# Success Messages
SUCCESS_MESSAGES = {
    "DATA_FETCHED": "Data fetched successfully",
    "CACHE_UPDATED": "Cache updated successfully",
    "WEBSOCKET_CONNECTED": "WebSocket connected successfully"
}

# Market Hours (IST)
MARKET_HOURS = {
    "PRE_MARKET": "09:00",
    "MARKET_OPEN": "09:15",
    "MARKET_CLOSE": "15:30",
    "POST_MARKET": "15:45"
}

# Default Parameters
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
DEFAULT_NEWS_COUNT = 10


