#!/usr/bin/env python3
"""
Client example for Bloomberg Terminal-like Backend API
Demonstrates how to use various endpoints
"""

import requests
import json
import time
from datetime import datetime
import websocket
import threading

class BloombergTerminalClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_health(self):
        """Get API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Health check error: {e}")
            return None
    
    def get_symbols(self):
        """Get available Indian stock symbols"""
        try:
            response = self.session.get(f"{self.base_url}/symbols/indian-stocks")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Get symbols error: {e}")
            return None
    
    def get_stock_quote(self, symbol):
        """Get real-time stock quote"""
        try:
            response = self.session.post(f"{self.base_url}/stock/quote", 
                                       json={"symbol": symbol})
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Stock quote error for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, period="1y", interval="1d"):
        """Get historical stock data"""
        try:
            response = self.session.post(f"{self.base_url}/stock/historical", 
                                       json={"symbol": symbol, "period": period, "interval": interval})
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Historical data error for {symbol}: {e}")
            return None
    
    def get_technical_indicators(self, symbol, period="6mo"):
        """Get technical indicators"""
        try:
            response = self.session.post(f"{self.base_url}/stock/technical-indicators", 
                                       json={"symbol": symbol, "period": period})
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Technical indicators error for {symbol}: {e}")
            return None
    
    def get_stock_news(self, symbol, count=5):
        """Get stock news"""
        try:
            response = self.session.post(f"{self.base_url}/stock/news", 
                                       json={"symbol": symbol, "count": count})
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Stock news error for {symbol}: {e}")
            return None
    
    def screen_stocks(self, **filters):
        """Screen stocks based on criteria"""
        try:
            response = self.session.post(f"{self.base_url}/market/screener", json=filters)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Market screener error: {e}")
            return None
    
    def track_portfolio(self, symbols):
        """Track multiple stocks"""
        try:
            response = self.session.post(f"{self.base_url}/portfolio/track", 
                                       json={"symbols": symbols})
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Portfolio tracking error: {e}")
            return None
    
    def get_market_indices(self):
        """Get market indices"""
        try:
            response = self.session.get(f"{self.base_url}/market/indices")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Market indices error: {e}")
            return None
    
    def get_api_stats(self):
        """Get API statistics"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"API stats error: {e}")
            return None

class WebSocketClient:
    def __init__(self, ws_url="ws://localhost:8000/ws/real-time"):
        self.ws_url = ws_url
        self.ws = None
        self.connected = False
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            print(f"\n📊 Real-time Update ({data.get('timestamp', 'N/A')}):")
            
            if 'indices' in data:
                print("📈 Market Indices:")
                for index_name, index_data in data['indices'].items():
                    change_symbol = "📈" if index_data.get('change_percent', 0) >= 0 else "📉"
                    print(f"   {change_symbol} {index_name}: {index_data.get('value', 'N/A')} ({index_data.get('change_percent', 'N/A')}%)")
            
            if 'top_stocks' in data:
                print("🏢 Top Stocks:")
                for stock in data['top_stocks']:
                    change_symbol = "📈" if stock.get('change_percent', 0) >= 0 else "📉"
                    print(f"   {change_symbol} {stock.get('symbol', 'N/A')}: ₹{stock.get('price', 'N/A')} ({stock.get('change_percent', 'N/A')}%)")
                    
        except Exception as e:
            print(f"Error parsing WebSocket message: {e}")
    
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        self.connected = False
    
    def on_open(self, ws):
        print("WebSocket connected! Receiving real-time updates...")
        self.connected = True
    
    def connect(self):
        """Connect to WebSocket"""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run WebSocket in a separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
        except Exception as e:
            print(f"WebSocket connection error: {e}")
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
            self.connected = False

