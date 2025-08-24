#!/usr/bin/env python3
"""
Test script for the updated Bloomberg Terminal-like Backend API
Testing the new *args and **kwargs parameter structure
"""

import requests
import json
import time

# Test the updated API structure with explicit parameters
def test_api():
    """Test the updated API structure with explicit parameters"""
    
    base_url = "http://localhost:8000"
    
    print("Testing Bloomberg Terminal-like Backend API")
    print("=" * 50)
    
    # Test basic endpoints
    print("\n1. Testing basic endpoints...")
    
    # Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Get Indian stocks
    try:
        response = requests.get(f"{base_url}/symbols/indian-stocks")
        print(f"Indian stocks: {response.status_code} - Found {len(response.json()['stocks'])} stocks")
    except Exception as e:
        print(f"Indian stocks failed: {e}")
    
    # Test stock quote
    print("\n2. Testing stock quote...")
    try:
        data = {"symbol": "RELIANCE"}
        response = requests.post(f"{base_url}/stock/quote", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Stock quote for RELIANCE: {result['current_price']} ({result['change_percent']:.2f}%)")
        else:
            print(f"Stock quote failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Stock quote error: {e}")
    
    # Test historical data
    print("\n3. Testing historical data...")
    try:
        data = {"symbol": "TCS", "period": "1mo", "interval": "1d"}
        response = requests.post(f"{base_url}/stock/historical", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Historical data for TCS: {len(result['data'])} days of data")
        else:
            print(f"Historical data failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Historical data error: {e}")
    
    # Test technical indicators
    print("\n4. Testing technical indicators...")
    try:
        data = {"symbol": "INFY", "period": "6mo", "interval": "1d"}
        response = requests.post(f"{base_url}/stock/technical-indicators", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Technical indicators for INFY: RSI={result['rsi'][-1]:.2f}, MACD={result['macd']['macd'][-1]:.2f}")
        else:
            print(f"Technical indicators failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Technical indicators error: {e}")
    
    # Test news
    print("\n5. Testing news...")
    try:
        data = {"symbol": "HDFC", "count": 5}
        response = requests.post(f"{base_url}/stock/news", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"News for HDFC: {len(result['news'])} articles found")
        else:
            print(f"News failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"News error: {e}")
    
    # Test market screener
    print("\n6. Testing market screener...")
    try:
        data = {"market_cap_min": 1000000000, "pe_max": 25, "sector": "Technology"}
        response = requests.post(f"{base_url}/market/screener", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Market screener: {len(result)} stocks found")
        else:
            print(f"Market screener failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Market screener error: {e}")
    
    # Test portfolio tracking
    print("\n7. Testing portfolio tracking...")
    try:
        data = {"symbols": ["RELIANCE", "TCS", "INFY", "HDFC"]}
        response = requests.post(f"{base_url}/portfolio/track", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Portfolio tracking: {result['total_stocks']} stocks, total value: {result['total_value']:.2f}")
        else:
            print(f"Portfolio tracking failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Portfolio tracking error: {e}")
    
    # Test fundamentals
    print("\n8. Testing fundamentals...")
    try:
        data = {"symbol": "RELIANCE"}
        response = requests.post(f"{base_url}/stock/fundamentals", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Fundamentals for RELIANCE: PE={result['valuation_metrics']['pe_ratio']}, Market Cap={result['valuation_metrics']['market_cap']}")
        else:
            print(f"Fundamentals failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Fundamentals error: {e}")
    
    # Test financials
    print("\n9. Testing financials...")
    try:
        data = {"symbol": "TCS", "period": "annual"}
        response = requests.post(f"{base_url}/stock/financials", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Financials for TCS: {len(result['income_statement'])} income statements")
        else:
            print(f"Financials failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Financials error: {e}")
    
    # Test holdings
    print("\n10. Testing holdings...")
    try:
        data = {"symbol": "INFY"}
        response = requests.post(f"{base_url}/stock/holdings", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Holdings for INFY: {len(result['major_holders'])} major holders")
        else:
            print(f"Holdings failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Holdings error: {e}")
    
    # Test market analysis
    print("\n11. Testing market analysis...")
    try:
        data = {"market": "NSE"}
        response = requests.post(f"{base_url}/market/analysis", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Market analysis: {len(result['indices'])} indices analyzed")
        else:
            print(f"Market analysis failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Market analysis error: {e}")
    
    # Test search stocks
    print("\n12. Testing search stocks...")
    try:
        data = {"query": "BANK", "limit": 5}
        response = requests.post(f"{base_url}/search/stocks", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Search stocks: {result['total_found']} stocks found for 'BANK'")
        else:
            print(f"Search stocks failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Search stocks error: {e}")
    
    # Test sector analysis
    print("\n13. Testing sector analysis...")
    try:
        data = {"sector": "Technology", "limit": 10}
        response = requests.post(f"{base_url}/sector/analysis", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Sector analysis: {len(result['stocks'])} stocks in Technology sector")
        else:
            print(f"Sector analysis failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Sector analysis error: {e}")
    
    # Test advanced screener
    print("\n14. Testing advanced screener...")
    try:
        data = {
            "market_cap_min": 5000000000,
            "pe_max": 30,
            "dividend_yield_min": 1.0,
            "sector": "Banking"
        }
        response = requests.post(f"{base_url}/screener/advanced", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Advanced screener: {len(result)} stocks found")
        else:
            print(f"Advanced screener failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Advanced screener error: {e}")
    
    # Test market indices
    print("\n15. Testing market indices...")
    try:
        response = requests.get(f"{base_url}/market/indices")
        if response.status_code == 200:
            result = response.json()
            print(f"Market indices: {len(result['indices'])} indices")
            for index_name, index_data in result['indices'].items():
                print(f"  {index_name}: {index_data['value']:.2f} ({index_data['change_percent']:.2f}%)")
        else:
            print(f"Market indices failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Market indices error: {e}")
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api()
