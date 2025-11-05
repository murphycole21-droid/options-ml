# pipeline/pull_options.py
import yfinance as yf
import pandas as pd
import yaml
from datetime import datetime
from pathlib import Path

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

        expiry = expiries[0]
        chain = tk.option_chain(expiry)
        calls = chain.calls.copy()
        puts = chain.puts.copy()

        # ADD TYPE
        calls['type'] = 'call'
        puts['type'] = 'put'

        # ADD UNDERLYING PRICE
        underlying_price = tk.info.get('regularMarketPrice') or tk.info.get('previousClose')
        calls['underlyingPrice'] = underlying_price
        puts['underlyingPrice'] = underlying_price

        # Add metadata
        for df in [calls, puts]:
            df['expiry'] = expiry
            df['ticker'] = ticker
            df['date'] = today

        full = pd.concat([calls, puts], ignore_index=True)
        path = raw_path / f"{ticker}_{today}.parquet"
        full.to_parquet(path, index=False)
        print(f" [OK] {len(full)} contracts")
    except Exception as e:
        print(f" [ERROR] {e}")

print("\nAll done! Data saved to data/raw/")