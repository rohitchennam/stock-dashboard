# app/data.py
import yfinance as yf
import pandas as pd
import numpy as np
import os

# Top Indian stocks (NSE symbols with .NS suffix for yfinance)
COMPANIES = {
    "INFY": "Infosys",
    "TCS": "Tata Consultancy Services",
    "RELIANCE": "Reliance Industries",
    "HDFCBANK": "HDFC Bank",
    "WIPRO": "Wipro",
    "ICICIBANK": "ICICI Bank",
    "HINDUNILVR": "Hindustan Unilever",
    "SBIN": "State Bank of India",
    "BAJFINANCE": "Bajaj Finance",
    "MARUTI": "Maruti Suzuki",
}


DATA_DIR = "data"


def get_yf_symbol(symbol: str) -> str:
    return f"{symbol}.NS"


def fetch_and_save(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Fetch stock data from yfinance, clean it, add metrics, and cache as CSV."""
    ticker = yf.Ticker(get_yf_symbol(symbol))
    df = ticker.history(period=period)

    if df.empty:
        raise ValueError(f"No data found for symbol: {symbol}")

    # --- Clean ---
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)  # remove timezone
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Date"}, inplace=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # --- Calculated Metrics ---
    df["Daily_Return"] = ((df["Close"] - df["Open"]) / df["Open"] * 100).round(4)
    df["MA_7"] = df["Close"].rolling(window=7).mean().round(2)
    df["52W_High"] = df["Close"].rolling(window=252, min_periods=1).max().round(2)
    df["52W_Low"] = df["Close"].rolling(window=252, min_periods=1).min().round(2)

    # --- Custom Metric: Volatility Score (std of last 7 daily returns) ---
    df["Volatility_7D"] = df["Daily_Return"].rolling(window=7).std().round(4)

    # Cache to CSV
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(f"{DATA_DIR}/{symbol}.csv", index=False)

    return df


def load_data(symbol: str) -> pd.DataFrame:
    """Load from cache if available, else fetch fresh."""
    path = f"{DATA_DIR}/{symbol}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        df = fetch_and_save(symbol)
    return df


def get_last_n_days(symbol: str, days: int = 30) -> pd.DataFrame:
    df = load_data(symbol)
    return df.tail(days)


def get_summary(symbol: str) -> dict:
    df = load_data(symbol)
    return {
        "symbol": symbol,
        "name": COMPANIES.get(symbol, symbol),
        "52w_high": float(df["Close"].max()),
        "52w_low": float(df["Close"].min()),
        "avg_close": round(float(df["Close"].mean()), 2),
        "latest_close": float(df["Close"].iloc[-1]),
        "latest_return": float(df["Daily_Return"].iloc[-1]),
        "volatility_7d": float(df["Volatility_7D"].iloc[-1])
    }


def compare_stocks(symbol1: str, symbol2: str) -> dict:
    df1 = load_data(symbol1)[["Date", "Close"]].tail(90).rename(columns={"Close": symbol1})
    df2 = load_data(symbol2)[["Date", "Close"]].tail(90).rename(columns={"Close": symbol2})
    merged = pd.merge(df1, df2, on="Date")

    # Normalize to 100 for fair comparison
    merged[f"{symbol1}_norm"] = (merged[symbol1] / merged[symbol1].iloc[0] * 100).round(2)
    merged[f"{symbol2}_norm"] = (merged[symbol2] / merged[symbol2].iloc[0] * 100).round(2)

    # Correlation
    correlation = round(merged[symbol1].corr(merged[symbol2]), 4)

    return {
        "correlation": correlation,
        "data": merged[["Date", f"{symbol1}_norm", f"{symbol2}_norm"]].to_dict(orient="records")
    }


def preload_all():
    """Pre-fetch and cache data for all companies on startup."""
    print("Preloading stock data...")
    for symbol in COMPANIES:
        try:
            fetch_and_save(symbol)
            print(f"  ✅ {symbol}")
        except Exception as e:
            print(f"  ❌ {symbol}: {e}")
    print("Preload complete.")