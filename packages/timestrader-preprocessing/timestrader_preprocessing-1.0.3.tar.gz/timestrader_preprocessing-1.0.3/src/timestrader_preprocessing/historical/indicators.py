"""
Technical Indicators Implementation for TimeStrader
Optimized for Google Colab environment with vectorized operations.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging
import warnings

# Optional numba import for performance optimization
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    # Fallback: create dummy decorators if numba not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
    
    prange = range
    NUMBA_AVAILABLE = False

warnings.filterwarnings('ignore')


class TechnicalIndicators:
    """
    Vectorized technical indicators implementation optimized for large datasets.
    All calculations validated against standard reference implementations.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with OHLCV data.
        
        Args:
            data: DataFrame with columns [timestamp, open, high, low, close, volume]
        """
        self.data = data.copy()
        self.logger = self._setup_logger()
        self._validate_data()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger("TechnicalIndicators")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _validate_data(self):
        """Validate input data structure."""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = set(required_cols) - set(self.data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    def calculate_vwap(self) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).
        
        Formula: VWAP = Σ(Price × Volume) / Σ(Volume)
        Where Price = (High + Low + Close) / 3
        
        Returns:
            Series with VWAP values
        """
        typical_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        volume = self.data['volume']
        
        # Cumulative VWAP calculation
        cum_price_volume = (typical_price * volume).cumsum()
        cum_volume = volume.cumsum()
        
        # Avoid division by zero
        vwap = cum_price_volume / cum_volume.replace(0, np.nan)
        
        self.logger.debug(f"VWAP calculated: min={vwap.min():.2f}, max={vwap.max():.2f}")
        return vwap
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Formula: RSI = 100 - (100 / (1 + RS))
        Where RS = Average Gain / Average Loss
        
        Args:
            period: RSI period (default: 14)
            
        Returns:
            Series with RSI values
        """
        close_prices = self.data['close']
        delta = close_prices.diff()
        
        gains = delta.where(delta > 0, 0)
        losses = (-delta).where(delta < 0, 0)
        
        # Use Wilder's smoothing method (exponential moving average with alpha = 1/period)
        alpha = 1.0 / period
        avg_gains = gains.ewm(alpha=alpha, adjust=False).mean()
        avg_losses = losses.ewm(alpha=alpha, adjust=False).mean()
        
        rs = avg_gains / avg_losses.replace(0, np.inf)
        rsi = 100 - (100 / (1 + rs))
        
        # Handle edge cases
        rsi = rsi.fillna(50)  # Neutral RSI for first values
        rsi = rsi.clip(0, 100)  # Ensure RSI stays in valid range
        
        self.logger.debug(f"RSI({period}) calculated: min={rsi.min():.2f}, max={rsi.max():.2f}")
        return rsi
    
    def calculate_atr(self, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
        ATR = EMA of True Range
        
        Args:
            period: ATR period (default: 14)
            
        Returns:
            Series with ATR values
        """
        high = self.data['high']
        low = self.data['low']
        close = self.data['close']
        prev_close = close.shift(1)
        
        # Calculate True Range components
        tr1 = high - low
        tr2 = np.abs(high - prev_close)
        tr3 = np.abs(low - prev_close)
        
        # True Range is the maximum of the three components
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR is Wilder's smoothed average of True Range
        alpha = 1.0 / period
        atr = true_range.ewm(alpha=alpha, adjust=False).mean()
        
        # Handle first value
        atr.iloc[0] = true_range.iloc[0]
        
        self.logger.debug(f"ATR({period}) calculated: min={atr.min():.2f}, max={atr.max():.2f}")
        return atr
    
    def calculate_ema(self, period: int, price_column: str = 'close') -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).
        
        Formula: EMA = (Close - EMA_prev) × (2/(period+1)) + EMA_prev
        
        Args:
            period: EMA period
            price_column: Column to calculate EMA on (default: 'close')
            
        Returns:
            Series with EMA values
        """
        prices = self.data[price_column]
        alpha = 2.0 / (period + 1)
        ema = prices.ewm(alpha=alpha, adjust=False).mean()
        
        self.logger.debug(f"EMA({period}) calculated: min={ema.min():.2f}, max={ema.max():.2f}")
        return ema
    
    def calculate_stochastic(
        self, 
        k_period: int = 14, 
        d_period: int = 3, 
        smooth_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator (%K and %D).
        
        Formula:
        %K = ((Close - Lowest Low) / (Highest High - Lowest Low)) × 100
        %D = SMA of %K
        
        Args:
            k_period: Period for %K calculation (default: 14)
            d_period: Period for %D smoothing (default: 3)
            smooth_period: Period for %K smoothing (default: 3)
            
        Returns:
            Tuple of (smoothed %K, %D) Series
        """
        high = self.data['high']
        low = self.data['low']
        close = self.data['close']
        
        # Calculate rolling highest high and lowest low
        highest_high = high.rolling(window=k_period).max()
        lowest_low = low.rolling(window=k_period).min()
        
        # Calculate raw %K
        k_raw = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Smooth %K
        k_smoothed = k_raw.rolling(window=smooth_period).mean()
        
        # Calculate %D
        d = k_smoothed.rolling(window=d_period).mean()
        
        # Handle edge cases
        k_smoothed = k_smoothed.fillna(50).clip(0, 100)
        d = d.fillna(50).clip(0, 100)
        
        self.logger.debug(f"Stochastic({k_period},{d_period},{smooth_period}) calculated")
        return k_smoothed, d
    
    def calculate_all_indicators(self) -> pd.DataFrame:
        """
        Calculate all technical indicators and return as DataFrame.
        
        Returns:
            DataFrame with all technical indicators
        """
        self.logger.info("Calculating all technical indicators...")
        
        result_df = self.data.copy()
        
        # Calculate indicators
        result_df['vwap'] = self.calculate_vwap()
        result_df['rsi'] = self.calculate_rsi(period=14)
        result_df['atr'] = self.calculate_atr(period=14)
        result_df['ema9'] = self.calculate_ema(period=9)
        result_df['ema21'] = self.calculate_ema(period=21)
        
        # Stochastic returns tuple, use %K (first element)
        stoch_k, stoch_d = self.calculate_stochastic()
        result_df['stochastic'] = stoch_k
        result_df['stochastic_d'] = stoch_d  # Keep %D for reference
        
        # Log statistics
        indicators = ['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stochastic']
        for indicator in indicators:
            values = result_df[indicator].dropna()
            self.logger.info(
                f"{indicator.upper()}: "
                f"mean={values.mean():.2f}, "
                f"std={values.std():.2f}, "
                f"min={values.min():.2f}, "
                f"max={values.max():.2f}"
            )
        
        return result_df
    
    def validate_against_reference(self, reference_data: Dict[str, pd.Series]) -> Dict[str, bool]:
        """
        Validate calculated indicators against reference implementations.
        
        Args:
            reference_data: Dictionary with reference indicator values
            
        Returns:
            Dictionary with validation results for each indicator
        """
        current_indicators = self.calculate_all_indicators()
        validation_results = {}
        tolerance = 1e-6  # Tolerance for floating point comparison
        
        for indicator_name, reference_values in reference_data.items():
            if indicator_name in current_indicators.columns:
                current_values = current_indicators[indicator_name].dropna()
                
                # Align series for comparison
                min_length = min(len(current_values), len(reference_values))
                current_subset = current_values.iloc[-min_length:]
                reference_subset = reference_values.iloc[-min_length:]
                
                # Calculate relative difference
                relative_diff = np.abs(
                    (current_subset - reference_subset) / reference_subset
                ).fillna(0)
                
                # Check if differences are within tolerance
                is_valid = (relative_diff < tolerance).all()
                validation_results[indicator_name] = is_valid
                
                if not is_valid:
                    max_diff = relative_diff.max()
                    self.logger.warning(
                        f"{indicator_name} validation failed: max relative diff = {max_diff:.2e}"
                    )
                else:
                    self.logger.info(f"{indicator_name} validation passed")
            else:
                validation_results[indicator_name] = False
                self.logger.error(f"{indicator_name} not found in calculated indicators")
        
        return validation_results
    
    def get_indicators_for_training(self) -> np.ndarray:
        """
        Get indicators formatted for TimesNet training (6 indicators only).
        
        Returns:
            NumPy array with shape (n_samples, 6) containing:
            [VWAP, RSI, ATR, EMA9, EMA21, Stochastic]
        """
        indicators_df = self.calculate_all_indicators()
        
        # Select the 6 required indicators in correct order
        training_columns = ['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stochastic']
        training_data = indicators_df[training_columns].values
        
        # Remove rows with NaN values
        mask = ~np.isnan(training_data).any(axis=1)
        training_data = training_data[mask]
        
        self.logger.info(f"Training data shape: {training_data.shape}")
        return training_data


