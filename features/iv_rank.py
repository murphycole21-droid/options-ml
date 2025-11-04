 # features/iv_rank.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def compute_iv_rank(ticker: str, lookback_days: int = 252) -> float:
    """
    Compute IV Rank over past year.
    Returns: percentile (0.0 to 1.0)
    """
    try:
        end = datetime.now()
        start = end - timedelta(days=lookback_days + 100)
        hist = yf.Ticker(ticker).history(start=start, end=end, interval="1d")
        if len(hist) < 200:
            return None
        # 20-day HV
        hv = hist['Close'].pct_change().rolling(20).std() * (252 ** 0.5)
        current_hv = hv.iloc[-1]
        past_hv = hv.dropna()
        if len(past_hv) == 0:
            return None
        rank = (past_hv <= current_hv).mean()  # % of time HV was lower
        return round(rank, 3)
    except:
        return None
