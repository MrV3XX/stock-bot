import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

TICKERS = ['AAPL', 'MSFT', 'JNJ', 'KO', 'PG', 'PEP', 'XOM', 'V', 'MA', 'HD', 'NVDA']
YEARS = 5
VOLATILITY_THRESHOLD = 25
MIN_CAGR = 5
PE_RANGE = (10, 30)

def get_stock_data(ticker, years=YEARS):
    end = datetime.today()
    start = end - timedelta(days=365 * years)
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        return None
    df['Return'] = df['Adj Close'].pct_change()
    df['Cumulative'] = (1 + df['Return']).cumprod()
    return df

def get_cagr(df):
    n = len(df) / 252
    cagr = (df['Cumulative'].iloc[-1])**(1/n) - 1
    return round(cagr * 100, 2)

def get_volatility(df):
    return round(df['Return'].std() * np.sqrt(252) * 100, 2)

def get_max_drawdown(df):
    cum_max = df['Cumulative'].cummax()
    drawdown = (df['Cumulative'] - cum_max) / cum_max
    return round(drawdown.min() * 100, 2)

def get_pe_ratio(ticker):
    stock = yf.Ticker(ticker)
    pe = stock.info.get('trailingPE', None)
    return round(pe, 2) if pe else None

def analyze_stock(ticker):
    df = get_stock_data(ticker)
    if df is None:
        return {'Ticker': ticker, 'Error': 'No Data'}
    cagr = get_cagr(df)
    vol = get_volatility(df)
    mdd = get_max_drawdown(df)
    pe = get_pe_ratio(ticker)
    return {
        'Ticker': ticker,
        'CAGR (%)': cagr,
        'Volatility (%)': vol,
        'Max Drawdown (%)': mdd,
        'P/E Ratio': pe
    }

def main():
    st.title("📈 Stock Market Trend Analyzer")
    st.write(f"Analyzing {YEARS} years of data for selected stocks...")

    results = [analyze_stock(ticker) for ticker in TICKERS]
    df_results = pd.DataFrame(results)

    st.subheader("Full Results")
    st.dataframe(df_results)

    filtered = df_results[
        (df_results['Volatility (%)'] <= VOLATILITY_THRESHOLD) &
        (df_results['CAGR (%)'] >= MIN_CAGR) &
        (df_results['P/E Ratio'] >= PE_RANGE[0]) &
        (df_results['P/E Ratio'] <= PE_RANGE[1])
    ].sort_values(by='CAGR (%)', ascending=False)

    st.subheader("Filtered (Steady Performers)")
    st.dataframe(filtered)

    st.download_button("Download CSV", df_results.to_csv(index=False), file_name="stock_analysis.csv")

if __name__ == '__main__':
    main()
