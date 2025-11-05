# features/screen_long.py
import pandas as pd
import glob
from pathlib import Path
import yaml
from features.iv_rank import compute_iv_rank
from datetime import datetime
import yfinance as yf

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Load all chains + add underlying price
def load_chains():
    files = glob.glob("data/raw/*_*.parquet")
    dfs = []
    for f in files:
        df = pd.read_parquet(f)
        ticker = Path(f).stem.split('_')[0]
        try:
            underlying_price = yf.Ticker(ticker).info.get('regularMarketPrice') or yf.Ticker(ticker).info.get('previousClose')
        except:
            underlying_price = None
        df['ticker'] = ticker
        df['underlyingPrice'] = underlying_price
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# Add DTE
def add_dte(df):
    df['expiry_date'] = pd.to_datetime(df['expiry'])
    df['dte'] = (df['expiry_date'] - datetime.now()).dt.days
    return df

# Screen: Top 1 call + 1 put per ticker
def screen_top_per_stock():
    df = load_chains()
    if df.empty or df['underlyingPrice'].isna().all():
        print("No data or underlying prices. Run pull_options.py first.")
        return pd.DataFrame()

    df = add_dte(df)
    filters = config['strategy']['long']['filters']
    df = df[df['volume'] > filters['volume_min']]
    df = df[df['dte'] <= filters['max_dte']]

    # OTM filter
    if filters['otm_only']:
        calls = df[df['type'] == 'call'].copy()
        puts = df[df['type'] == 'put'].copy()
        calls = calls[calls['strike'] > calls['underlyingPrice']]
        puts = puts[puts['strike'] < puts['underlyingPrice']]
        df = pd.concat([calls, puts])

    # Compute IV Rank per ticker
    iv_ranks = {}
    for ticker in df['ticker'].unique():
        iv_ranks[ticker] = compute_iv_rank(ticker)

    df['iv_rank'] = df['ticker'].map(iv_ranks)
    df = df.dropna(subset=['iv_rank', 'underlyingPrice'])
    df = df[df['iv_rank'] <= filters['iv_rank_max']]

    # STEP 1: Top 1 per [ticker, type]
    top_per_group = (
        df.groupby(['ticker', 'type'])
        .apply(lambda x: x.nsmallest(1, 'iv_rank'))
        .reset_index(drop=True)
    )

    # STEP 2: Top 5 calls + Top 5 puts
    top_calls = top_per_group[top_per_group['type'] == 'call'].nsmallest(5, 'iv_rank')
    top_puts = top_per_group[top_per_group['type'] == 'put'].nsmallest(5, 'iv_rank')

    # Combine and save
    top_picks = pd.concat([top_calls, top_puts]).sort_values(['type', 'iv_rank'])
    Path("backtest").mkdir(exist_ok=True)
    top_picks.to_csv("backtest/top_picks.csv", index=False)

    # Print
    print("\nTOP 5 LONG CALLS (IVR ≤ 30%)")
    print("-" * 70)
    for _, row in top_calls.iterrows():
        print(f"{row['ticker']:4} {row['expiry']} C ${row['strike']:6.2f} | "
              f"IVR: {row['iv_rank']:.1%} | Price: ${row['lastPrice']:.2f} | "
              f"DTE: {row['dte']:2} | Vol: {row['volume']:4}")

    print("\nTOP 5 LONG PUTS (IVR ≤ 30%)")
    print("-" * 70)
    for _, row in top_puts.iterrows():
        print(f"{row['ticker']:4} {row['expiry']} P ${row['strike']:6.2f} | "
              f"IVR: {row['iv_rank']:.1%} | Price: ${row['lastPrice']:.2f} | "
              f"DTE: {row['dte']:2} | Vol: {row['volume']:4}")

    print(f"\nSaved {len(top_picks)} picks to backtest/top_picks.csv")
    return top_picks

if __name__ == "__main__":
    screen_top_per_stock()