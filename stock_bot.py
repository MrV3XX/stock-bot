import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# List of stock tickers to analyze
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Example tickers

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y")
    
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    
    if 'Adj Close' not in df.columns:
        st.error(f"'Adj Close' column missing for {ticker}")
        return None
    
    df['Return'] = df['Adj Close'].pct_change()
    return df

def analyze_stock(ticker):
    df = get_stock_data(ticker)
    if df is None or df.empty:
        return None
    
    # Calculate average annual return and volatility
    avg_return = df['Return'].mean() * 252  # Approximate trading days per year
    volatility = df['Return'].std() * np.sqrt(252)
    
    # Try to get P/E ratio from info
    pe_ratio = None
    try:
        info = yf.Ticker(ticker).info
        pe_ratio = info.get('trailingPE', None)
    except Exception:
        pe_ratio = None
    
    return {
        'Ticker': ticker,
        'Avg Annual Return': avg_return,
        'Volatility': volatility,
        'P/E Ratio': pe_ratio
    }

def main():
    st.title("📈 Stock Market Trend Analyzer")
    st.write("Analyzing 5 years of data for selected stocks...")
    
    results = []
    for ticker in TICKERS:
        res = analyze_stock(ticker)
        if res is not None:
            results.append(res)
    
    if results:
        df_results = pd.DataFrame(results)
        st.dataframe(df_results)
    else:
        st.warning("No valid stock data found.")

if __name__ == "__main__":
    main()
