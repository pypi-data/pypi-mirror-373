"""
Core factor computation engine for quantitative analysis.

Provides efficient factor matrix operations with pandas-like API.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, Callable
from scipy.stats import rankdata


class Factor:
    """
    Professional factor matrix for quantitative analysis.
    
    Standardized format: timestamp, symbol, factor columns.
    Supports method chaining and vectorized operations.
    """
    
    def __init__(self, data: Union[pd.DataFrame, str], name: Optional[str] = None):
        """
        Initialize factor matrix.
        
        Parameters
        ----------
        data : DataFrame or str
            Factor data or CSV path with [timestamp, symbol, factor] columns
        name : str, optional
            Factor name for identification
        """
        if isinstance(data, str):
            df = pd.read_csv(data, parse_dates=['timestamp'])
        else:
            df = data.copy()
            
        # Standardize column names
        if len(df.columns) == 3 and 'factor' not in df.columns:
            df.columns = ['timestamp', 'symbol', 'factor']
        elif 'factor' not in df.columns:
            factor_cols = [col for col in df.columns 
                          if col not in ['timestamp', 'symbol']]
            if not factor_cols:
                raise ValueError("No factor column found")
            df = df[['timestamp', 'symbol', factor_cols[0]]]
            df.columns = ['timestamp', 'symbol', 'factor']
            
        self.data = df[['timestamp', 'symbol', 'factor']].copy()
        self.data = self.data.sort_values(['timestamp', 'symbol'])
        self.name = name or 'factor'
    
    # Core operations
    def rank(self) -> 'Factor':
        """Cross-sectional rank within each timestamp."""
        result = self.data.copy()
        
        # 確保數據類型正確
        result['factor'] = pd.to_numeric(result['factor'], errors='coerce')
        
        # 檢查是否有有效數據
        if result['factor'].isna().all():
            raise ValueError("All factor values are NaN")
        
        # 分組計算排名，處理 NaN 值
        def safe_rank(group):
            try:
                # 只對非 NaN 值計算排名
                valid_mask = group.notna()
                if valid_mask.sum() == 0:
                    return group  # 如果全是 NaN，保持原樣
                
                ranked = group.copy()
                ranked[valid_mask] = group[valid_mask].rank(method='min', pct=True)
                return ranked
            except Exception as e:
                # 如果出錯，返回 NaN
                return pd.Series(np.nan, index=group.index)
        
        result['factor'] = (result.groupby('timestamp')['factor']
                           .transform(safe_rank))
        
        return Factor(result, f"rank({self.name})")
    
    def ts_rank(self, window: int) -> 'Factor':
        """Rolling time-series rank within window."""
        if window <= 0:
            raise ValueError("Window must be positive")
        
        def safe_ts_rank(x):
            try:
                # 確保有足夠的數據
                if len(x) < window:
                    return np.nan
                
                # 移除 NaN 值
                valid_values = x.dropna()
                if len(valid_values) == 0:
                    return np.nan
                
                # 計算當前值在窗口內的排名
                current_value = x.iloc[-1]
                if pd.isna(current_value):
                    return np.nan
                
                # 使用 scipy.stats.rankdata 計算排名
                ranks = rankdata(valid_values, method='min')
                
                # 找到當前值的排名位置
                current_rank = ranks[-1] if len(ranks) > 0 else np.nan
                
                # 轉換為百分位數 (0-1)
                return current_rank / len(ranks) if len(ranks) > 0 else np.nan
                
            except Exception as e:
                return np.nan
        
        result = self._apply_rolling(safe_ts_rank, window)
        return Factor(result, f"ts_rank({self.name},{window})")
    
    def ts_sum(self, window: int) -> 'Factor':
        """Rolling sum over window."""
        result = self._apply_rolling('sum', window)
        return Factor(result, f"ts_sum({self.name},{window})")
    
    def ts_mean(self, window: int) -> 'Factor':
        """Rolling mean over window."""
        result = self._apply_rolling('mean', window)
        return Factor(result, f"ts_mean({self.name},{window})")
    
    def ts_std(self, window: int) -> 'Factor':
        """Rolling standard deviation over window."""
        result = self._apply_rolling('std', window)
        return Factor(result, f"ts_std({self.name},{window})")
    
    def ts_min(self, window: int) -> 'Factor':
        """Rolling minimum over window."""
        result = self._apply_rolling('min', window)
        return Factor(result, f"ts_min({self.name},{window})")
    
    def ts_max(self, window: int) -> 'Factor':
        """Rolling maximum over window."""
        result = self._apply_rolling('max', window)
        return Factor(result, f"ts_max({self.name},{window})")
    
    def delta(self, periods: int = 1) -> 'Factor':
        """Difference with lagged values."""
        result = self._apply_groupby('diff', periods)
        return Factor(result, f"delta({self.name},{periods})")
    
    def delay(self, periods: int = 1) -> 'Factor':
        """Lag factor by periods."""
        result = self._apply_groupby('shift', periods)
        return Factor(result, f"delay({self.name},{periods})")
    
    def returns(self, periods: int = 1) -> 'Factor':
        """Percentage returns over periods."""
        result = self._apply_groupby('pct_change', periods)
        return Factor(result, f"returns({self.name},{periods})")
    
    # Math operations
    def add(self, other: Union['Factor', float]) -> 'Factor':
        """Addition with factor or scalar."""
        if isinstance(other, Factor):
            result = self._binary_op(other, lambda x, y: x + y)
            return Factor(result, f"({self.name}+{other.name})")
        else:
            result = self.data.copy()
            result['factor'] += other
            return Factor(result, f"({self.name}+{other})")
    
    def subtract(self, other: Union['Factor', float]) -> 'Factor':
        """Subtraction with factor or scalar."""
        if isinstance(other, Factor):
            result = self._binary_op(other, lambda x, y: x - y)
            return Factor(result, f"({self.name}-{other.name})")
        else:
            result = self.data.copy()
            result['factor'] -= other
            return Factor(result, f"({self.name}-{other})")
    
    def multiply(self, other: Union['Factor', float]) -> 'Factor':
        """Multiplication with factor or scalar."""
        if isinstance(other, Factor):
            result = self._binary_op(other, lambda x, y: x * y)
            return Factor(result, f"({self.name}*{other.name})")
        else:
            result = self.data.copy()
            result['factor'] *= other
            return Factor(result, f"({self.name}*{other})")
    
    def scale(self, k: float = 1.0) -> 'Factor':
        """Scale to sum of absolute values equals k."""
        result = self.data.copy()
        abs_sum = np.abs(result['factor']).sum()
        if abs_sum != 0:
            result['factor'] *= k / abs_sum
        return Factor(result, f"scale({self.name},{k})")
    
    # Python 運算符重載 - 讓因子表達式更直觀
    def __neg__(self) -> 'Factor':
        """Unary negation: -factor"""
        return self.multiply(-1)
    
    def __add__(self, other: Union['Factor', float]) -> 'Factor':
        """Addition: factor + other"""
        return self.add(other)
    
    def __radd__(self, other: Union['Factor', float]) -> 'Factor':
        """Right addition: other + factor"""
        return self.add(other)
    
    def __sub__(self, other: Union['Factor', float]) -> 'Factor':
        """Subtraction: factor - other"""
        return self.subtract(other)
    
    def __rsub__(self, other: Union['Factor', float]) -> 'Factor':
        """Right subtraction: other - factor"""
        if isinstance(other, Factor):
            return other.subtract(self)
        else:
            result = self.data.copy()
            result['factor'] = other - result['factor']
            return Factor(result, f"({other}-{self.name})")
    
    def __mul__(self, other: Union['Factor', float]) -> 'Factor':
        """Multiplication: factor * other"""
        return self.multiply(other)
    
    def __rmul__(self, other: Union['Factor', float]) -> 'Factor':
        """Right multiplication: other * factor"""
        return self.multiply(other)
    
    def __truediv__(self, other: Union['Factor', float]) -> 'Factor':
        """Division: factor / other"""
        if isinstance(other, Factor):
            result = self._binary_op(other, lambda x, y: x / y)
            return Factor(result, f"({self.name}/{other.name})")
        else:
            result = self.data.copy()
            result['factor'] /= other
            return Factor(result, f"({self.name}/{other})")
    
    def __rtruediv__(self, other: Union['Factor', float]) -> 'Factor':
        """Right division: other / factor"""
        if isinstance(other, Factor):
            return other.__truediv__(self)
        else:
            result = self.data.copy()
            result['factor'] = other / result['factor']
            return Factor(result, f"({other}/{self.name})")
    
    # Correlation
    def ts_corr(self, other: 'Factor', window: int) -> 'Factor':
        """
        Returns Pearson correlation of two factors for the past d days.
        
        Measures linear relationship between variables. Most effective when
        variables are normally distributed and relationship is linear.
        
        Parameters
        ----------
        other : Factor
            The other factor to correlate with
        window : int
            Number of periods for rolling correlation
            
        Returns
        -------
        Factor
            Rolling correlation values between -1 and 1
        """
        if window <= 0:
            raise ValueError("Window must be positive")
        
        if not isinstance(other, Factor):
            raise TypeError("Other must be a Factor object")
        
        # 合併兩個因子的數據
        try:
            merged = pd.merge(self.data, other.data, on=['timestamp', 'symbol'], 
                             suffixes=('_x', '_y'), how='inner')
        except Exception as e:
            raise ValueError(f"Failed to merge factor data: {e}")
        
        if merged.empty:
            raise ValueError("No common data between factors")
        
        merged = merged.sort_values(['symbol', 'timestamp'])
        
        # 分組計算滾動相關性
        result_data = []
        
        for symbol in merged['symbol'].unique():
            try:
                symbol_data = merged[merged['symbol'] == symbol].copy()
                symbol_data = symbol_data.sort_values('timestamp')
                
                # 確保數據類型正確
                x_values = pd.to_numeric(symbol_data['factor_x'], errors='coerce')
                y_values = pd.to_numeric(symbol_data['factor_y'], errors='coerce')
                
                # 計算滾動相關性
                corr_values = x_values.rolling(window, min_periods=window).corr(y_values)
                
                # 處理無效相關性值
                corr_values = corr_values.where(
                    (corr_values >= -1) & (corr_values <= 1), np.nan
                )
                
                # 添加到結果中
                symbol_data['factor'] = corr_values
                result_data.append(symbol_data[['timestamp', 'symbol', 'factor']])
                
            except Exception as e:
                # 如果出錯，添加 NaN 值
                symbol_data = merged[merged['symbol'] == symbol][['timestamp', 'symbol']].copy()
                symbol_data['factor'] = np.nan
                result_data.append(symbol_data)
        
        if result_data:
            merged = pd.concat(result_data, ignore_index=True)
        else:
            merged['factor'] = np.nan
        
        # 處理 NaN 值 - 保持 NaN 而不是填充為 0
        result = merged[['timestamp', 'symbol', 'factor']].copy()
        
        return Factor(result, f"ts_corr({self.name},{other.name},{window})")
    
    # 保持向後兼容性的別名
    def correlation(self, other: 'Factor', window: int) -> 'Factor':
        """Deprecated: Use ts_corr instead."""
        import warnings
        warnings.warn("correlation() is deprecated, use ts_corr() instead", 
                     DeprecationWarning, stacklevel=2)
        return self.ts_corr(other, window)
    
    # Utility methods
    def _apply_rolling(self, func: Union[str, Callable], window: int) -> pd.DataFrame:
        """Apply rolling function by symbol."""
        result = self.data.copy().sort_values(['symbol', 'timestamp'])
        if isinstance(func, str):
            result['factor'] = (result.groupby('symbol')['factor']
                               .rolling(window, min_periods=window)
                               .agg(func).values)
        else:
            result['factor'] = (result.groupby('symbol')['factor']
                               .rolling(window, min_periods=window)
                               .apply(func, raw=False).values)
        return result.sort_values(['timestamp', 'symbol'])
    
    def _apply_groupby(self, func: str, *args) -> pd.DataFrame:
        """Apply groupby function by symbol."""
        result = self.data.copy().sort_values(['symbol', 'timestamp'])
        result['factor'] = (result.groupby('symbol')['factor']
                           .transform(func, *args))
        return result.sort_values(['timestamp', 'symbol'])
    
    def _binary_op(self, other: 'Factor', op: Callable) -> pd.DataFrame:
        """Apply binary operation with another factor."""
        merged = pd.merge(self.data, other.data, on=['timestamp', 'symbol'], 
                         suffixes=('_x', '_y'))
        merged['factor'] = op(merged['factor_x'], merged['factor_y'])
        return merged[['timestamp', 'symbol', 'factor']]
    
    # Data access
    def to_csv(self, path: str) -> str:
        """Save to CSV file."""
        self.data.to_csv(path, index=False)
        return path
    
    def to_multiindex(self) -> pd.Series:
        """Convert to MultiIndex Series."""
        return self.data.set_index(['timestamp', 'symbol'])['factor']
    
    def info(self) -> dict:
        """Get factor information."""
        return {
            'name': self.name,
            'shape': self.data.shape,
            'time_range': (self.data['timestamp'].min(), self.data['timestamp'].max()),
            'symbols': sorted(self.data['symbol'].unique()),
            'valid_ratio': self.data['factor'].notna().mean()
        }
    
    def __repr__(self):
        n_obs = self.data.shape[0]
        n_symbols = len(self.data['symbol'].unique())
        valid_ratio = self.data['factor'].notna().mean()
        time_range = f"{self.data['timestamp'].min().strftime('%Y-%m-%d')} to {self.data['timestamp'].max().strftime('%Y-%m-%d')}"
        return (f"Factor(name={self.name}, obs={n_obs}, symbols={n_symbols}, "
               f"valid={valid_ratio:.1%}, period={time_range})")
    
    def __str__(self):
        """User-friendly string representation."""
        return f"Factor({self.name}): {self.data.shape[0]} obs, {len(self.data['symbol'].unique())} symbols"


# Factory functions
def load_factor(data: Union[str, pd.DataFrame], column: str, name: Optional[str] = None) -> Factor:
    """
    Load factor from data source.
    
    Parameters
    ----------
    data : str or DataFrame
        Data source (CSV path or DataFrame)
    column : str
        Column name to extract as factor
    name : str, optional
        Factor name
        
    Returns
    -------
    Factor
        Factor object with specified column
    """
    if isinstance(data, str):
        df = pd.read_csv(data, parse_dates=['timestamp'])
    else:
        df = data.copy()
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")
    
    factor_data = df[['timestamp', 'symbol', column]].copy()
    factor_data.columns = ['timestamp', 'symbol', 'factor']
    
    return Factor(factor_data, name or column)


# Functional API - WQ style operator functions (tested and stable)
def rank(factor: Factor) -> Factor:
    """Cross-sectional rank within each timestamp (functional style)."""
    return factor.rank()

def ts_rank(factor: Factor, window: int) -> Factor:
    """Rolling time-series rank within window (functional style)."""
    return factor.ts_rank(window)

def ts_corr(factor1: Factor, factor2: Factor, window: int) -> Factor:
    """Rolling correlation between two factors (functional style)."""
    return factor1.ts_corr(factor2, window)

# End of core Factor implementation
