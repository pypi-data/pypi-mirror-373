"""
TuData - A Python library for accessing Tushare financial data through optimized API

This library provides a convenient interface to access various financial data
including stocks, funds, futures, options, and cryptocurrency data.
"""

__version__ = "1.0.3"
__author__ = "TuData Team"
__email__ = "contact@tudata.com"

# Import main classes and functions
from .core import pro_api, pro_bar, set_token, get_token, BK

# Define what gets imported with "from tudata import *"
__all__ = [
    'pro_api',
    'pro_bar', 
    'set_token',
    'get_token',
    'BK'
]

# Package metadata
__title__ = "tudata"
__summary__ = "A Python library for accessing Tushare financial data through optimized API"
__uri__ = "https://github.com/your-username/tudata" 