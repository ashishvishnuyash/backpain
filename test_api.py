#!/usr/bin/env python3
"""
Test script for Bloomberg Terminal-like Backend API
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_SYMBOLS = ["RELIANCE", "TCS", "HDFC", "INFY", "ICICI"]

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_get_symbols():
    """Test getting Indian stock symbols"""
    print("\n🔍 Testing Get Symbols...")
    try:
        response = requests.get(f"{BASE_URL}/symbols/indian-stocks")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get symbols passed")
            print(f"   Total stocks: {data['total_stocks']}")
            print(f"   Total indices: {data['total_indices']}")
            return True
        else:
            print(f"❌ Get symbols failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get symbols error: {str(e)}")
        return False

def test_stock_quote(symbol):
    """Test stock quote endpoint"""
    print(f"\n🔍 Testing Stock Quote for {symbol}...")
    try:
        response = requests.post(f"{BASE_URL}/stock/quote", 
                               json={"symbol": symbol})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stock quote for {symbol} passed")
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   Price: ₹{data.get('current_price', 'N/A')}")
            print(f"   Change: {data.get('change_percent', 'N/A')}%")
            return True
        else:
            print(f"❌ Stock quote for {symbol} failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stock quote error for {symbol}: {str(e)}")
        return False

def test_historical_data(symbol):
    """Test historical data endpoint"""
    print(f"\n🔍 Testing Historical Data for {symbol}...")
    try:
        response = requests.post(f"{BASE_URL}/stock/historical", 
                               json={"symbol": symbol, "period": "1mo"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical data for {symbol} passed")
            print(f"   Data points: {len(data['data'])}")
            print(f"   Period: {data['period']}")
            return True
        else:
            print(f"❌ Historical data for {symbol} failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Historical data error for {symbol}: {str(e)}")
        return False

def test_technical_indicators(symbol):
    """Test technical indicators endpoint"""
    print(f"\n🔍 Testing Technical Indicators for {symbol}...")
    try:
        response = requests.post(f"{BASE_URL}/stock/technical-indicators", 
                               json={"symbol": symbol, "period": "3mo"})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Technical indicators for {symbol} passed")
            print(f"   Indicators calculated: {len(data['indicators'])}")
            if data.get('current_signals'):
                print(f"   RSI: {data['current_signals'].get('rsi', 'N/A')}")
            return True
        else:
            print(f"❌ Technical indicators for {symbol} failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Technical indicators error for {symbol}: {str(e)}")
        return False

def test_stock_news(symbol):
    """Test stock news endpoint"""
    print(f"\n🔍 Testing Stock News for {symbol}...")
    try:
        response = requests.post(f"{BASE_URL}/stock/news", 
                               json={"symbol": symbol, "count": 5})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stock news for {symbol} passed")
            print(f"   News articles: {data.get('total_news', 0)}")
            return True
        else:
            print(f"❌ Stock news for {symbol} failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stock news error for {symbol}: {str(e)}")
        return False

def test_market_screener():
    """Test market screener endpoint"""
    print("\n🔍 Testing Market Screener...")
    try:
        response = requests.post(f"{BASE_URL}/market/screener", 
                               json={"pe_max": 30, "market_cap_min": 1000000000})
        if response.status_code == 200:
            data = response.json()
            print("✅ Market screener passed")
            print(f"   Matches found: {data.get('total_matches', 0)}")
            return True
        else:
            print(f"❌ Market screener failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market screener error: {str(e)}")
        return False

def test_portfolio_tracking():
    """Test portfolio tracking endpoint"""
    print("\n🔍 Testing Portfolio Tracking...")
    try:
        response = requests.post(f"{BASE_URL}/portfolio/track", 
                               json={"symbols": TEST_SYMBOLS[:3]})
        if response.status_code == 200:
            data = response.json()
            print("✅ Portfolio tracking passed")
            print(f"   Stocks tracked: {data.get('total_stocks', 0)}")
            print(f"   Total value: ₹{data.get('total_value', 0):,.2f}")
            return True
        else:
            print(f"❌ Portfolio tracking failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Portfolio tracking error: {str(e)}")
        return False

def test_market_indices():
    """Test market indices endpoint"""
    print("\n🔍 Testing Market Indices...")
    try:
        response = requests.get(f"{BASE_URL}/market/indices")
        if response.status_code == 200:
            data = response.json()
            print("✅ Market indices passed")
            print(f"   Indices available: {len(data.get('indices', {}))}")
            for index_name, index_data in data.get('indices', {}).items():
                print(f"   {index_name}: {index_data.get('value', 'N/A')} ({index_data.get('change_percent', 'N/A')}%)")
            return True
        else:
            print(f"❌ Market indices failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market indices error: {str(e)}")
        return False

def test_api_stats():
    """Test API stats endpoint"""
    print("\n🔍 Testing API Stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ API stats passed")
            print(f"   Cache size: {data.get('cache_size', 0)}")
            print(f"   Active WebSocket connections: {data.get('active_websocket_connections', 0)}")
            return True
        else:
            print(f"❌ API stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API stats error: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting Bloomberg Terminal-like Backend API Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Get Symbols", test_get_symbols),
        ("Market Indices", test_market_indices),
        ("Market Screener", test_market_screener),
        ("Portfolio Tracking", test_portfolio_tracking),
        ("API Stats", test_api_stats),
    ]
    
    # Add individual stock tests
    for symbol in TEST_SYMBOLS[:2]:  # Test first 2 symbols to avoid rate limiting
        tests.extend([
            (f"Stock Quote - {symbol}", lambda s=symbol: test_stock_quote(s)),
            (f"Historical Data - {symbol}", lambda s=symbol: test_historical_data(s)),
            (f"Technical Indicators - {symbol}", lambda s=symbol: test_technical_indicators(s)),
            (f"Stock News - {symbol}", lambda s=symbol: test_stock_news(s)),
        ])
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(0.5)  # Small delay to avoid rate limiting
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs.")
    
    return passed == total

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            run_all_tests()
        else:
            print("❌ Server is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please make sure the server is running on http://localhost:8000")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")


