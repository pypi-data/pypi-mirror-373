
"""
nsefin_api_refactored
---------------------
A robust NSE (National Stock Exchange of India) client with:
- Centralized endpoint definitions
- Hardened HTTP session & cookie priming
- Consistent retries with exponential backoff + jitter
- Clear docstrings & typed signatures
- Safe JSON parsing and graceful fallbacks

Designed to be published as a package and used in apps/notebooks.
Returns pandas DataFrames (or lists) similar to yfinance-like workflows.

Usage:
    from nsefin_api_refactored import NSEClient

    nse = NSEClient()
    fno_list = nse.get_fno_list(list_only=True)
    oc_df = nse.get_option_chain("RELIANCE")  # equities
    pre_open = nse.get_pre_market_info("All")

Author: You ✨
"""

from __future__ import annotations

import time
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import StringIO
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests
import io 
import zipfile

import numpy as np
from volg import greek

from urllib.parse import quote


# ----------------------------
# Exceptions
# ----------------------------

class NSEHTTPError(RuntimeError):
    """Raised when an NSE HTTP request ultimately fails after retries."""


# ----------------------------
# Endpoints centralized
# ----------------------------

@dataclass(frozen=True)
class NSEEndpoints:
    """Holds all endpoint and referrer paths in one place so future changes are easy."""
    BASE: str = "https://www.nseindia.com"

    # API endpoints
    UNDERLYING_INFORMATION: str = "/api/underlying-information"
    PRE_OPEN: str = "/api/market-data-pre-open"  # params: key=ALL/FO/NIFTY/BANKNIFTY/...
    EQUITY_STOCK_INDICES: str = "/api/equity-stockIndices"  # params: index=<encoded>
    CORPORATE_ACTIONS: str = "/api/corporates-corporateActions"  # params: index, from_date, to_date
    CORPORATE_ANNOUNCEMENTS: str = "/api/corporate-announcements"  # params: index, from_date, to_date
    CORPORATES_PIT: str = "/api/corporates-pit"  # insider trading; params: index, from_date, to_date
    EVENT_CALENDAR: str = "/api/event-calendar?"  # returns list
    LIVE_MOST_ACTIVE_SECURITIES: str = "/api/live-analysis-most-active-securities"  # params: index=value|volume
    SNAPSHOT_DERIVATIVES: str = "/api/snapshot-derivatives-equity"  # params: index=...
    OPTION_CHAIN_EQUITIES: str = "/api/option-chain-equities"  # params: symbol=
    OPTION_CHAIN_INDICES: str = "/api/option-chain-indices"  # params: symbol=
    QUOTE_EQUITY: str = "/api/quote-equity"  # params: symbol=
    ALL_INDICES: str = "/api/allIndices"  # no params
    FII_DII:str = "api/fiidiiTradeReact"
    HISTORICAL_EQUITY = "/api/historical/cm/equity"
    HISTORICAL_INDEX = "/api/historical/indicesHistory"
    INDEX_SNAPSHOT = "/api/allIndices"

    # Static CSV (note: this is a dated artifact; NSE may change it in future)
    CSV_52_WEEK: str = "https://nsearchives.nseindia.com/content/CM_52_wk_High_low_25012024.csv"

    # Referrer pages (used to obtain cookies/CSRF protections)
    REF_UNDERLYINGS: str = "/products-services/equity-derivatives-list-underlyings-information"
    REF_PRE_OPEN: str = "/market-data/pre-open-market-cm-and-emerge-market"
    REF_LIVE_EQ_MARKET: str = "/market-data/live-equity-market"
    REF_MOST_ACTIVE_EQUITIES: str = "/market-data/most-active-equities"
    REF_MOST_ACTIVE_CONTRACTS: str = "/market-data/most-active-contracts"
    REF_CORP_ACTIONS: str = "/companies-listing/corporate-filings-actions"
    REF_CORP_ANNOUNCEMENTS: str = "/companies-listing/corporate-filings-announcements"
    REF_CORP_PIT: str = "/companies-listing/corporate-filings-insider-trading"
    REF_EVENT_CAL: str = "/companies-listing/corporate-filings-event-calendar"
    REF_FII_DII:str = "/reports/fii-dii"
    REF_HISTORICAL_EQUITY = "/products-services/equities-equity-historical-data"



    equity_market_list = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100',
                          'NIFTY MIDCAP 150', 'NIFTY SMALLCAP 50', 'NIFTY SMALLCAP 100', 'NIFTY SMALLCAP 250',
                          'NIFTY MIDSMALLCAP 400', 'NIFTY 100', 'NIFTY 200', 'NIFTY AUTO',
                          'NIFTY BANK', 'NIFTY ENERGY', 'NIFTY FINANCIAL SERVICES', 'NIFTY FINANCIAL SERVICES 25/50',
                          'NIFTY FMCG',
                          'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA', 'NIFTY PSU BANK', 'NIFTY REALTY',
                          'NIFTY PRIVATE BANK', 'Securities in F&O', 'Permitted to Trade',
                          'NIFTY DIVIDEND OPPORTUNITIES 50',
                          'NIFTY50 VALUE 20', 'NIFTY100 QUALITY 30', 'NIFTY50 EQUAL WEIGHT', 'NIFTY100 EQUAL WEIGHT',
                          'NIFTY100 LOW VOLATILITY 30', 'NIFTY ALPHA 50', 'NIFTY200 QUALITY 30',
                          'NIFTY ALPHA LOW-VOLATILITY 30',
                          'NIFTY200 MOMENTUM 30', 'NIFTY COMMODITIES', 'NIFTY INDIA CONSUMPTION', 'NIFTY CPSE',
                          'NIFTY INFRASTRUCTURE',
                          'NIFTY MNC', 'NIFTY GROWTH SECTORS 15', 'NIFTY PSE', 'NIFTY SERVICES SECTOR',
                          'NIFTY100 LIQUID 15',
                          'NIFTY MIDCAP LIQUID 15']

