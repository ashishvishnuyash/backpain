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

# Initialize the FastAPI app
app = FastAPI(
    title="yfinance Financial Data API",
    description="An API to fetch comprehensive financial data using the yfinance library.",
    version="1.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:9002", "http://127.0.0.1:3000", "http://127.0.0.1:9002"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS
    allow_headers=["*"],  # Allow all headers
)

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