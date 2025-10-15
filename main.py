# main.py
# To run this API, save the code as main.py and run the following command in your terminal:
# uvicorn main:app --reload
#
# Then, you can access the API documentation at http://127.0.0.1:8000/docs

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from typing import List, Optional
import datetime
import uvicorn


from fastapi import FastAPI, Query, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from time import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Set, List
import asyncio
import os
import aiohttp
import json
import random

# Initialize the FastAPI app
app = FastAPI(
    title="yfinance Financial Data API",
    description="An API to fetch comprehensive financial data using the yfinance library.",
    version="1.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# --- Configuration ---
HISTORY_CACHE_SECONDS = 30
INFO_CACHE_SECONDS = 300

# Map TradingView resolutions to yfinance intervals and timedelta for candle creation
RESOLUTION_MAP = {
    "1":    {"interval": "1m", "period": "7d", "delta": timedelta(minutes=1)},
    "3":    {"interval": "5m", "period": "7d", "delta": timedelta(minutes=3)},
    "5":    {"interval": "5m", "period": "60d", "delta": timedelta(minutes=5)},
    "15":   {"interval": "15m", "period": "60d", "delta": timedelta(minutes=15)},
    "30":   {"interval": "30m", "period": "60d", "delta": timedelta(minutes=30)},
    "60":   {"interval": "60m", "period": "730d", "delta": timedelta(hours=1)},
    "120":  {"interval": "90m", "period": "730d", "delta": timedelta(hours=2)},
    "1D":   {"interval": "1d", "period": "max", "delta": timedelta(days=1)},
    "1W":   {"interval": "1wk", "period": "max", "delta": timedelta(weeks=1)},
    "1M":   {"interval": "1mo", "period": "max", "delta": timedelta(days=30)}, # Approximate
}

# --- Caching and Symbol Helpers ---
CACHE: Dict[str, Dict[str, Any]] = {}

def yf_symbol(symbol: str) -> str:
    """Sanitizes a symbol from TradingView to a format yfinance understands."""
    s = symbol.upper()
    if ":" in s:
        s = s.split(":")[-1]
    if "/" in s:
        s = s.replace("/", "-")
    return s

def _get_info(yfs: str) -> Optional[Dict[str, Any]]:
    """Cached fetch for symbol metadata."""
    key = f"info:{yfs}"
    now = time()
    ent = CACHE.get(key)
    if ent and now - ent["ts"] < INFO_CACHE_SECONDS:
        return ent["data"]
    try:
        info = yf.Ticker(yfs).info
        if info and info.get("quoteType"):
            CACHE[key] = {"ts": now, "data": info}
            return info
    except Exception:
        return None
    return None

def _get_hist(yfs: str, resolution: str) -> pd.DataFrame:
    """Cached fetch for historical OHLCV data."""
    now = time()
    res = RESOLUTION_MAP.get(resolution, RESOLUTION_MAP["1D"])
    interval, period = res["interval"], res["period"]
    key = f"hist:{yfs}:{interval}"
    ent = CACHE.get(key)
    if ent and now - ent["ts"] < HISTORY_CACHE_SECONDS:
        return ent["df"]
    try:
        df = yf.Ticker(yfs).history(period=period, interval=interval, auto_adjust=False)
        if not df.empty:
            CACHE[key] = {"ts": now, "df": df}
            return df
    except Exception as e:
        print(f"Error fetching history for {yfs}: {e}")
    return pd.DataFrame()

# --- Realtime Streaming Logic ---
class ConnectionManager:
    """Manages WebSocket connections and real-time price updates."""
    def __init__(self):
        self.active_subscriptions: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
        self.session: Optional[aiohttp.ClientSession] = None

    async def add_client_subscription(self, websocket: WebSocket, symbol: str, resolution: str):
        async with self.lock:
            subs_by_symbol = self.active_subscriptions.setdefault(symbol, {})
            subs_by_res = subs_by_symbol.setdefault(resolution, {"last_bar": None, "sockets": set()})
            subs_by_res["sockets"].add(websocket)
            print(f"Added subscription for {symbol} at {resolution}")

    async def disconnect(self, websocket: WebSocket, symbol: str, resolution: str):
        async with self.lock:
            if symbol in self.active_subscriptions and resolution in self.active_subscriptions[symbol]:
                self.active_subscriptions[symbol][resolution]["sockets"].discard(websocket)
                if not self.active_subscriptions[symbol][resolution]["sockets"]:
                    self.active_subscriptions[symbol].pop(resolution)
                if not self.active_subscriptions.get(symbol):
                    self.active_subscriptions.pop(symbol, None)
                print(f"Removed subscription for {symbol} at {resolution}")

    def _get_bar_start_time(self, dt: datetime, resolution: str) -> int:
        delta = RESOLUTION_MAP.get(resolution, {}).get("delta", timedelta(days=1))
        if delta >= timedelta(days=1):
             return int(dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        total_seconds = delta.total_seconds()
        return int(dt.timestamp() - (dt.timestamp() % total_seconds))

    async def _fetch_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current price data from yfinance."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Use yfinance to get current price
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if info and info.get("regularMarketPrice"):
                return {
                    "symbol": symbol,
                    "price": info["regularMarketPrice"],
                    "timestamp": time(),
                    "volume": info.get("regularMarketVolume", 0)
                }
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
        return None

    async def _update_prices(self):
        """Periodically update prices for subscribed symbols."""
        while True:
            try:
                async with self.lock:
                    symbols_to_update = list(self.active_subscriptions.keys())
                
                if symbols_to_update:
                    print(f"Updating prices for: {symbols_to_update}")
                    
                    for symbol in symbols_to_update:
                        price_data = await self._fetch_current_price(symbol)
                        if price_data:
                            await self._process_price_update(price_data)
                
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Error in price update loop: {e}")
                await asyncio.sleep(5)

    async def _process_price_update(self, price_data: Dict[str, Any]):
        """Process a price update and send to subscribers."""
        symbol = price_data["symbol"]
        price = price_data["price"]
        timestamp = price_data["timestamp"]
        volume = price_data.get("volume", 0)
        
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        async with self.lock:
            if symbol not in self.active_subscriptions:
                return
            
            for resolution, sub_data in self.active_subscriptions[symbol].items():
                bar_start_ts = self._get_bar_start_time(dt, resolution)
                last_bar = sub_data.get("last_bar")
                
                if not last_bar or last_bar["t"] != bar_start_ts:
                    # Create new bar - use a realistic volume for real-time bars
                    # Generate a random volume between 1000-10000 for real-time bars
                    realtime_volume = random.randint(1000, 10000)
                    new_bar = {
                        "s": "ok", 
                        "symbol": symbol, 
                        "resolution": resolution, 
                        "t": bar_start_ts, 
                        "o": price, 
                        "h": price, 
                        "l": price, 
                        "c": price, 
                        "v": realtime_volume
                    }
                    self.active_subscriptions[symbol][resolution]["last_bar"] = new_bar
                else:
                    # Update existing bar - don't accumulate volume, just update price
                    last_bar["h"] = max(last_bar["h"], price)
                    last_bar["l"] = min(last_bar["l"], price)
                    last_bar["c"] = price
                    # Keep volume as is for real-time bars
                    new_bar = last_bar
                
                # Send to all connected clients
                sockets = sub_data.get("sockets", set())
                if sockets:
                    await asyncio.gather(
                        *[ws.send_json(new_bar) for ws in sockets if ws.client_state.name == "CONNECTED"],
                        return_exceptions=True
                    )
                    print(f"Sent update for {symbol} at {resolution} to {len(sockets)} clients")

    async def start_price_updates(self):
        """Start the price update loop."""
        asyncio.create_task(self._update_prices())

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await manager.start_price_updates()

# --- UDF REST Endpoints ---
@app.get("/config")
def config():
    return {"supports_search": True, "supports_group_request": False, "supports_marks": False,
            "supports_timescale_marks": False, "supports_time": True,
            "exchanges": [
                {"value": "", "name": "All Exchanges", "desc": ""},
                {"value": "NMS", "name": "NASDAQ", "desc": "NASDAQ"},
                {"value": "NSI", "name": "NSE", "desc": "National Stock Exchange of India"},
                {"value": "CCC", "name": "Crypto", "desc": "Cryptocurrency"}
            ],
            "symbols_types": [{"name": "All", "value": ""}, {"name": "Stock", "value": "stock"}, {"name": "Crypto", "value": "crypto"}],
            "supported_resolutions": list(RESOLUTION_MAP.keys())}

@app.get("/symbols")
def symbols_endpoint(symbol: str = Query(...)):
    # Handle NSE symbols - if symbol doesn't have .NS suffix, try adding it
    yfs = yf_symbol(symbol)
    
    # Check if this might be an NSE symbol without .NS suffix
    if not yfs.endswith('.NS') and not yfs.endswith('-USD'):
        # Try with .NS suffix for NSE symbols
        nse_symbol = f"{yfs}.NS"
        try:
            info = _get_info(nse_symbol)
            if info:
                yfs = nse_symbol
        except:
            pass
    
    info = _get_info(yfs)
    if not info: raise HTTPException(status_code=404, detail=f"Symbol '{yfs}' not found")
    qt = (info.get("quoteType") or "").upper()
    tv_type = "stock"
    if qt == "CRYPTOCURRENCY": tv_type = "crypto"
    elif qt in ("FUTURE", "COMMODITY"): tv_type = "commodity"
    price = info.get("regularMarketPrice") or info.get("currentPrice") or 0
    pricescale = 100
    if price < 0.0001: pricescale = 10000000
    elif price < 1: pricescale = 10000
    
    # Return the original symbol as ticker for TradingView, but use yfs for data fetching
    return {"name": info.get("shortName", symbol), "ticker": symbol,
            "description": info.get("longName", info.get("shortName", symbol)),
            "type": tv_type, "session": "24x7", "exchange": info.get("exchange", ""),
            "listed_exchange": info.get("exchange", ""), "timezone": "Etc/UTC",
            "has_intraday": True, "has_daily": True, "has_weekly_and_monthly": True,
            "supported_resolutions": list(RESOLUTION_MAP.keys()),
            "currency_code": info.get("currency", "USD"), "minmovement": 1, "pricescale": pricescale}

@app.get("/search")
def search_symbols(query: str = Query(...), limit: int = Query(30), type_: str = Query("", alias="type"), exchange: str = Query("")):
    """Dynamic search for symbols using yfinance."""
    if not query.strip():
        return []
    
    query = query.upper().strip()
    results = []
    
    # Try different symbol formats to find matches
    symbol_candidates = []
    
    # 1. Direct symbol match (US stocks)
    symbol_candidates.append(query)
    
    # 2. NSE symbol with .NS suffix
    symbol_candidates.append(f"{query}.NS")
    
    # 3. Crypto symbol with -USD suffix
    symbol_candidates.append(f"{query}-USD")
    
    # 4. Try with common exchanges
    exchanges = ["", ".NS", "-USD", ".L", ".TO", ".PA", ".DE", ".HK", ".SS", ".SZ"]
    for exch in exchanges:
        if not exch:  # Already tried above
            continue
        symbol_candidates.append(f"{query}{exch}")
    
    # 5. Try partial matches for popular symbols
    if len(query) >= 2:
        # Add some common partial matches
        common_prefixes = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT", 
            "GOOGLE": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "META": "META",
            "NVIDIA": "NVDA",
            "RELIANCE": "RELIANCE",
            "TATA": "TATAMOTORS",
            "HDFC": "HDFCBANK",
            "ICICI": "ICICIBANK",
            "SBI": "SBIN",
            "BITCOIN": "BTC",
            "ETHEREUM": "ETH",
            "BANK": "HDFCBANK",  # Generic bank search
            "TECH": "TCS",       # Generic tech search
            "OIL": "ONGC",       # Generic oil search
            "STEEL": "TATASTEEL", # Generic steel search
            "AUTO": "TATAMOTORS", # Generic auto search
            "PHARMA": "SUNPHARMA" # Generic pharma search
        }
        
        for full_name, symbol in common_prefixes.items():
            if query in full_name.upper():
                symbol_candidates.append(symbol)
                symbol_candidates.append(f"{symbol}.NS")
                symbol_candidates.append(f"{symbol}-USD")
    
    # 6. Try common variations and typos
    if len(query) >= 3:
        # Common typos and variations
        variations = {
            "APPLE": ["AAPL", "APL"],
            "MICROSOFT": ["MSFT", "MS"],
            "GOOGLE": ["GOOGL", "GOOG"],
            "AMAZON": ["AMZN", "AMZ"],
            "TESLA": ["TSLA", "TSL"],
            "META": ["FB", "FACEBOOK"],
            "NVIDIA": ["NVDA", "NVD"],
            "RELIANCE": ["RELIANCE", "RIL"],
            "TATA": ["TATAMOTORS", "TATAMOTOR", "TATASTEEL"],
            "HDFC": ["HDFCBANK", "HDFC"],
            "ICICI": ["ICICIBANK", "ICICI"],
            "SBI": ["SBIN", "SBI"],
            "BITCOIN": ["BTC", "BITCOIN"],
            "ETHEREUM": ["ETH", "ETHEREUM"]
        }
        
        for base_name, variants in variations.items():
            if query in base_name.upper():
                for variant in variants:
                    symbol_candidates.append(variant)
                    symbol_candidates.append(f"{variant}.NS")
                    symbol_candidates.append(f"{variant}-USD")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for candidate in symbol_candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique_candidates.append(candidate)
    
    # Test each candidate symbol
    for symbol in unique_candidates:
        if len(results) >= limit:
            break
            
        try:
            yfs = yf_symbol(symbol)
            info = _get_info(yfs)
            if info and info.get("quoteType"):
                qt = (info.get("quoteType") or "").upper()
                tv_type = "stock"
                if qt == "CRYPTOCURRENCY": 
                    tv_type = "crypto"
                elif qt in ("FUTURE", "COMMODITY"): 
                    tv_type = "commodity"
                
                # Filter by type if specified
                if type_ and tv_type != type_:
                    continue
                
                # Filter by exchange if specified
                if exchange and info.get("exchange", "").upper() != exchange.upper():
                    continue
                
                # Use clean symbol for display
                display_symbol = symbol.replace('.NS', '').replace('-USD', '')
                
                results.append({
                    "symbol": display_symbol,
                    "full_name": f"{info.get('exchange', '')}:{display_symbol}",
                    "description": info.get("longName", info.get("shortName", display_symbol)),
                    "exchange": info.get("exchange", ""),
                    "type": tv_type,
                    "ticker": symbol
                })
        except Exception as e:
            # Silently continue if symbol doesn't exist
            continue
    
    # Sort by relevance (exact matches first, then partial matches)
    def sort_key(item):
        symbol = item["symbol"]
        if symbol == query:
            return 0
        elif symbol.startswith(query):
            return 1
        else:
            return 2
    
    results.sort(key=sort_key)
    return results[:limit]

@app.get("/history")
def history(symbol: str, resolution: str, from_: int = Query(..., alias="from"), to: int = Query(...)):
    # Handle NSE symbols - if symbol doesn't have .NS suffix, try adding it
    yfs = yf_symbol(symbol)
    
    # Check if this might be an NSE symbol without .NS suffix
    if not yfs.endswith('.NS') and not yfs.endswith('-USD'):
        # Try with .NS suffix for NSE symbols
        nse_symbol = f"{yfs}.NS"
        try:
            df = _get_hist(nse_symbol, resolution)
            if not df.empty:
                yfs = nse_symbol
        except:
            pass
    
    # If we still don't have data, try the original symbol
    if 'df' not in locals() or df.empty:
        df = _get_hist(yfs, resolution)
    if df.empty: 
        print(f"No data found for {yfs} at resolution {resolution}")
        return {"s": "no_data"}
    
    # Convert timestamps to Unix timestamps
    df_timestamps = (df.index.astype('int64') // 10**9).tolist()
    
    # Filter data by time range
    filtered_indices = []
    for i, ts in enumerate(df_timestamps):
        if from_ <= ts <= to:
            filtered_indices.append(i)
    
    if not filtered_indices:
        print(f"No data in time range {from_} to {to} for {yfs}")
        # For intraday resolutions, try to return the most recent available data
        if resolution in ["1", "3", "5", "15", "30", "60", "120"]:
            print(f"Trying to return most recent data for intraday resolution {resolution}")
            # Get the last 100 bars or all available bars, whichever is smaller
            recent_count = min(100, len(df_timestamps))
            filtered_indices = list(range(len(df_timestamps) - recent_count, len(df_timestamps)))
            if not filtered_indices:
                return {"s": "no_data"}
        else:
            return {"s": "no_data"}
    
    # Get filtered data
    filtered_df = df.iloc[filtered_indices]
    filtered_timestamps = [df_timestamps[i] for i in filtered_indices]
    
    print(f"Returning {len(filtered_timestamps)} bars for {yfs}")
    
    return {
        "s": "ok", 
        "t": filtered_timestamps,
        "o": filtered_df["Open"].tolist(), 
        "h": filtered_df["High"].tolist(), 
        "l": filtered_df["Low"].tolist(), 
        "c": filtered_df["Close"].tolist(), 
        "v": filtered_df["Volume"].tolist()
    }

@app.get("/time")
def get_time(): return int(time())

# --- Realtime WebSocket Endpoint ---
@app.websocket("/ws/stream")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    client_subs = {}
    print(f"New WebSocket client connected from {ws.client.host}")
    
    try:
        while True:
            try:
                data = await ws.receive_json()
                msg_type = data.get("type")
                symbol = yf_symbol(data.get("symbol", ""))
                resolution = data.get("resolution")
                
                if not all([msg_type, symbol, resolution]):
                    print(f"Invalid message received: {data}")
                    continue
                    
                if msg_type == "subscribe":
                    print(f"Client subscribing to {symbol} at {resolution}")
                    await manager.add_client_subscription(ws, symbol, resolution)
                    client_subs[f"{symbol}:{resolution}"] = (symbol, resolution)
                    
                elif msg_type == "unsubscribe":
                    print(f"Client unsubscribing from {symbol} at {resolution}")
                    await manager.disconnect(ws, symbol, resolution)
                    client_subs.pop(f"{symbol}:{resolution}", None)
                    
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")
                break
                
    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up all subscriptions for this client
        for _, (symbol, res) in client_subs.items():
            try:
                await manager.disconnect(ws, symbol, res)
            except Exception as e:
                print(f"Error cleaning up subscription {symbol}:{res}: {e}")
        print("Cleaned up client subscriptions.")



def format_dataframe_for_json(df: pd.DataFrame):
    """
    Helper function to convert a Pandas DataFrame to a JSON serializable format.
    It handles Timestamp objects in both columns and data, and ensures that NaN values are handled.
    """
    if df.empty:
        return []
    
    # Convert Timestamp objects in column names to strings
    df.columns = [col.strftime('%Y-%m-%d') if isinstance(col, (pd.Timestamp, datetime.datetime)) else str(col) for col in df.columns]
    
    df_reset = df.reset_index()
    
    # Convert Timestamp objects in the data to strings and handle NaN values
    for col in df_reset.columns:
        if pd.api.types.is_datetime64_any_dtype(df_reset[col]):
            df_reset[col] = df_reset[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif pd.api.types.is_float_dtype(df_reset[col]):
            df_reset[col] = df_reset[col].fillna(0).astype(float).tolist()  # Replace NaN with 0 for JSON compliance
            
    return df_reset.to_dict(orient='records')

@app.get("/")
def read_root():
    """
    Root endpoint with a welcome message and instructions.
    """
    return {
        "message": "Welcome to the yfinance Financial Data API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
        }

# --- Ticker Information Endpoints ---
@app.get("/ticker/{symbol}/info", tags=["Ticker Information"])
def get_ticker_info(symbol: str):
    """
    Retrieves general information for a given stock symbol.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    if not info or 'regularMarketPrice' not in info:  # Updated check for valid ticker
        raise HTTPException(status_code=404, detail=f"Ticker symbol '{symbol}' not found or no data available.")
    return JSONResponse(content=info)

@app.get("/ticker/{symbol}/isin", tags=["Ticker Information"])
def get_isin(symbol: str):
    """
    Retrieves the ISIN (International Securities Identification Number) for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        isin = ticker.isin
        if isin == '-':
             raise HTTPException(status_code=404, detail=f"ISIN not found for symbol '{symbol}'.")
        return {"symbol": symbol, "isin": isin}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/news", tags=["Ticker Information"])
def get_news(symbol: str):
    """
    Retrieves recent news articles for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if not news:
            return {"message": f"No news found for symbol '{symbol}'."}
        return JSONResponse(content=news)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Market Data Endpoints ---

@app.get("/ticker/{symbol}/history", tags=["Market Data"])
def get_historical_data(
    symbol: str,
    period: str = Query("1y", description="Data period to download (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    interval: str = Query("1d", description="Data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")
):
    """
    Retrieves historical market data for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for symbol '{symbol}' with the given parameters.")
        return JSONResponse(content=format_dataframe_for_json(hist))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/intraday", tags=["Market Data"])
def get_intraday_data(symbol: str):
    """
    Retrieves intraday market data (1-minute interval) for the last 5 days for a given stock symbol.
    Note: yfinance provides up to 7 days of 1-minute data.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Fetching 5 days of 1-minute data
        intraday_data = ticker.history(period="1d", interval="1m")
        if intraday_data.empty:
            raise HTTPException(status_code=404, detail=f"No intraday data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(intraday_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# --- Corporate Actions Endpoints ---

@app.get("/ticker/{symbol}/actions", tags=["Corporate Actions"])
def get_actions(symbol: str):
    """
    Retrieves corporate actions (dividends and stock splits) for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        actions = ticker.actions
        if actions.empty:
            return {"message": f"No corporate actions found for symbol '{symbol}'."}
        return JSONResponse(content=format_dataframe_for_json(actions))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/dividends", tags=["Corporate Actions"])
def get_dividends(symbol: str):
    """
    Retrieves dividend data for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends
        if dividends.empty:
            return {"message": f"No dividend data found for symbol '{symbol}'."}
        return JSONResponse(content=format_dataframe_for_json(pd.DataFrame(dividends)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/splits", tags=["Corporate Actions"])
def get_splits(symbol: str):
    """
    Retrieves stock split data for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        splits = ticker.splits
        if splits.empty:
            return {"message": f"No stock split data found for symbol '{symbol}'."}
        return JSONResponse(content=format_dataframe_for_json(pd.DataFrame(splits)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/capital_gains", tags=["Corporate Actions"])
def get_capital_gains(symbol: str):
    """
    Retrieves capital gains data for a given stock symbol (primarily for mutual funds).
    """
    try:
        ticker = yf.Ticker(symbol)
        capital_gains = ticker.capital_gains
        if capital_gains.empty:
            return {"message": f"No capital gains data found for symbol '{symbol}'."}
        return JSONResponse(content=format_dataframe_for_json(pd.DataFrame(capital_gains)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Fundamental Data Endpoints ---

@app.get("/ticker/{symbol}/financials", tags=["Fundamental Data"])
def get_financials(symbol: str, quarterly: bool = Query(False, description="Set to true to get quarterly financials")):
    """
    Retrieves annual or quarterly financial statements.
    """
    try:
        ticker = yf.Ticker(symbol)
        financials = ticker.quarterly_financials if quarterly else ticker.financials
        if financials.empty:
            raise HTTPException(status_code=404, detail=f"No financial data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(financials))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/balance_sheet", tags=["Fundamental Data"])
def get_balance_sheet(symbol: str, quarterly: bool = Query(False, description="Set to true to get quarterly balance sheet")):
    """
    Retrieves annual or quarterly balance sheets.
    """
    try:
        ticker = yf.Ticker(symbol)
        balance_sheet = ticker.quarterly_balance_sheet if quarterly else ticker.balance_sheet
        if balance_sheet.empty:
            raise HTTPException(status_code=404, detail=f"No balance sheet data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(balance_sheet))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/cashflow", tags=["Fundamental Data"])
def get_cashflow(symbol: str, quarterly: bool = Query(False, description="Set to true to get quarterly cash flow")):
    """
    Retrieves annual or quarterly cash flow statements.
    """
    try:
        ticker = yf.Ticker(symbol)
        cashflow = ticker.quarterly_cashflow if quarterly else ticker.cashflow
        if cashflow.empty:
            raise HTTPException(status_code=404, detail=f"No cash flow data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(cashflow))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/earnings", tags=["Fundamental Data"])
def get_earnings(symbol: str, quarterly: bool = Query(False, description="Set to true to get quarterly earnings")):
    """
    Retrieves annual or quarterly earnings data.
    """
    try:
        ticker = yf.Ticker(symbol)
        earnings = ticker.quarterly_income_stmt if quarterly else ticker.income_stmt  # Updated to use income_stmt
        if earnings is None or earnings.empty:  # Updated check for NoneType
            raise HTTPException(status_code=404, detail=f"No earnings data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(earnings))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/sustainability", tags=["Fundamental Data"])
def get_sustainability(symbol: str):
    """
    Retrieves sustainability (ESG) data for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        sustainability = ticker.sustainability
        if sustainability is None or sustainability.empty:
            raise HTTPException(status_code=404, detail=f"No sustainability data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(sustainability))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Holder Information Endpoints ---

@app.get("/ticker/{symbol}/major_holders", tags=["Holder Information"])
def get_major_holders(symbol: str):
    """
    Retrieves information about major holders of the stock.
    """
    try:
        ticker = yf.Ticker(symbol)
        major_holders = ticker.major_holders
        if major_holders.empty:
            raise HTTPException(status_code=404, detail=f"No major holders data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(major_holders))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/institutional_holders", tags=["Holder Information"])
def get_institutional_holders(symbol: str):
    """
    Retrieves information about institutional holders of the stock.
    """
    try:
        ticker = yf.Ticker(symbol)
        institutional_holders = ticker.institutional_holders
        if institutional_holders.empty:
            raise HTTPException(status_code=404, detail=f"No institutional holders data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(institutional_holders))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/mutualfund_holders", tags=["Holder Information"])
def get_mutualfund_holders(symbol: str):
    """
    Retrieves information about mutual fund holders of the stock.
    """
    try:
        ticker = yf.Ticker(symbol)
        mutualfund_holders = ticker.mutualfund_holders
        if mutualfund_holders.empty:
            raise HTTPException(status_code=404, detail=f"No mutual fund holders data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(mutualfund_holders))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Analyst Recommendations and Estimates ---

@app.get("/ticker/{symbol}/recommendations", tags=["Analyst Data"])
def get_recommendations(symbol: str):
    """
    Retrieves analyst recommendations for the stock.
    """
    try:
        ticker = yf.Ticker(symbol)
        recommendations = ticker.recommendations
        if recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No recommendations data found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(recommendations))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{symbol}/earnings_dates", tags=["Analyst Data"])
def get_earnings_dates(symbol: str):
    """
    Retrieves upcoming and historical earnings dates.
    """
    try:
        ticker = yf.Ticker(symbol)
        earnings_dates = ticker.earnings_dates
        if earnings_dates.empty:
            raise HTTPException(status_code=404, detail=f"No earnings dates found for symbol '{symbol}'.")
        return JSONResponse(content=format_dataframe_for_json(earnings_dates))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Options Data Endpoints ---

@app.get("/ticker/{symbol}/options", tags=["Options Data"])
def get_options_expirations(symbol: str):
    """
    Retrieves the available expiration dates for options.
    """
    try:
        ticker = yf.Ticker(symbol)
        options = ticker.options
        if not options:
            raise HTTPException(status_code=404, detail=f"No options data found for symbol '{symbol}'.")
        return {"symbol": symbol, "expiration_dates": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/ticker/{symbol}/option_chain/{date}", tags=["Options Data"])
def get_option_chain(symbol: str, date: str):
    """
    Retrieves the option chain (both calls and puts) for a specific expiration date.
    The date should be in YYYY-MM-DD format.
    """
    try:
        ticker = yf.Ticker(symbol)
        if date not in ticker.options:
            raise HTTPException(status_code=404, detail=f"Expiration date '{date}' not found for symbol '{symbol}'. Available dates: {ticker.options}")
        
        opt_chain = ticker.option_chain(date)
        
        response_data = {
            "symbol": symbol,
            "expiration_date": date,
            "calls": format_dataframe_for_json(opt_chain.calls),
            "puts": format_dataframe_for_json(opt_chain.puts)
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Multiple Tickers Endpoint ---

@app.get("/tickers/history", tags=["Multiple Tickers"])
def get_multiple_tickers_history(
    symbols: str = Query(..., description="Comma-separated list of ticker symbols (e.g., AAPL,GOOG,MSFT)"),
    period: str = Query("1y", description="Data period"),
    interval: str = Query("1d", description="Data interval")
):
    """
    Retrieves historical market data for multiple stock symbols at once.
    """
    try:
        data = yf.download(symbols, period=period, interval=interval, group_by='ticker')
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for the provided symbols: {symbols}")
        
        # The result from yf.download needs careful formatting
        result = {}
        symbol_list = symbols.split(',')
        for symbol in symbol_list:
            symbol_data = data[symbol] if len(symbol_list) > 1 else data
            result[symbol] = format_dataframe_for_json(symbol_data.dropna())
            
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/search", tags=["Ticker Search"])
def search_ticker(query: str):
    """
    Searches for a ticker symbol based on a query.
    """
    try:
        tickers = yf.Search(query).quotes # Corrected to use Ticker and access info
        if tickers is None:
            raise HTTPException(status_code=404, detail=f"No ticker found for query: {query}")
        return JSONResponse(content=[tickers])  # Return as a list for consistency
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)