# ----------------------------
# Client
# ----------------------------

class NSEClient:
    """
    Hardened HTTP client for NSE endpoints.

    Features:
        - Persistent requests.Session with realistic headers
        - Cookie priming via homepage and optional referrer pages
        - Exponential backoff with jitter on failure
        - JSON content-type checks and safe parsing
        - Helpful exceptions and graceful empty return fallbacks

    Parameters
    ----------
    retries : int
        Number of attempts for each API call (default: 3).
    timeout : float
        Per-request timeout in seconds (default: 12.0).
    backoff : float
        Base backoff (seconds) for retries; actual sleep is backoff * 2**(attempt-1) + jitter.
    user_agent : Optional[str]
        Override the default desktop UA string.
    endpoints : Optional[NSEEndpoints]
        Custom endpoints object if NSE changes paths.
    session : Optional[requests.Session]
        Provide a preconfigured session (e.g., with proxies). If None, a new one is created.
    """

    def __init__(
        self,
        retries: int = 3,
        timeout: float = 12.0,
        backoff: float = 1.25
    ) -> None:
        self.retries = max(1, retries)
        self.timeout = timeout
        self.backoff = backoff
        self.endpoints = NSEEndpoints()

        # Prepare session & headers
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": self.endpoints.BASE,
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        })

        self._prime_cookies()

    # ----------------------------
    # Internal HTTP helpers
    # ----------------------------

    def _prime_cookies(self) -> None:
        """Hit the base URL once to establish cookies for the session."""
        try:
            self.session.get(self.endpoints.BASE, timeout=self.timeout)
        except Exception as e:
            # Not fatal; we will retry during API requests
            pass

    def _referrer_get(self, ref_path: Optional[str]) -> None:
        """
        If a referrer path is provided, issue a GET to that page to refresh cookies/CSRF.
        This mimics browser flow that NSE expects.
        """
        if not ref_path:
            return
        try:
            self.session.get(
                f"{self.endpoints.BASE}{ref_path}",
                timeout=self.timeout,
                headers={"Referer": f"{self.endpoints.BASE}{ref_path}"}
            )
        except Exception:
            # Not fatal; API call will still be attempted
            pass

    def _get_json(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        ref_path: Optional[str] = None,
        expect_list: bool = False,
        allow_text_json: bool = True,
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Generic JSON GET with retries, cookie refresh, and content-type checks.

        Parameters
        ----------
        path : str
            API path (e.g., "/api/underlying-information").
        params : dict, optional
            Query parameters to include.
        ref_path : str, optional
            A referrer page path to hit before the API call to refresh cookies.
        expect_list : bool
            Set True if a top-level JSON list is expected (e.g., event calendar).
        allow_text_json : bool
            Some NSE endpoints return 'text/html' but still contain valid JSON.
            If True, we attempt to parse JSON even when content-type mismatches.

        Returns
        -------
        dict | list
            Parsed JSON.

        Raises
        ------
        NSEHTTPError
            If all retry attempts fail or JSON is invalid.
        """
        url = f"{self.endpoints.BASE}{path}"
        last_error: Optional[Exception] = None

        for attempt in range(1, self.retries + 1):
            try:
                # Refresh cookies via referrer (if provided)
                self._referrer_get(ref_path)

                resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()

                ct = resp.headers.get("Content-Type", "")
                is_json_ct = "application/json" in ct or "application/octet-stream" in ct

                # If JSON content-type: trust json()
                if is_json_ct:
                    data = resp.json()
                else:
                    # Some NSE endpoints send JSON with text/html; parse if allowed
                    if allow_text_json:
                        try:
                            data = resp.json()
                        except ValueError as ve:
                            raise ValueError("Non‑JSON response (blocked or HTML page).") from ve
                    else:
                        raise ValueError("Unexpected Content-Type; refusing to parse.")

                # Basic shape sanity checks if caller expects a list
                if expect_list and not isinstance(data, list):
                    raise ValueError("Expected a JSON list but received an object.")
                if not expect_list and not isinstance(data, (dict, list)):
                    raise ValueError("Unexpected JSON top-level type.")

                return data

            except Exception as e:
                last_error = e
                if attempt < self.retries:
                    sleep_for = self.backoff * (2 ** (attempt - 1)) + random.uniform(0, 0.9)
                    time.sleep(sleep_for)
                    # Re-prime cookies in case NSE flipped tokens
                    self._prime_cookies()
                    continue
                else:
                    raise NSEHTTPError(f"Failed GET {url} after {self.retries} attempts: {e}") from e

        # Should never reach here
        assert last_error is not None
        raise NSEHTTPError(f"Failed GET {url}: {last_error}")


    # ----------------------------
    # Public API methods
    # ----------------------------

    def get_fno_list(self, list_only: bool = False) -> Union[pd.DataFrame, List[str]]:
        """
        Fetch F&O underlyings along with recent lot sizes.

        Parameters
        ----------
        list_only : bool
            If True, returns just a list of symbols. Otherwise returns a DataFrame.

        Returns
        -------
        pandas.DataFrame | list[str]
        """
        data = self._get_json(
            self.endpoints.UNDERLYING_INFORMATION,
            ref_path=self.endpoints.REF_UNDERLYINGS
        )
        # Expected shape: {"data": {"UnderlyingList": [...]}} or {"data": [...]}
        records = []
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict) and "UnderlyingList" in data["data"]:
                records = data["data"]["UnderlyingList"]
            elif "data" in data and isinstance(data["data"], list):
                records = data["data"]
        elif isinstance(data, list):
            records = data

        df = pd.DataFrame(records)
        if df.empty:
            return [] if list_only else df

        return df["symbol"].tolist() if list_only and "symbol" in df.columns else df

    def get_option_chain(self, symbol: str) -> pd.DataFrame:
        """
        Fetch option chain for a symbol (auto-selects indices/equities endpoint).

        Parameters
        ----------
        symbol : str
            'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY' treated as indices, others as equities.

        Returns
        -------
        pandas.DataFrame
            Flattened/organized option chain if possible; otherwise raw records DataFrame.
        """
        sym = symbol.upper()
        is_index = sym in {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}
        path = self.endpoints.OPTION_CHAIN_INDICES if is_index else self.endpoints.OPTION_CHAIN_EQUITIES
        params = {"symbol": sym}
        data = self._get_json(path, params=params, ref_path=self.endpoints.REF_LIVE_EQ_MARKET)

        # Typical shape: {"records": {..., "data": [...]}, ...}
        records = (data or {}).get("records", {})
        data_list = records.get("data", [])

        # Return as DataFrame of raw legs; caller can pivot further as needed
        df = pd.json_normalize(data_list)

        # Drop unwanted columns
        df = df.drop(columns=['CE.strikePrice', 'CE.expiryDate',
                               'PE.strikePrice', 'PE.expiryDate',
                               'CE.impliedVolatility','PE.impliedVolatility',
                               'PE.totalBuyQuantity', 'PE.totalSellQuantity',
                               'CE.totalBuyQuantity', 'CE.totalSellQuantity',
                               'CE.pchangeinOpenInterest','PE.pchangeinOpenInterest',
                               'PE.bidQty', 'PE.askQty', 'CE.bidQty', 'CE.askQty',    
                               'PE.change','CE.change','CE.pChange', 'PE.pChange',
                               'PE.bidprice', 'PE.askPrice', 'CE.bidprice', 'CE.askPrice',
                               'CE.underlying', 'PE.underlying','CE.underlyingValue',
                               'CE.identifier','PE.identifier'])


        df = df.rename(columns={
            'strikePrice': 'strike',
            'expiryDate': 'expiry',
            'PE.lastPrice': 'pe_ltp',
            'CE.lastPrice': 'ce_ltp',
            'PE.openInterest': 'pe_oi',
            'CE.openInterest': 'ce_oi',
            'PE.changeinOpenInterest': 'pe_oi_change',
            'CE.changeinOpenInterest': 'ce_oi_change',
            'PE.totalTradedVolume': 'pe_volume',
            'CE.totalTradedVolume': 'ce_volume',
             'PE.underlyingValue' : 'spot_price',

         })

        df['name'] = symbol

        return df

    def get_pre_market_info(self, category: str = "All") -> pd.DataFrame:
        """
        Get pre-market information for a category.

        Valid categories: 'All','NIFTY 50','Nifty Bank','Emerge','Securities in F&O','Others'

        Returns
        -------
        pandas.DataFrame
        """
        #available key value pair 
        all_categories = {
            "NIFTY 50": "NIFTY",
            "Nifty Bank": "BANKNIFTY",
            "Emerge": "SME",
            "Securities in F&O": "FO",
            "Others": "OTHERS",
            "All": "ALL",
        }

        key = category
        params = {"key": key}
        data = self._get_json(self.endpoints.PRE_OPEN, params=params, ref_path=self.endpoints.REF_PRE_OPEN)

        # Expected shape: {"data": [{ "metadata": {...}}, ...]}
        rows = []
        for item in (data or {}).get("data", []):
            if isinstance(item, dict) and "metadata" in item:
                rows.append(item["metadata"])
        return pd.DataFrame(rows)

    def get_index_details(self, category: str, list_only: bool = False) -> Union[pd.DataFrame, List[str]]:
        """
        Get index members/details for a given category (index name).

        Parameters
        ----------
        category : str
            Index name as shown on NSE (e.g., "NIFTY 50").
        list_only : bool
            If True, return only the list of member symbols.

        Returns
        -------
        pandas.DataFrame | list[str]
        """
        # NSE expects encoded name in 'index' param
        params = {"index": category}
        data = self._get_json(self.endpoints.EQUITY_STOCK_INDICES, params=params, ref_path=self.endpoints.REF_LIVE_EQ_MARKET)

        if not isinstance(data, dict) or "data" not in data:
            return [] if list_only else pd.DataFrame()

        df = pd.DataFrame(data["data"])
        if "meta" in df.columns:
            df = df.drop(columns=["meta"], errors="ignore")
        if "symbol" in df.columns:
            df = df.set_index("symbol", drop=True)

        if list_only and not df.empty:
            # Some responses include a first row of the index itself; skip it if detected
            try:
                return sorted(df.index.tolist()[1:])
            except Exception:
                return sorted(df.index.tolist())

        return df

    def get_52_week_high_low(self, stock: Optional[str] = None) -> Union[pd.DataFrame, Optional[Dict[str, Any]]]:
        """
        Fetch the dated 52-week high/low CSV snapshot from NSE archives.

        Notes
        -----
        This CSV link is static and dated ("Effective for 25-Jan-2024").
        NSE may update the path/name; keep an eye and adjust `CSV_52_WEEK` in `NSEEndpoints`.

        Returns
        -------
        pandas.DataFrame | dict | None
            Returns a full DataFrame by default, or a dict for a specific stock, or None if not found.
        """
        # This file is hosted on a different domain; use session directly with full URL
        url = self.endpoints.CSV_52_WEEK
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                txt = resp.text.replace(
                    '"Disclaimer - The Data provided in the adjusted 52 week high and adjusted 52 week low columns  are adjusted for corporate actions (bonus, splits & rights).For actual (unadjusted) 52 week high & low prices, kindly refer bhavcopy."\\n"Effective for 25-Jan-2024"\\n',
                    ''
                )
                df = pd.read_csv(StringIO(txt))
                break
            except Exception as e:
                if attempt < self.retries:
                    time.sleep(self.backoff * (2 ** (attempt - 1)) + random.uniform(0, 0.9))
                    continue
                raise NSEHTTPError(f"Failed to fetch 52-week CSV after {self.retries} attempts: {e}") from e

        if stock is None:
            return df

        row = df[df['SYMBOL'] == stock]
        if row.empty:
            return None
        return {
            "Symbol": stock,
            "52 Week High": row["Adjusted 52_Week_High"].values[0],
            "52 Week High Date": row["52_Week_High_Date"].values[0],
            "52 Week Low": row["Adjusted 52_Week_Low"].values[0],
            "52 Week Low Date": row["52_Week_Low_DT"].values[0],
        }

    def get_corporate_actions(
        self,
        from_date_str: Optional[str] = None,
        to_date_str: Optional[str] = None,
        subject_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch corporate action data.

        Parameters
        ----------
        from_date_str : str, optional
            DD-MM-YYYY; defaults to 30 days back.
        to_date_str : str, optional
            DD-MM-YYYY; defaults to today.
        subject_filter : str, optional
            Case-insensitive substring filter on 'subject'.

        Returns
        -------
        pandas.DataFrame
        """
        if not from_date_str:
            from_date_str = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")
        if not to_date_str:
            to_date_str = datetime.now().strftime("%d-%m-%Y")

        params = {"index": "equities", "from_date": from_date_str, "to_date": to_date_str}
        data = self._get_json(self.endpoints.CORPORATE_ACTIONS, params=params, ref_path=self.endpoints.REF_CORP_ACTIONS)

        df = pd.DataFrame(data or [])
        if subject_filter and not df.empty and "subject" in df.columns:
            df = df[df["subject"].str.contains(subject_filter, case=False, na=False)]
        return df

    def get_corporate_announcements(
        self,
        from_date_str: Optional[str] = None,
        to_date_str: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch corporate announcements.

        Parameters
        ----------
        from_date_str : str, optional
            DD-MM-YYYY; defaults to 30 days back.
        to_date_str : str, optional
            DD-MM-YYYY; defaults to today.

        Returns
        -------
        pandas.DataFrame
        """
        if not from_date_str:
            from_date_str = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")
        if not to_date_str:
            to_date_str = datetime.now().strftime("%d-%m-%Y")

        params = {"index": "equities", "from_date": from_date_str, "to_date": to_date_str}
        data = self._get_json(self.endpoints.CORPORATE_ANNOUNCEMENTS, params=params, ref_path=self.endpoints.REF_CORP_ANNOUNCEMENTS)
        return pd.DataFrame(data or [])

    def get_insider_trading(
        self,
        from_date_str: Optional[str] = None,
        to_date_str: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch insider trading (PIT) filings.

        Parameters
        ----------
        from_date_str : str, optional
            DD-MM-YYYY; defaults to 30 days back.
        to_date_str : str, optional
            DD-MM-YYYY; defaults to today.

        Returns
        -------
        pandas.DataFrame
        """
        if not from_date_str:
            from_date_str = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")
        if not to_date_str:
            to_date_str = datetime.now().strftime("%d-%m-%Y")

        params = {"index": "equities", "from_date": from_date_str, "to_date": to_date_str}
        data = self._get_json(self.endpoints.CORPORATES_PIT, params=params, ref_path=self.endpoints.REF_CORP_PIT)
        # Expected {"data": [...]}
        rows = (data or {}).get("data", []) if isinstance(data, dict) else data
        return pd.DataFrame(rows or [])

    def get_upcoming_results(self) -> pd.DataFrame:
        """
        Fetch upcoming event calendar and filter to Results.
        Returns a DataFrame with 'purpose' containing 'Results' (case-insensitive).

        Returns
        -------
        pandas.DataFrame
        """
        data = self._get_json(self.endpoints.EVENT_CALENDAR, ref_path=self.endpoints.REF_EVENT_CAL, expect_list=True)
        df = pd.DataFrame(data or [])
        if df.empty or "purpose" not in df.columns:
            return pd.DataFrame()
        return df[df["purpose"].str.contains("Results", case=False, na=False)]

    def get_most_active_by_volume(self) -> pd.DataFrame:
        """Most active equities by volume."""
        params = {"index": "volume"}
        data = self._get_json(self.endpoints.LIVE_MOST_ACTIVE_SECURITIES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_EQUITIES)
        return pd.DataFrame((data or {}).get("data", []))

    def get_most_active_by_value(self) -> pd.DataFrame:
        """Most active equities by value."""
        params = {"index": "value"}
        data = self._get_json(self.endpoints.LIVE_MOST_ACTIVE_SECURITIES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_EQUITIES)
        return pd.DataFrame((data or {}).get("data", []))

    def get_most_active_index_calls(self) -> pd.DataFrame:
        """Most active index calls (options)."""
        params = {"index": "calls-index-vol"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("OPTIDX", {}) or {}).get("data", []))

    def get_most_active_index_puts(self) -> pd.DataFrame:
        """Most active index puts (options)."""
        params = {"index": "puts-index-vol"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("OPTIDX", {}) or {}).get("data", []))

    def get_most_active_stock_calls(self) -> pd.DataFrame:
        """Most active stock calls (options)."""
        params = {"index": "calls-stocks-vol"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("OPTSTK", {}) or {}).get("data", []))

    def get_most_active_stock_puts(self) -> pd.DataFrame:
        """Most active stock puts (options)."""
        params = {"index": "puts-stocks-vol"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("OPTSTK", {}) or {}).get("data", []))

    def get_most_active_contracts_by_oi(self) -> pd.DataFrame:
        """Most active contracts by open interest."""
        params = {"index": "oi"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("volume", {}) or {}).get("data", []))

    def get_most_active_contracts_by_volume(self) -> pd.DataFrame:
        """Most active contracts by number of contracts."""
        params = {"index": "contracts"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("volume", {}) or {}).get("data", []))

    def get_most_active_futures_by_volume(self) -> pd.DataFrame:
        """Most active futures by volume."""
        params = {"index": "futures"}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("volume", {}) or {}).get("data", []))

    def get_most_active_options_by_volume(self) -> pd.DataFrame:
        """Most active options by volume."""
        params = {"index": "options", "limit": 20}
        data = self._get_json(self.endpoints.SNAPSHOT_DERIVATIVES, params=params, ref_path=self.endpoints.REF_MOST_ACTIVE_CONTRACTS)
        return pd.DataFrame(((data or {}).get("volume", {}) or {}).get("data", []))


    def _download_csv(self, url: str, referrer: str = None) -> pd.DataFrame:
        """Generic CSV/ZIP downloader with cookie priming."""
        if referrer:
            self.session.get(referrer, timeout=10)  # get cookies
        resp = self.session.get(url, timeout=20)
        resp.raise_for_status()

        if resp.headers.get("Content-Type", "").startswith("application/zip"):
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                file_name = z.namelist()[0]
                with z.open(file_name) as f:
                    return pd.read_csv(f)
        elif resp.headers.get("Content-Type", "").startswith("text/csv"):
            return pd.read_csv(io.StringIO(resp.text))
        else:
            raise ValueError("Unexpected file type for bhav copy")


    def get_equity_list(self) -> pd.DataFrame:
        """Get NSE equity list (all available securities)."""
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        return self._download_csv(url, referrer="https://www.nseindia.com/market-data/securities-available-for-trading")

    def get_etf_list(self) -> pd.DataFrame:
        """Get NSE ETF list."""
        url = "https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv"
        return self._download_csv(url, referrer="https://www.nseindia.com/market-data/securities-available-for-trading")

    def get_fii_dii_activity(self) -> pd.DataFrame:
        """Get FII/DII trading activity data."""
        data = self._get_json(self.endpoints.FII_DII, ref_path=self.endpoints.REF_FII_DII)

        return pd.DataFrame(data)


    def get_equity_bhav_copy(self, date: datetime) -> pd.DataFrame:
        """
        Fetch NSE equity cash market bhav copy for a given date.

        Parameters
        ----------
        date : datetime
            The trading date for which to fetch the bhav copy.

        Returns
        -------
        pd.DataFrame
            Bhav copy dataframe. Empty dataframe if not available.
        """
        date_str = date.strftime("%d%m%Y")
        url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
        headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Connection": "keep-alive"
        }


        try:
            resp = self.session.get(url, headers=headers, timeout=30)
            if resp.status_code == 404:
                print(f"Bhav copy not available for {date.strftime('%Y-%m-%d')}")
                return pd.DataFrame()

            resp.raise_for_status()

            df = pd.read_csv(StringIO(resp.text))

                        # Filter only EQ series
            df = df[df[' SERIES'] == ' EQ']

            # Clean and rename columns
            df = df.rename(columns=lambda x: x.strip().lower())

            # Drop unwanted columns
            df = df.drop(columns=['date1', 'series'])

            # Convert key columns to numeric
            for col in ['last_price', 'deliv_qty', 'deliv_per']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.rename(columns={'prev_close': 'prv_close','open_price':'open','high_price': 'high','low_price': 'low',
                                'last_price': 'last','close_price': 'close','avg_price':'vwap','ttl_trd_qnty': 'trade_qty',
                                    'turnover_lacs': 'value_lakh', 'no_of_trades': 'volume','deliv_qty': 'del_qty','deliv_per': 'del_pct' })

            return df

        except Exception as e:
            print(f"Error fetching equity bhav copy for {date.strftime('%Y-%m-%d')}: {e}")
            return pd.DataFrame()

    def get_fno_bhav_copy(self, date: datetime) -> pd.DataFrame:
        """
        Fetch NSE derivatives (F&O) bhav copy for a given date.

        Parameters
        ----------
        date : datetime
            The trading date for which to fetch the bhav copy.

        Returns
        -------
        pd.DataFrame
            Bhav copy dataframe. Empty dataframe if not available.
        """
        date_str = date.strftime("%Y%m%d")
        url = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{date_str}_F_0000.csv.zip"
        headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Connection": "keep-alive"
        }

        try:
            resp = self.session.get(url, headers=headers, timeout=30)
            if resp.status_code == 404:
                print(f"F&O bhav copy not available for {date.strftime('%Y-%m-%d')}")
                return pd.DataFrame()
            resp.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                csv_name = z.namelist()[0]
                df = pd.read_csv(z.open(csv_name))

            df = df.drop(columns=[ 'BizDt','Src','Sgmt','FinInstrmId','SctySrs','ISIN','FininstrmActlXpryDt','SttlmPric',
                                   'SsnId', 'Rmks', 'Rsvd1', 'Rsvd2', 'Rsvd3', 'Rsvd4'])

            # Rename columns to clearer names
            df = df.rename(columns={'TradDt': 'date','FinInstrmTp':'category','TckrSymb': 'symbol','XpryDt': 'expiry',
                                      'StrkPric': 'strike','OptnTp': 'right','FinInstrmNm':'ticker',
                            'OpnPric': 'open','HghPric': 'high', 'LwPric': 'low','ClsPric': 'close','LastPric': 'last','PrvsClsgPric': 'prv_close',
                            'UndrlygPric': 'spot','OpnIntrst': 'oi','ChngInOpnIntrst': 'coi','TtlTradgVol': 'volume',
                            'TtlTrfVal': 'trade_value','TtlNbOfTxsExctd': 'trade_contract','NewBrdLotQty': 'lot_size' })

            return df

        except Exception as e:
            print(f"Error fetching F&O bhav copy for {date.strftime('%Y-%m-%d')}: {e}")
            return pd.DataFrame()


    def format_fo_data(self,df:pd.DataFrame) -> pd.DataFrame:

        """
        Process FO (Futures & Options) EOD data:
        - Aggregates futures OI, COI, volume
        - Aggregates CE/PE OI, COI, volume
        - Finds ATM strike
        - Extracts ATM CE/PE prices
        - Calculates straddle, percentage, synthetic future
        - Adds DTE (days to expiry)
        """

        # Ensure consistent column names
        df = df.copy()
        df['expiry'] = pd.to_datetime(df['expiry'])

        # 1️⃣ Split futures & options data
        fut_mask = df['category'].isin(['STF', 'IDF'])
        opt_mask = df['category'].isin(['STO', 'IDO'])

        # 2️⃣ Find ATM strikes in one groupby
        atm_df = (
            df[opt_mask]
            .assign(diff=(df['strike'] - df['spot']).abs())
            .sort_values(['symbol', 'expiry', 'diff'])
            .groupby(['symbol', 'expiry'])
            .first()
            .reset_index()[['symbol', 'expiry', 'strike', 'spot']]
            .rename(columns={'strike': 'ATM_STRIKE', 'spot': 'SPOT'})
        )

        # 3️⃣ Aggregate futures metrics
        fut_agg = (
            df[fut_mask]
            .groupby(['symbol', 'expiry'])
            .agg(
                FUT_OI=('oi', 'sum'),
                FUT_COI=('coi', 'sum'),
                FUT_VOL=('volume', 'sum'),
                PREV=('prv_close', 'last'),
                OPEN=('open', 'last'),
                HIGH=('high', 'last'),
                LOW=('low', 'last'),
                CLOSE=('close', 'last')
            )
            .reset_index()
        )

        # 4️⃣ Aggregate CE/PE option metrics
        opt_agg = (
            df[opt_mask]
            .pivot_table(
                index=['symbol', 'expiry', 'right'],
                values=['oi', 'coi', 'volume', 'close'],
                aggfunc='sum'
            )
            .unstack(fill_value=0)
        )

        # Flatten multi-index columns: ('oi', 'CE') → 'CE_OI'
        opt_agg.columns = [f"{right}_{metric}".upper() for metric, right in opt_agg.columns]
        opt_agg = opt_agg.reset_index()

        # 5️⃣ Merge futures + options + ATM
        merged = fut_agg.merge(opt_agg, on=['symbol', 'expiry'], how='left')
        merged = merged.merge(atm_df, on=['symbol', 'expiry'], how='left')

        # 6️⃣ Extract ATM CE/PE close prices
        atm_prices = (
            df[opt_mask]
            .groupby(['symbol', 'expiry', 'strike', 'right'])['close']
            .last()
            .unstack()
            .reset_index()
        )

        atm_prices = atm_prices.merge(atm_df, left_on=['symbol', 'expiry', 'strike'],
                                      right_on=['symbol', 'expiry', 'ATM_STRIKE'],
                                      how='right')[['symbol', 'expiry', 'CE', 'PE']]

        merged = merged.merge(atm_prices, on=['symbol', 'expiry'], how='left')

        # 7️⃣ Calculate derived fields
        merged['STRADDLE'] = (merged['CE'] + merged['PE']).round(2)
        merged['PCT'] = (merged['STRADDLE'] / merged['SPOT'] * 100).round(2)
        merged['SFUT'] = (merged['ATM_STRIKE'] + merged['CE'] - merged['PE']).round(2)

        # 8️⃣ Add Days to Expiry
        current_date = pd.Timestamp.now().normalize()
        merged['DTE'] = (merged['expiry'] - current_date).dt.days

        return merged



    def get_equity_historical_data(self, symbol: str, from_date: str, to_date: str) -> pd.DataFrame:
        """
        Fetch historical equity data for a given symbol from NSE.

        Parameters
        ----------
        symbol : str
            Equity symbol (e.g., 'WIPRO').
        from_date : str
            Start date in dd-mm-yyyy format.
        to_date : str
            End date in dd-mm-yyyy format.

        Returns
        -------
        pandas.DataFrame
            Historical OHLCV data from NSE.
        """
        sym = symbol.upper()
        params = {
            "symbol": sym,
            "series": '["EQ"]',
            "from": from_date,
            "to": to_date
        }

        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Connection": "keep-alive"
            }

        # Hit referrer first to set cookies (historical data page)
        ref_url = f"https://www.nseindia.com/get-quotes/equity"
        self.session.get(ref_url, headers=headers, timeout=self.timeout)

        # Now call API
        url = f"{self.endpoints.BASE}{self.endpoints.HISTORICAL_EQUITY}"
        resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()

        if not data or "data" not in data:
            print(f"⚠ No historical data found for {sym} between {from_date} and {to_date}")
            return pd.DataFrame()

        df = pd.DataFrame(data["data"])

        df = df[['CH_SYMBOL','CH_OPENING_PRICE','CH_TRADE_HIGH_PRICE','CH_TRADE_LOW_PRICE','CH_CLOSING_PRICE','CH_LAST_TRADED_PRICE',
                 'CH_PREVIOUS_CLS_PRICE','VWAP','CH_TOT_TRADED_QTY','CH_TOT_TRADED_VAL','CH_52WEEK_HIGH_PRICE','CH_52WEEK_LOW_PRICE',
                 'CH_TOTAL_TRADES','mTIMESTAMP']].copy()

        df = df.rename(columns={'mTIMESTAMP':'date','CH_SYMBOL':'symbol','CH_OPENING_PRICE':'open','CH_TRADE_HIGH_PRICE':'high','CH_TRADE_LOW_PRICE':'low',
                                'CH_CLOSING_PRICE':'close','CH_LAST_TRADED_PRICE':'ltp','CH_PREVIOUS_CLS_PRICE':'prv_close','VWAP':'vwap',
                                'CH_TOT_TRADED_QTY':'trade_qty','CH_TOT_TRADED_VAL':'trade_value_cr','CH_52WEEK_HIGH_PRICE':'52w_high',
                                'CH_52WEEK_LOW_PRICE':'52w_low','CH_TOTAL_TRADES':'volume'})


        # Convert to datetime
        df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")

        df['trade_value_cr'] = round(df["trade_value_cr"] / 1e7,2)

        return df



    def get_index_historical_data(self, symbol: str, from_date: str, to_date: str):
        """
        Fetch historical equity data for a given symbol from NSE.

        Parameters
        ----------
        symbol : str
            Equity symbol (e.g., 'NIFTY 50').
        from_date : str
            Start date in dd-mm-yyyy format.
        to_date : str
            End date in dd-mm-yyyy format.

        Returns
        -------
        pandas.DataFrame
            Historical OHLCV data from NSE.
        """
        sym = quote(symbol.upper(), safe="")
        params = {
            "indexType": sym,
            "from": from_date,
            "to": to_date
        }

        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Connection": "keep-alive"
            }

        # Hit referrer first to set cookies (historical data page)
        ref_url = f"https://www.nseindia.com/reports-indices-historical-index-data"
        self.session.get(ref_url, headers=headers, timeout=self.timeout)

        # Now call API
        url = f"{self.endpoints.BASE}{self.endpoints.HISTORICAL_INDEX}"

        print(url,params)
        resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        #data = resp.json()

        return resp

    def history(self,symbol: str, day_count: int = 90, as_on_date: datetime = None) -> pd.DataFrame:
        """
        Fetch historical equity data over any period by batching NSE API calls.

        Parameters
        ----------
        symbol : str
            Stock symbol (e.g., 'WIPRO').
        day_count : int
            Number of calendar days to fetch (max 70 days per NSE call internally).
        as_on_date : datetime, optional
            End date for fetching data (defaults to today).

        Returns
        -------
        pandas.DataFrame
            Combined historical OHLCV data for the requested period.
        """
        if as_on_date is None:
            as_on_date = datetime.now()



        all_data = []

        chunk = 100
        max_date = (as_on_date - timedelta(days=day_count))
        to_date = as_on_date

        while True:
            from_date = (to_date - timedelta(days=chunk))
            to_date = to_date

            df = self.get_equity_historical_data(symbol,from_date.strftime("%d-%m-%Y"),to_date.strftime("%d-%m-%Y"))
            if df.empty:
                break

            all_data.append(df)
            earliest_date = df["date"].min()

            # Stop if we already covered everything
            if earliest_date <= max_date:
                print(f'Downloaded data for symbol {symbol}')
                break

            # Move the window back
            to_date = earliest_date - timedelta(days=1)

        if not all_data:
            return pd.DataFrame()

        # Merge and sort by date
        final_df = pd.concat(all_data, ignore_index=True)

        # Sort by mTIMESTAMP
        final_df = final_df.sort_values("date").reset_index(drop=True)

        return final_df


    def compute_greek(self,df,strike_diff=50):


        df['sfut_price'] = df['strike'] + df['ce_ltp'] - df['pe_ltp']
        df['atm_strike'] = (df['sfut_price'] / strike_diff).round() * strike_diff

        df['count'] = (df['strike'] - df['atm_strike']) / strike_diff

        df['expiry_date'] = pd.to_datetime(df["expiry"], format="%d-%b-%Y")

        # Convert the 'expiry_date' column to a datetime object and add the 15:30:00 timestamp
        df['expiry_datetime'] = pd.to_datetime(df['expiry'] + ' 15:30:00', format='%d-%b-%Y %H:%M:%S')

        date = dt.datetime.now()

        df['dte'] = np.floor((df['expiry_datetime'] - date ).dt.total_seconds() / (24 * 60 * 60)).fillna(0).astype(int)
        df['dte_greeks'] = (df['expiry_datetime'] - date).dt.total_seconds() / (24 * 60 * 60)

        df = df[df['dte'] <= 90].reset_index(drop=True)

        # Replace negative dte with 0
        df["dte"] = df["dte"].clip(lower=0)
        df["dte_greeks"] = df["dte_greeks"].clip(lower=0)

        df = df[(df['count'] >= -50) & (df['count'] <= 50)].reset_index(drop=True)

        column_mapping = {
            "sfut_price": "sfut_price",
            "strike_price": "strike",
            "dte": "dte_greeks",
            "count": "count",
            "ce_ltp": "ce_ltp",
            "pe_ltp": "pe_ltp"
        }


        df = greek.compute_greeks_vectorized(df, columns=column_mapping)

        return df


    def bulk_history(self,tickers, day_count=200):
        """
        Fetch historical data for multiple NSE tickers using nse.history.

        Args:
            tickers (list): List of NSE tickers as strings.
            day_count (int): Number of days to fetch for each ticker.

        Returns:
            pd.DataFrame: Multi-index DataFrame with 'Ticker' and 'Date'.
        """
        all_data = []

        for ticker in tickers:
            try:
                # Fetch data for single ticker
                df = self.history(ticker, day_count=day_count)
                df = df.copy()
                df['Ticker'] = ticker  # Add ticker column
                all_data.append(df)
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

        # Combine all tickers into one DataFrame
        if all_data:
            result = pd.concat(all_data).reset_index()
            # Optional: set multi-index for easy selection
            result.set_index(['Ticker', 'date'], inplace=True)
            return result
        else:
            return pd.DataFrame()  # Empty if no data fetched


    def get_index_snapshot(self) -> pd.DataFrame:

        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Connection": "keep-alive"
            }

        # Hit referrer first to set cookies (historical data page)
        ref_url = f"https://www.nseindia.com/market-data/live-market-indices"
        self.session.get(ref_url, headers=headers, timeout=self.timeout)

        # Now call API
        url = f"{self.endpoints.BASE}{self.endpoints.INDEX_SNAPSHOT}"

        resp = self.session.get(url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()

        df = pd.DataFrame(data["data"])

        df = df[['indexSymbol','last','percentChange','previousClose','pe', 'pb', 'dy', 'declines', 'advances','unchanged', 
             'previousDay', 'oneWeekAgo', 'oneMonthAgo', 'oneYearAgo']]

        # Calculate returns (relative change in %)
        df['r1D']  = round((df['last'] / df['previousDay']   - 1) * 100,2)
        df['r5D']  = round((df['last'] / df['oneWeekAgo']    - 1) * 100,2)
        df['r30D'] = round((df['last'] / df['oneMonthAgo']   - 1) * 100,2)
        df['r365D']= round((df['last'] / df['oneYearAgo']    - 1) * 100,2)

        # Drop raw history columns
        df = df.drop(columns=['percentChange','previousDay','oneWeekAgo','oneMonthAgo','oneYearAgo'])

        df = df.rename(columns={"indexSymbol": "symbol","last": "ltp","previousClose": "close"})

        df = df.dropna()

        return df




if __name__ == "__main__":
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    # Initialize NSE instance
    nse = NSEClient()

    # Select Timeframe for historic data download
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)

    # Symbol Search - NSE
    df = nse.get_index_snapshot()
    print(df.head(10))

