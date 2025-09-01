"""
Phandas: Professional quantitative analysis framework for cryptocurrency markets.

Clean, efficient factor analysis with pandas-like API.
"""

__author__ = "Phantom Management"
__version__ = "0.2.0"

# Core components
from .core import (
    Factor, load_factor,
    # Functional API (WQ style) - tested and stable
    rank, ts_rank, ts_corr
)
from .data import fetch_data, check_data_quality
from .backtest import Backtester, backtest
from .utils import save_factor, load_saved_factor, factor_info

__all__ = [
    # Core factor class
    'Factor',
    'load_factor',
    
    # Data management
    'fetch_data',
    'check_data_quality',
    
    # Backtesting
    'Backtester',
    'backtest',
    
    # Functional API (WQ style) - tested and stable
    'rank', 'ts_rank', 'ts_corr',
    
    # Utilities
    'save_factor',
    'load_saved_factor',
    'factor_info'
]