@jit(nopython=True, parallel=True)
def _fast_rolling_calculation(values: np.ndarray, window: int, operation: str) -> np.ndarray:
    """
    Fast rolling calculations using Numba JIT compilation.
    
    Args:
        values: Input array
        window: Rolling window size
        operation: Operation type ('mean', 'min', 'max', 'std')
        
    Returns:
        Array with rolling calculations
    """
    n = len(values)
    result = np.full(n, np.nan)
    
    for i in prange(window - 1, n):
        window_values = values[i - window + 1:i + 1]
        
        if operation == 'mean':
            result[i] = np.mean(window_values)
        elif operation == 'min':
            result[i] = np.min(window_values)
        elif operation == 'max':
            result[i] = np.max(window_values)
        elif operation == 'std':
            result[i] = np.std(window_values)
    
    return result


class OptimizedIndicators:
    """
    High-performance technical indicators using Numba JIT compilation.
    Use for very large datasets where performance is critical.
    """
    
    @staticmethod
    @jit(nopython=True)
    def fast_ema(prices: np.ndarray, period: int) -> np.ndarray:
        """
        Fast EMA calculation using Numba JIT.
        
        Args:
            prices: Price array
            period: EMA period
            
        Returns:
            EMA array
        """
        alpha = 2.0 / (period + 1)
        ema = np.full_like(prices, np.nan)
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i - 1]
        
        return ema
    
    @staticmethod
    @jit(nopython=True)
    def fast_rsi(prices: np.ndarray, period: int) -> np.ndarray:
        """
        Fast RSI calculation using Numba JIT.
        
        Args:
            prices: Price array
            period: RSI period
            
        Returns:
            RSI array
        """
        n = len(prices)
        rsi = np.full(n, np.nan)
        gains = np.zeros(n)
        losses = np.zeros(n)
        
        # Calculate price changes
        for i in range(1, n):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains[i] = change
            else:
                losses[i] = -change
        
        # Calculate RSI
        alpha = 1.0 / period
        avg_gain = 0.0
        avg_loss = 0.0
        
        for i in range(period, n):
            if i == period:
                # Initial calculation
                avg_gain = np.mean(gains[1:i + 1])
                avg_loss = np.mean(losses[1:i + 1])
            else:
                # Wilder's smoothing
                avg_gain = alpha * gains[i] + (1 - alpha) * avg_gain
                avg_loss = alpha * losses[i] + (1 - alpha) * avg_loss
            
            if avg_loss == 0:
                rsi[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))
        
        return rsi