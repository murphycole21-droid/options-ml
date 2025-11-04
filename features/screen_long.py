 # features/screen_long.py
import pandas as pd
import glob
from pathlib import Path
import yaml
from features.iv_rank import compute_iv_rank
from datetime import datetime

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Load all chains
def load_chains():
    files = glob.glob("data/raw/*_*.parquet")
    dfs = []
    for f in files:
        df = pd.read_parquet(f)
        ticker = Path(f).stem.split('_')[0]
        df['ticker'] = ticker
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# Add DTE
def add_dte(df):
    df['expiry_date'] = pd.to_datetime(df['expiry'])
    df['dte'] = (df['expiry_date'] - datetime.now()).dt.days
    return df

# Screen
def screen_long():
    df = load_chains()
    if df.empty:
        print("No data found. Run pull_options.py first.")
        return

    df = add_dte(df)
    df = df[df['volume'] > config['strategy']['long']['filters']['volume_min']]
    df = df[df['dte'] <= config['strategy']['long']['filters']['max_dte']]

    # OTM filter
    if config['strategy']['long']['filters']['otm_only']:
        calls = df[df['type'] == 'call']
        puts = df[df['type'] == 'put']
        calls = calls[calls['strike'] > calls['underlyingPrice']]
        puts = puts[puts['strike'] < puts['underlyingPrice']]
        df = pd.concat([calls, puts])

    # Compute IV Rank per ticker
    iv_ranks = {}
    for ticker in df['ticker'].unique():
        iv_ranks[ticker] = compute_iv_rank(ticker)

    df['iv_rank'] = df['ticker'].map(iv_ranks)
    df = df.dropna(subset=['iv_rank'])
    df = df[df['iv_rank'] <= config['strategy']['long']['filters']['iv_rank_max']]

    # Rank
    df = df.sort_values('iv_rank')

    # Top 5 calls
    top_calls = df[df['type'] == 'call'].head(5)
    top_puts = df[df['type'] == 'put'].head(5)

    print("\nTOP 5 LONG CALLS (IVR ≤ 30%)")
    print("-" * 60)
    for _, row in top_calls.iterrows():
        print(f"{row['ticker']} {row['expiry']} C ${row['strike']:.2f} | "
              f"IVR: {row['iv_rank']:.1%} | Price: ${row['lastPrice']:.2f} | "
              f"DTE: {row['dte']} | Vol: {row['volume']}")

    print("\nTOP 5 LONG PUTS (IVR ≤ 30%)")
    print("-" * 60)
    for _, row in top_puts.iterrows():
        print(f"{row['ticker']} {row['expiry']} P ${row['strike']:.2f} | "
              f"IVR: {row['iv_rank']:.1%} | Price: ${row['lastPrice']:.2f} | "
              f"DTE: {row['dte']} | Vol: {row['volume']}")

    # Save
    top_calls.to_csv("backtest/top_calls.csv", index=False)
    top_puts.to_csv("backtest/top_puts.csv", index=False)
    print("\nSaved to backtest/top_calls.csv and top_puts.csv")

if __name__ == "__main__":
    screen_long()