def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def main():
    """Main demonstration function"""
    print("🚀 Bloomberg Terminal-like Backend Client Example")
    print("=" * 60)
    
    # Initialize client
    client = BloombergTerminalClient()
    
    # Check API health
    print_separator("API Health Check")
    health = client.get_health()
    if health:
        print(f"✅ API Status: {health['status']}")
        print(f"⏰ Timestamp: {health['timestamp']}")
    else:
        print("❌ API is not responding")
        return
    
    # Get available symbols
    print_separator("Available Symbols")
    symbols = client.get_symbols()
    if symbols:
        print(f"📊 Total Stocks: {symbols['total_stocks']}")
        print(f"📈 Total Indices: {symbols['total_indices']}")
        print("\n🏢 Sample Stocks:")
        for i, (symbol, yf_symbol) in enumerate(list(symbols['stocks'].items())[:5]):
            print(f"   {i+1}. {symbol} -> {yf_symbol}")
    else:
        print("❌ Failed to get symbols")
    
    # Get market indices
    print_separator("Market Indices")
    indices = client.get_market_indices()
    if indices:
        for index_name, index_data in indices['indices'].items():
            change_symbol = "📈" if index_data.get('change_percent', 0) >= 0 else "📉"
            print(f"{change_symbol} {index_name}: {index_data.get('value', 'N/A')} ({index_data.get('change_percent', 'N/A')}%)")
    else:
        print("❌ Failed to get market indices")
    
    # Get stock quotes for top stocks
    print_separator("Stock Quotes")
    top_stocks = ["RELIANCE", "TCS", "HDFC", "INFY", "ICICI"]
    
    for symbol in top_stocks[:3]:  # Limit to 3 to avoid rate limiting
        quote = client.get_stock_quote(symbol)
        if quote:
            change_symbol = "📈" if quote.get('change_percent', 0) >= 0 else "📉"
            print(f"{change_symbol} {quote['name']} ({symbol})")
            print(f"   Price: ₹{quote.get('current_price', 'N/A')}")
            print(f"   Change: {quote.get('change', 'N/A')} ({quote.get('change_percent', 'N/A')}%)")
            print(f"   Volume: {quote.get('volume', 'N/A'):,}")
            print(f"   Market Cap: ₹{quote.get('market_cap', 'N/A'):,}" if quote.get('market_cap') else "   Market Cap: N/A")
            print()
        else:
            print(f"❌ Failed to get quote for {symbol}")
    
    # Get technical analysis for one stock
    print_separator("Technical Analysis")
    tech_data = client.get_technical_indicators("RELIANCE", "3mo")
    if tech_data and tech_data.get('current_signals'):
        signals = tech_data['current_signals']
        print(f"📊 RELIANCE Technical Signals:")
        print(f"   RSI: {signals.get('rsi', 'N/A')}")
        print(f"   MACD Signal: {signals.get('macd_signal', 'N/A')}")
        print(f"   Price vs SMA20: {signals.get('price_vs_sma20', 'N/A')}")
        print(f"   Price vs SMA50: {signals.get('price_vs_sma50', 'N/A')}")
    else:
        print("❌ Failed to get technical analysis")
    
    # Market screener
    print_separator("Market Screener")
    screener_results = client.screen_stocks(pe_max=25, market_cap_min=1000000000)
    if screener_results:
        print(f"🔍 Found {screener_results['total_matches']} stocks matching criteria:")
        for stock in screener_results['screener_results'][:5]:  # Show first 5
            print(f"   📊 {stock['name']} ({stock['symbol']})")
            print(f"      Price: ₹{stock.get('current_price', 'N/A')}")
            print(f"      P/E: {stock.get('pe_ratio', 'N/A')}")
            print(f"      Sector: {stock.get('sector', 'N/A')}")
            print()
    else:
        print("❌ Failed to get screener results")
    
    # Portfolio tracking
    print_separator("Portfolio Tracking")
    portfolio = client.track_portfolio(["RELIANCE", "TCS", "HDFC"])
    if portfolio:
        print(f"📈 Portfolio Summary:")
        print(f"   Total Stocks: {portfolio['total_stocks']}")
        print(f"   Total Value: ₹{portfolio['total_value']:,.2f}")
        print("\n   Individual Stocks:")
        for stock in portfolio['portfolio']:
            change_symbol = "📈" if stock.get('change_percent', 0) >= 0 else "📉"
            print(f"   {change_symbol} {stock['symbol']}: ₹{stock.get('current_price', 'N/A')} ({stock.get('change_percent', 'N/A')}%)")
    else:
        print("❌ Failed to track portfolio")
    
    # API Statistics
    print_separator("API Statistics")
    stats = client.get_api_stats()
    if stats:
        print(f"📊 Cache Size: {stats.get('cache_size', 0)}")
        print(f"🔗 Active WebSocket Connections: {stats.get('active_websocket_connections', 0)}")
        print(f"⏰ Uptime: {stats.get('uptime', 'N/A')}")
    else:
        print("❌ Failed to get API stats")
    
    # WebSocket Real-time Updates
    print_separator("Real-time Updates (WebSocket)")
    print("Connecting to WebSocket for real-time updates...")
    print("Press Ctrl+C to stop")
    
    ws_client = WebSocketClient()
    ws_client.connect()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping real-time updates...")
        ws_client.disconnect()
        print("✅ Disconnected from WebSocket")

if __name__ == "__main__":
    main()


