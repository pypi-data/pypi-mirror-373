"""
NSE Finance - A Python library for NSE India data access
"""

from .api import NSEClient

__version__ = "0.1.1"
__author__ = "Vinod Bhadala"
__email__ = "vinodbhadala@gmail.com"

# For backward compatibility, create module-level functions
def get_nse_instance():
    """Get a new NSE instance."""
    return NSEClient()

# Renamed functions with better descriptions
def get_snapshot():

    nse = NSEClient()
    return nse.get_index_snapshot()

def get_price_history(symbol):
    """
    Get historical OHLCV price data for a stock or index.

    Args:
        symbol (str): Symbol name
    Returns:
        pandas.DataFrame: Historical OHLCV data
    """
    nse = NSEClient()
    
    #nse.get_equity_historical_data("TCS", "15-08-2024", "31-12-2024") only for 70 rows.
    return nse.history(symbol,day_count=50)
    

def get_option_chain_data(symbol):
    """
    Get option chain data for a stock or index.

    Args:
        symbol (str): Symbol name
        is_index (bool): True if symbol is an index

    Returns:
        pandas.DataFrame: Option chain data
    """
    nse = NSEClient()
    return nse.get_option_chain(symbol)

def get_pre_market_data(category='All'):
    """
    Get pre-market trading data.

    Args:
        category (str): Market category

    Returns:
        pandas.DataFrame: Pre-market data
    """
    nse = NSEClient()
    return nse.get_pre_market_info(category)




__all__ = [
    "NSEClient",
    "NSEEndpoints",
    "NSEHTTPError",
]