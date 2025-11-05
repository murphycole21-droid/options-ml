# features/trade_plan_generator.py
import pandas as pd
from pathlib import Path
import numpy as np
from scipy.stats import norm

# Black-Scholes price
def black_scholes_call_put(S, K, T, r, sigma, option_type):
    if T <= 0:
        return max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    else:
        return K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Greeks
def black_scholes_greeks(S, K, T, r, sigma, option_type):
    if T <= 0 or sigma <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    if option_type == 'call':
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r*T) * norm.cdf(d2)
        rho = K * T * np.exp(-r*T) * norm.cdf(d2) / 100
    else:
        delta = norm.cdf(d1) - 1
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r*T) * norm.cdf(-d2)
        rho = -K * T * np.exp(-r*T) * norm.cdf(-d2) / 100
    return {
        'delta': round(delta, 3),
        'gamma': round(gamma, 3),
        'theta': round(theta, 2),
        'vega': round(vega, 3),
        'rho': round(rho, 3)
    }

# P&L Scenarios
def pnl_scenarios(S0, K, premium, T_days, r, sigma, option_type):
    T = T_days / 365
    moves = [-0.05, -0.02, -0.01, 0, 0.01, 0.02, 0.05]
    labels = ["(–5%)", "(–2%)", "(–1%)", "(flat)", "(+1%)", "(+2%)", "(+5%)"]
    scenarios = []
    for move, label in zip(moves, labels):
        S = S0 * (1 + move)
        new_price = black_scholes_call_put(S, K, T, r, sigma, option_type)
        pnl = (new_price - premium) * 100
        scenarios.append(f"${S:.2f},0%,0%,${new_price:.2f},{pnl:+.0f}  {label}")
    return scenarios

# Generate trade plans
def generate_trade_plans():
    picks_path = Path("backtest/top_picks.csv")
    if not picks_path.exists():
        print("Run screen_long.py first to generate top_picks.csv")
        return

    df = pd.read_csv(picks_path)
    r = 0.0525  # 5.25%

    output = []
    for idx, row in df.iterrows():
        S = row['underlyingPrice']
        K = row['strike']
        T_days = row['dte']
        sigma = row['impliedVolatility']
        premium = row['lastPrice']
        option_type = row['type']

        greeks = black_scholes_greeks(S, K, T_days/365, r, sigma, option_type)
        scenarios = pnl_scenarios(S, K, premium, T_days, r, sigma, option_type)

        plan = f"""
================================================================================
TRADE PLAN #{idx+1}: {row['ticker']} {row['expiry']} {'C' if option_type=='call' else 'P'} ${K:.2f}
================================================================================
BUY 1 {row['ticker']} {row['expiry']} {'C' if option_type=='call' else 'P'} ${K:.2f} @ ${premium:.2f}
Entry: 10:00 AM ET
Stop Loss: ${premium*0.6:.2f} (–40%)
Take Profit: ${premium*2:.2f} (+100%)
Max Hold: {T_days} days

GREEKS:
  Delta: {greeks['delta']:+.3f} | Gamma: {greeks['gamma']:+.3f} | Theta: {greeks['theta']:+.2f}
  Vega: {greeks['vega']:+.3f} | Rho: {greeks['rho']:+.3f}

RISK: ${premium*100:.0f} | REWARD: ${premium*100:.0f}+

P&L Scenarios
Price,IV Change,Rate Change,Option Value,P&L
{scenarios[0]}
{scenarios[1]}
{scenarios[2]}
{scenarios[3]}
{scenarios[4]}
{scenarios[5]}
{scenarios[6]}
"""
        output.append(plan.strip())

    Path("backtest").mkdir(exist_ok=True)
    with open("backtest/trade_plans.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(output))

    print(f"\nGenerated {len(df)} trade plans → backtest/trade_plans.txt")

if __name__ == "__main__":
    generate_trade_plans()