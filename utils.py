import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import yfinance as yf
from datetime import datetime, timedelta
import logging
from config import TECHNICAL_INDICATORS, INDIAN_STOCKS, INDIAN_INDICES

logger = logging.getLogger(__name__)

def normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to yfinance format"""
    symbol_upper = symbol.upper()
    
    if symbol_upper in INDIAN_STOCKS:
        return INDIAN_STOCKS[symbol_upper]
    elif symbol_upper in INDIAN_INDICES:
        return INDIAN_INDICES[symbol_upper]
    else:
        return symbol

def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average"""
    return prices.rolling(window=period).mean()

def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    return prices.ewm(span=period).mean()

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands"""
    middle_band = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    return upper_band, middle_band, lower_band

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Calculate Stochastic Oscillator"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=d_period).mean()
    return k_percent, d_percent

def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Williams %R"""
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
    return williams_r

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

def calculate_volume_indicators(volume: pd.Series, close: pd.Series) -> Dict[str, pd.Series]:
    """Calculate volume-based indicators"""
    # Volume SMA
    volume_sma = volume.rolling(window=20).mean()
    
    # On-Balance Volume (OBV)
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    # Volume Price Trend (VPT)
    vpt = pd.Series(index=close.index, dtype=float)
    vpt.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        price_change = (close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1]
        vpt.iloc[i] = vpt.iloc[i-1] + (volume.iloc[i] * price_change)
    
    return {
        "volume_sma": volume_sma,
        "obv": obv,
        "vpt": vpt
    }

def get_support_resistance_levels(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> Dict[str, List[float]]:
    """Calculate support and resistance levels using pivot points"""
    support_levels = []
    resistance_levels = []
    
    for i in range(window, len(close) - window):
        # Check for support level
        if all(low.iloc[i] <= low.iloc[j] for j in range(i-window, i+window+1)):
            support_levels.append(low.iloc[i])
        
        # Check for resistance level
        if all(high.iloc[i] >= high.iloc[j] for j in range(i-window, i+window+1)):
            resistance_levels.append(high.iloc[i])
    
    return {
        "support": sorted(list(set(support_levels))),
        "resistance": sorted(list(set(resistance_levels)))
    }

def calculate_fibonacci_retracements(high: float, low: float) -> Dict[str, float]:
    """Calculate Fibonacci retracement levels"""
    diff = high - low
    return {
        "0.0": low,
        "0.236": low + 0.236 * diff,
        "0.382": low + 0.382 * diff,
        "0.5": low + 0.5 * diff,
        "0.618": low + 0.618 * diff,
        "0.786": low + 0.786 * diff,
        "1.0": high
    }

def get_trading_signals(indicators: Dict[str, Any]) -> Dict[str, str]:
    """Generate trading signals based on technical indicators"""
    signals = {}
    
    # RSI signals
    if indicators.get('rsi'):
        rsi = indicators['rsi']
        if rsi > 70:
            signals['rsi'] = "overbought"
        elif rsi < 30:
            signals['rsi'] = "oversold"
        else:
            signals['rsi'] = "neutral"
    
    # MACD signals
    if indicators.get('macd') and indicators.get('macd_signal'):
        macd = indicators['macd']
        signal = indicators['macd_signal']
        if macd > signal:
            signals['macd'] = "bullish"
        else:
            signals['macd'] = "bearish"
    
    # Moving average signals
    if indicators.get('close') and indicators.get('sma_20'):
        close = indicators['close']
        sma_20 = indicators['sma_20']
        if close > sma_20:
            signals['price_vs_sma20'] = "above"
        else:
            signals['price_vs_sma20'] = "below"
    
    # Bollinger Bands signals
    if indicators.get('close') and indicators.get('bb_upper') and indicators.get('bb_lower'):
        close = indicators['close']
        bb_upper = indicators['bb_upper']
        bb_lower = indicators['bb_lower']
        
        if close > bb_upper:
            signals['bollinger'] = "above_upper"
        elif close < bb_lower:
            signals['bollinger'] = "below_lower"
        else:
            signals['bollinger'] = "within_bands"
    
    return signals

def calculate_risk_metrics(returns: pd.Series) -> Dict[str, float]:
    """Calculate risk metrics for a stock"""
    if len(returns) < 2:
        return {}
    
    # Basic statistics
    mean_return = returns.mean()
    std_return = returns.std()
    
    # Sharpe Ratio (assuming risk-free rate of 0.05)
    risk_free_rate = 0.05
    sharpe_ratio = (mean_return - risk_free_rate) / std_return if std_return != 0 else 0
    
    # Maximum Drawdown
    cumulative_returns = (1 + returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Value at Risk (95% confidence)
    var_95 = returns.quantile(0.05)
    
    # Skewness and Kurtosis
    skewness = returns.skew()
    kurtosis = returns.kurtosis()
    
    return {
        "mean_return": float(mean_return),
        "std_return": float(std_return),
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": float(max_drawdown),
        "var_95": float(var_95),
        "skewness": float(skewness),
        "kurtosis": float(kurtosis)
    }

def format_currency(amount: float, currency: str = "INR") -> str:
    """Format currency values"""
    if currency == "INR":
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f}Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f}L"
        else:
            return f"₹{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format percentage values"""
    return f"{value:.2f}%"

def is_market_open() -> bool:
    """Check if Indian market is currently open"""
    now = datetime.now()
    
    # Check if it's a weekday
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check market hours (9:15 AM to 3:30 PM IST)
    market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_start <= now <= market_end

def get_market_status() -> Dict[str, Any]:
    """Get current market status"""
    is_open = is_market_open()
    now = datetime.now()
    
    if is_open:
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        time_remaining = market_end - now
        status = "open"
    else:
        # Calculate next market open
        if now.weekday() >= 5:  # Weekend
            days_ahead = 7 - now.weekday()
            next_market = now + timedelta(days=days_ahead)
        else:
            if now.hour >= 15 and now.minute >= 30:  # After market close
                next_market = now + timedelta(days=1)
            else:  # Before market open
                next_market = now
        
        next_market = next_market.replace(hour=9, minute=15, second=0, microsecond=0)
        time_remaining = next_market - now
        status = "closed"
    
    return {
        "status": status,
        "is_open": is_open,
        "current_time": now.isoformat(),
        "time_remaining": str(time_remaining),
        "next_session": next_market.isoformat() if not is_open else None
    }

def validate_symbol(symbol: str) -> bool:
    """Validate if a symbol is supported"""
    symbol_upper = symbol.upper()
    return (symbol_upper in INDIAN_STOCKS or 
            symbol_upper in INDIAN_INDICES or 
            symbol.endswith('.NS') or 
            symbol.startswith('^'))

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get comprehensive stock information"""
    try:
        normalized_symbol = normalize_symbol(symbol)
        ticker = yf.Ticker(normalized_symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get('longName', info.get('shortName', 'Unknown')),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('trailingPE'),
            "pb_ratio": info.get('priceToBook'),
            "dividend_yield": info.get('dividendYield'),
            "beta": info.get('beta'),
            "fifty_two_week_high": info.get('fiftyTwoWeekHigh'),
            "fifty_two_week_low": info.get('fiftyTwoWeekLow'),
            "volume_avg": info.get('averageVolume'),
            "shares_outstanding": info.get('sharesOutstanding'),
            "float_shares": info.get('floatShares'),
            "insider_ownership": info.get('heldPercentInsiders'),
            "institutional_ownership": info.get('heldPercentInstitutions')
        }
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {str(e)}")
        return {}


