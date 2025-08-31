"""
NSE Finance - A Python library for NSE India data access
"""

from .api import NSEClient

__version__ = "0.1.1"
__author__ = "Vinod Bhadala"
__email__ = "vinodbhadala@gmail.com"


__all__ = [
    "NSEClient",
    "NSEEndpoints",
    "NSEHTTPError",
]

nse = NSEClient()

# For backward compatibility, create module-level functions
def get_nse_instance():
    """Get a new NSE instance."""
    return nse



