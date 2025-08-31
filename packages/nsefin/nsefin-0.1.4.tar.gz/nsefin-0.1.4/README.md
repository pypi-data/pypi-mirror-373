
# NSE Finance - Python Library for NSE India Data

A lightweight Python package to fetch commonly used market data from NSE India and shape it as pandas DataFrames for analysis and trading research.


## ✨ Features

* End‑of‑day (EOD) **bhavcopy** for equities & F\&O
* **Pre‑market** snapshots (All, FO, NIFTY categories)
* **Index details** for multiple market lists (e.g., *NIFTY 50*, *NIFTY AUTO*)
* **Option chain** + optional **Greeks** computation
* Convenience lists: equities, F\&O, ETFs
* **FII/DII** cash/derivatives activity
* **Corporate** actions & announcements, insider trades, upcoming results
* **Most active** (by value/volume, options & futures, OI, etc.)
* Historical data helpers for **equities** (and indices; see notes)

All functions are designed to return clean **`pandas.DataFrame`** objects (unless noted), ready for further transformation and visualization.

---

## 📦 Installation

> If your package is on PyPI:

```bash
pip install nsefin
```


**Requirements:** Python 3.9+, `pandas`, `requests` (and optionally `numpy`).

---

## 🚀 Quick Start

```python
import datetime as dt
import pandas as pd
import nsefin

nse = nsefin.NSEClient()

# Example: EOD Equity Bhavcopy
bhav = nse.get_equity_bhav_copy(dt.datetime(2025, 8, 14))
print(bhav.head())

# Example: Pre‑market (All)
pm_all = nse.get_pre_market_info(category="All")

# Example: Index details (see available market lists below)
ix = nse.get_index_details(category="NIFTY 50")

# Example: Option Chain + Greeks for NIFTY
oc = nse.get_option_chain("NIFTY")
og = nse.compute_greek(oc, strike_diff=50)
```

---

## 🔌 API Overview & Examples

### 1) EOD files

```python
# Equity bhavcopy (EOD)
nse.get_equity_bhav_copy(dt.datetime(2025, 8, 14))

# F&O bhavcopy (EOD)
nse.get_fno_bhav_copy(dt.datetime(2025, 8, 14))

# Optional post‑processing
nse.format_fo_data(df)
```

**Returns:** DataFrames with symbol, series, OHLC, volume/turnover, OI (for F\&O), etc.

---

### 2) Pre‑Market data

```python
nse.get_pre_market_info(category="All")
nse.get_pre_market_info(category="FO")
nse.get_pre_market_info(category="NIFTY")
```

**Tip:** Pre‑market snapshots are most useful before 9:15 IST and during early ticks.

---

### 3) Market Lists & Index Details

```python
# See all supported markets for index details
nse.endpoints.equity_market_list  # -> iterable of valid market names

# Fetch index details
nse.get_index_details(category="NIFTY 50")
nse.get_index_details(category="NIFTY AUTO")
```

**Output:** Index‑level stats (LTP, % change, PE/PB/DY, breadth, time‑window returns where available).

---

### 4) Option Chain & Greeks

```python
# Option chain for an index/stock (near‑dated by default; check function signature)
oc = nse.get_option_chain("NIFTY")

# Compute Greeks on a normalized OC DataFrame (requires columns like LTP, strike, etc.)
og = nse.compute_greek(oc, strike_diff=50)
```

**Note:** Greeks rely on implied vols/assumptions; read function docstring for parameters and expected columns.

---

### 5) Universe Helpers

```python
nse.get_equity_list()
nse.get_fno_list()
nse.get_etf_list()
```

**Use cases:** Screen eligible symbols, build watchlists, or validate tickers.

---

### 6) FII/DII Activity

```python
nse.get_fii_dii_activity()
```

**Common usage:** Market breadth and flows dashboard; daily net buy/sell across segments.

---

### 7) Corporate Data

```python
nse.get_corporate_actions()
nse.get_corporate_actions(subject_filter="dividend")  # filter examples: dividend, split, bonus
nse.get_corporate_announcements()
nse.get_insider_trading()
nse.get_upcoming_results()
```

---

### 8) Most Active & Derivatives Scans

```python
nse.get_most_active_by_volume()
nse.get_most_active_by_value()

nse.get_most_active_index_calls()
nse.get_most_active_index_puts()

nse.get_most_active_stock_calls()
nse.get_most_active_stock_puts()

nse.get_most_active_contracts_by_oi()
nse.get_most_active_contracts_by_volume()

nse.get_most_active_futures_by_volume()
nse.get_most_active_options_by_volume()
```

**Great for:** Intraday scanners, dispersion/volatility screens, liquidity checks for strategy filters.

---

### 9) Historical Data

```python
# Equities
nse.get_equity_historical_data("TCS", "15-08-2024", "31-12-2024")  # ~70 rows limit (API cap)

# Convenience wrapper (day_count based)
nse.history("TCS", day_count=200)

# Indices — currently not working (see Known Limitations below)
# nse.get_index_historical_data("NIFTY 50", "15-08-2024", "31-12-2024")
```


---

## ⚠️ Known Limitations & Notes

* **Index historical data**: `get_index_historical_data(...)` is currently **not working** (NSE endpoints may have changed / rate‑limited). Use alternate data sources or your own cached series.
* **52‑week high/low**: `get_52_week_high_low()` currently errors; pending fix.
* **Daily row caps**: NSE may cap history responses (e.g., \~70 rows). Prefer rolling downloads with local caching.
* **Stability**: NSE’s public endpoints can change without notice. Handle **HTTP 301/403/429**, add **retry with backoff**, and include a realistic **User‑Agent** header.
* **Compliance**: Respect NSE terms of use. This library is for **educational/research** purposes; not endorsed by or affiliated with NSE.

---

## 🛠️ Troubleshooting

* **Empty/blocked responses** → rotate/retry with polite backoff; verify cookies and headers.
* **Schema changes** → use `df.columns` introspection and normalize keys defensively.
* **Timezones** → NSE trading hours are IST; align your schedulers & timestamps accordingly.
* **Option Greeks** → Ensure required columns (spot, strike, rate, expiry, iv) are present/derived before calling `compute_greek`.

---

## 🗺️ Roadmap

* Stable index history with fallbacks
* Robust 52‑week high/low endpoint
* Built‑in caching & sqlite/duckdb persistence helpers
* Async client implementation
* Expanded Greeks/IV calculators + RND utilities

---

## 🤝 Contributing

PRs and issues welcome! Please:

1. Open an issue describing the bug/feature with sample payloads.
2. Add tests where possible.
3. Follow standard formatting (`black`, `ruff`) and type hints.

---

## 📄 License

MIT (or your preferred license). Update `LICENSE` accordingly.

---

## 🙏 Acknowledgements

* NSE India public website and documentation.
* Community packages & references that inspired certain endpoints and data normalizations.

---
