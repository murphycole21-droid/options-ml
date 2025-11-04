\# DATA SOURCES



| Data | Source | Access | Cache |

|------|--------|--------|-------|

| Option Chains | Yahoo Finance (`yfinance`) | Free | `data/raw/{ticker}\\\_{date}.parquet` |

| Underlying Prices | Yahoo Finance | Free | Same |

| VIX, VVIX | FRED / Yahoo | Free | `data/raw/vix\\\_daily.csv` |

| SPX PCR | CBOE (datashop.cboe.com) | Free CSV | `data/raw/spx\\\_pcr.csv` |

| Historical Options | Polygon.io (free tier) | 2k req/day | Backup if Yahoo fails |

