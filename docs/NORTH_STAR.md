\# NORTH STAR: Long-Only Options ML Engine



\## Vision

Build a \*\*self-improving, data-driven system\*\* that identifies \*\*high-conviction long call and long put opportunities\*\* using a \*\*progressive stack of quantitative models\*\*, starting simple and evolving into a \*\*hybrid statistical + deep learning pipeline\*\*.



We \*\*never\*\* trade spreads, calendars, or short options.

We \*\*only\*\* go long calls or long puts.



---



\## Success = \*\*Consistent Positive Expectancy\*\*

| Metric | Target |

|-------|--------|

| \*\*Profit Factor\*\* | ≥ 1.6 |

| \*\*Sharpe Ratio (daily)\*\* | ≥ 1.2 |

| \*\*Win Rate\*\* | ≥ \*\*65 %\*\* |

| \*\*Max Drawdown\*\* | ≤ \*\*15 %\*\* ← \*\*TIGHTENED\*\* |

| \*\*Edge over IV Rank Rule\*\* | ≥ +25 % cumulative return |



\*Measured over rolling 6-month windows in paper + live trading\*



---



\## Core Principles

1\. \*\*Start Simple, Add Complexity Only When Validated\*\*

2\. \*\*Every Model Must Beat the Prior Baseline\*\*

3\. \*\*Time-Series Aware: No Look-Ahead Bias\*\*

4\. \*\*Moderate Risk: Growth with Guardrails\*\*

   - \*\*Max Position Size\*\* ≤ \*\*3 %\*\* per trade ← \*\*MODERATE\*\*

   - \*\*Max Total Exposure\*\* ≤ \*\*6 %\*\* (2 positions)

   - \*\*Daily CVaR\*\* < \*\*3 %\*\*

   - \*\*Hard Stop-Loss\*\* at \*\*40 %\*\* of premium

5\. \*\*Transparency: SHAP, Attention, Feature Drift Logs\*\*



---



\## Universe

| Ticker | Rationale |

|--------|---------|

| SPY | Market proxy, deepest liquidity |

| QQQ | Tech-heavy, high vol |

| AAPL | Earnings catalyst, retail favorite |

| TSLA | Meme + vol monster |

| NVDA | AI leader, gamma squeeze potential |



\*Future expansion: IWM, GLD, TLT (after Phase 5)\*



---



\## Data Philosophy

\- \*\*Free First\*\*: Yahoo Finance, CBOE, FRED

\- \*\*Paid Later\*\*: Polygon (free tier → paid if needed)

\- \*\*Cache Everything\*\*: No live API calls in backtest

\- \*\*Versioned\*\*: `data/raw/`, `data/processed/`, `data/labeled/`



---



\## Non-Negotiables

\- No overfitting: \*\*TimeSeriesSplit only\*\*

\- No survivorship bias: include \*\*all expired contracts\*\*

\- No manual overrides in live system

\- Full audit trail: every trade → `live/log\\\_YYYYMMDD.json`



---



\## End State (Phase 5)

