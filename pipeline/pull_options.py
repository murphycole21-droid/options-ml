# pipeline/pull_options.py
import yfinance as yf
import pandas as pd
import yaml
from datetime import datetime
from pathlib import Path

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

universe = config["universe"]
raw_path = Path(config["paths"]["raw"])
raw_path.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y%m%d")

print(f"Pulling option chains for {len(universe)} tickers on {today}...\n")

for ticker in universe:
    print(f"→ {ticker}", end="")
    try:
        tk = yf.Ticker(ticker)
        expiries = tk.options
        if not expiries:
            print(" [NO OPTIONS]")
            continue

        # Use nearest expiry
        expiry = expiries[0]
        chain = tk.option_chain(expiry)
        calls = chain.calls.assign(type="call", expiry=expiry, ticker=ticker, date=today)
        puts = chain.puts.assign(type="put", expiry=expiry, ticker=ticker, date=today)
        full = pd.concat([calls, puts], ignore_index=True)

        path = raw_path / f"{ticker}_{today}.parquet"
        full.to_parquet(path)
        print(f" [OK] {len(full)} contracts")
    except Exception as e:
        print(f" [ERROR] {e}")

print("\nAll done! Data saved to data/raw/")