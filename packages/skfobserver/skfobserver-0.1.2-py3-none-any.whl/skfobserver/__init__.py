# skfobserver/skfobserver/__init__.py

"""
Python client library for easy integration with the SKF Observer API.
Provides functionalities for authentication, reading data, and other related operations.
"""

__version__ = "0.1.0"

# Expose the APIClient directly from the package
from .client import APIClient

# You might also expose other commonly used functions or exceptions here
# from .exceptions import SKFObserverAPIError