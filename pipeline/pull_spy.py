 # pipeline/pull_spy.py
import yfinance as yf
import pandas as pd
from datetime import datetime

print("Pulling SPY option chain...")

ticker = "SPY"
tk = yf.Ticker(ticker)
expiries = tk.options
if not expiries:
    print("No options available (market closed?)")
    exit()

expiry = expiries[0]
print(f"Using expiry: {expiry}")

chain = tk.option_chain(expiry)
calls = chain.calls.assign(type="call", expiry=expiry, ticker=ticker)
puts = chain.puts.assign(type="put", expiry=expiry, ticker=ticker)
full = pd.concat([calls, puts])

today = datetime.now().strftime("%Y%m%d")
path = f"data/raw/SPY_{today}.parquet"
full.to_parquet(path)

print(f"Saved {len(full)} contracts → {path}")
