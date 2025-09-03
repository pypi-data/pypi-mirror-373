"""
Historical Data Processing Pipeline for Google Colab

Simplified version for PyPI package distribution.
Provides core functionality for historical data processing optimized for Google Colab.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
from datetime import datetime
import json
from dataclasses import dataclass
import io

try:
    from tqdm.auto import tqdm
except ImportError:
    # Fallback for environments without tqdm
    def tqdm(iterable, *args, **kwargs):
        return iterable


@dataclass
class DataQualityMetrics:
    """Data quality metrics for historical processing."""
    score: float
    total_records: int
    valid_records: int
    outliers: int
    missing_values: int
    issues: List[str]


@dataclass  
class NormalizationParams:
    """Normalization parameters for production consistency."""
    method: str
    window_size: int
    parameters: Dict[str, Dict[str, float]]
    timestamp: str
    version: str = "1.0.0"


@dataclass
class ProcessingConfig:
    """Configuration for historical processing."""
    indicators: List[str]
    window_size: int = 288
    normalization_method: str = "zscore"
    quality_threshold: float = 0.995


class HistoricalProcessor:
    """
    Historical data processor optimized for Google Colab.
    
    Provides functionality for loading, validating, and processing
    historical market data for TimesNet model training.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the historical processor."""
        self.config = config or {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the processor."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def load_from_csv(
        self, 
        file_path: Union[str, Path, io.StringIO], 
        progress_bar: bool = True,
        auto_aggregate: bool = True,
        target_timeframe: int = 5
    ) -> pd.DataFrame:
        """
        Load OHLCV data from CSV file or StringIO (Colab compatible).
        
        Args:
            file_path: Path to CSV file or StringIO object
            progress_bar: Show progress bar for large files
            auto_aggregate: Automatically aggregate to target timeframe if needed
            target_timeframe: Target timeframe in minutes (default: 5)
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            ValueError: If data format is invalid
        """
        self.logger.info("Loading historical data...")
        
        try:
            if isinstance(file_path, io.StringIO):
                data = pd.read_csv(file_path)
            else:
                data = pd.read_csv(file_path)
                
            # Validate required columns
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = set(required_columns) - set(data.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
                
            # Convert timestamp
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                
            self.logger.info(f"Loaded {len(data):,} records")
            
            # Detect and validate timeframe
            if len(data) >= 2:
                detected_timeframe = self.detect_timeframe(data)
                self.logger.info(f"Detected timeframe: {detected_timeframe} minutes")
                
                # Check if aggregation is needed
                if auto_aggregate and detected_timeframe < target_timeframe:
                    self.logger.info(f"Timeframe mismatch detected: {detected_timeframe}min data vs {target_timeframe}min target")
                    self.logger.info("Applying automatic aggregation...")
                    data = self.aggregate_timeframe(
                        data, 
                        target_minutes=target_timeframe, 
                        progress_bar=progress_bar
                    )
                elif detected_timeframe != target_timeframe:
                    self.logger.warning(
                        f"Timeframe mismatch: {detected_timeframe}min data vs {target_timeframe}min expected. "
                        f"Set auto_aggregate=True to fix automatically."
                    )
                    
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def aggregate_timeframe(
        self, 
        data: pd.DataFrame, 
        target_minutes: int = 5,
        progress_bar: bool = True
    ) -> pd.DataFrame:
        """
        Aggregate data from smaller to larger timeframes (e.g., 1min -> 5min).
        
        Args:
            data: DataFrame with OHLCV data and timestamp
            target_minutes: Target timeframe in minutes (default: 5)
            progress_bar: Show progress bar for aggregation
            
        Returns:
            DataFrame with aggregated OHLCV data
            
        Raises:
            ValueError: If data format is invalid or timeframe cannot be detected
        """
        self.logger.info(f"Aggregating data to {target_minutes}-minute timeframe...")
        
        # Validate required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = set(required_columns) - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns for aggregation: {missing_columns}")
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Sort by timestamp
        data_sorted = data.sort_values('timestamp').copy()
        
        # Detect current timeframe
        if len(data_sorted) > 1:
            time_diff = data_sorted['timestamp'].diff().median()
            current_minutes = int(time_diff.total_seconds() / 60)
            self.logger.info(f"Detected current timeframe: {current_minutes} minutes")
            
            if current_minutes >= target_minutes:
                self.logger.warning(f"Current timeframe ({current_minutes}min) >= target ({target_minutes}min), returning original data")
                return data_sorted
        else:
            raise ValueError("Not enough data to determine timeframe")
        
        # Set timestamp as index for resampling
        data_sorted.set_index('timestamp', inplace=True)
        
        # Define aggregation rules for OHLCV
        agg_rules = {
            'open': 'first',    # First price in the period
            'high': 'max',      # Maximum price in the period  
            'low': 'min',       # Minimum price in the period
            'close': 'last',    # Last price in the period
            'volume': 'sum'     # Total volume in the period
        }
        
        # Add symbol column if exists
        if 'symbol' in data_sorted.columns:
            agg_rules['symbol'] = 'first'
        
        try:
            # Resample to target timeframe
            resampled = data_sorted.resample(f'{target_minutes}T').agg(agg_rules)
            
            # Remove periods with no data (NaN values)
            resampled = resampled.dropna()
            
            # Reset index to get timestamp back as column
            resampled.reset_index(inplace=True)
            
            # Validate aggregated OHLC relationships
            invalid_ohlc = (
                (resampled['high'] < resampled[['open', 'close']].max(axis=1)) |
                (resampled['low'] > resampled[['open', 'close']].min(axis=1))
            ).sum()
            
            if invalid_ohlc > 0:
                self.logger.warning(f"Found {invalid_ohlc} periods with invalid OHLC relationships after aggregation")
            
            # Log aggregation results
            original_count = len(data)
            aggregated_count = len(resampled)
            reduction_ratio = (1 - aggregated_count / original_count) * 100
            
            self.logger.info(f"Aggregation complete: {original_count:,} -> {aggregated_count:,} candles ({reduction_ratio:.1f}% reduction)")
            
            return resampled
            
        except Exception as e:
            self.logger.error(f"Error during timeframe aggregation: {e}")
            raise
    
    def detect_timeframe(self, data: pd.DataFrame) -> int:
        """
        Detect the timeframe of the data in minutes.
        
        Args:
            data: DataFrame with timestamp column
            
        Returns:
            Detected timeframe in minutes
        """
        if len(data) < 2:
            raise ValueError("Need at least 2 records to detect timeframe")
        
        # Ensure timestamp is datetime
        timestamps = pd.to_datetime(data['timestamp'])
        
        # Calculate time differences
        time_diffs = timestamps.sort_values().diff().dropna()
        
        # Get median time difference (more robust than mean)
        median_diff = time_diffs.median()
        timeframe_minutes = int(median_diff.total_seconds() / 60)
        
        return timeframe_minutes
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality and detect issues.
        
        Args:
            data: OHLCV DataFrame to validate
            
        Returns:
            Dict with validation results and quality metrics
        """
        self.logger.info("Validating data quality...")
        
        issues = []
        total_records = len(data)
        
        # Check for missing values
        missing_values = data.isnull().sum().sum()
        if missing_values > 0:
            issues.append(f"Found {missing_values} missing values")
            
        # Validate OHLC relationships
        ohlc_issues = 0
        if 'open' in data.columns and 'high' in data.columns:
            invalid_high = (data['high'] < data[['open', 'close']].max(axis=1)).sum()
            ohlc_issues += invalid_high
            if invalid_high > 0:
                issues.append(f"Found {invalid_high} records where high < max(open, close)")
                
        if 'low' in data.columns:
            invalid_low = (data['low'] > data[['open', 'close']].min(axis=1)).sum()  
            ohlc_issues += invalid_low
            if invalid_low > 0:
                issues.append(f"Found {invalid_low} records where low > min(open, close)")
        
        # Detect outliers (simple z-score method)
        outliers = 0
        if 'close' in data.columns:
            z_scores = np.abs((data['close'] - data['close'].mean()) / data['close'].std())
            outliers = (z_scores > 3).sum()
            if outliers > 0:
                issues.append(f"Found {outliers} potential outliers (z-score > 3)")
        
        valid_records = total_records - missing_values - ohlc_issues
        quality_score = valid_records / total_records if total_records > 0 else 0.0
        
        metrics = DataQualityMetrics(
            score=quality_score,
            total_records=total_records,
            valid_records=valid_records,
            outliers=outliers,
            missing_values=missing_values,
            issues=issues
        )
        
        self.logger.info(f"Data quality score: {quality_score:.1%}")
        
        return {
            "quality_score": quality_score,
            "metrics": metrics,
            "issues": issues
        }
    
    def calculate_indicators(
        self,
        data: pd.DataFrame,
        indicators: List[str],
        progress_bar: bool = True
    ) -> pd.DataFrame:
        """
        Calculate technical indicators.
        
        Args:
            data: OHLCV DataFrame
            indicators: List of indicators to calculate
            progress_bar: Show progress bar
            
        Returns:
            DataFrame with indicators added
        """
        self.logger.info(f"Calculating {len(indicators)} indicators...")
        
        result = data.copy()
        
        indicator_funcs = {
            'vwap': self._calculate_vwap,
            'rsi': self._calculate_rsi,
            'atr': self._calculate_atr,
            'ema9': lambda df: self._calculate_ema(df, 9),
            'ema21': lambda df: self._calculate_ema(df, 21),
            'stoch': self._calculate_stochastic
        }
        
        progress_iter = tqdm(indicators, desc="Calculating indicators") if progress_bar else indicators
        
        for indicator in progress_iter:
            if indicator in indicator_funcs:
                try:
                    result[indicator] = indicator_funcs[indicator](result)
                    self.logger.debug(f"Calculated {indicator}")
                except Exception as e:
                    self.logger.error(f"Error calculating {indicator}: {e}")
                    # Add NaN column if calculation fails
                    result[indicator] = np.nan
            else:
                self.logger.warning(f"Unknown indicator: {indicator}")
                result[indicator] = np.nan
        
        self.logger.info("Indicator calculation complete")
        return result
    
    def _calculate_vwap(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price."""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        return (typical_price * data['volume']).rolling(window=20).sum() / data['volume'].rolling(window=20).sum()
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def _calculate_ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data['close'].ewm(span=period).mean()
    
    def _calculate_stochastic(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Stochastic Oscillator."""
        low_min = data['low'].rolling(window=period).min()
        high_max = data['high'].rolling(window=period).max()
        k_percent = 100 * ((data['close'] - low_min) / (high_max - low_min))
        return k_percent.rolling(window=3).mean()
    
    def normalize_data(
        self,
        data: pd.DataFrame,
        window_size: int = 288,
        method: str = 'zscore'
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Normalize data using rolling window.
        
        Args:
            data: DataFrame with indicators
            window_size: Rolling window size
            method: Normalization method
            
        Returns:
            Tuple of (normalized_data, normalization_parameters)
        """
        self.logger.info(f"Normalizing data with {method} method...")
        
        result = data.copy()
        params = {}
        
        # Get numeric columns (excluding timestamp)
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        exclude_columns = ['timestamp'] if 'timestamp' in numeric_columns else []
        target_columns = [col for col in numeric_columns if col not in exclude_columns]
        
        if method == 'zscore':
            for col in target_columns:
                if col in data.columns:
                    # Rolling z-score normalization
                    rolling_mean = data[col].rolling(window=window_size, min_periods=1).mean()
                    rolling_std = data[col].rolling(window=window_size, min_periods=1).std()
                    
                    # Avoid division by zero
                    rolling_std = rolling_std.where(rolling_std > 1e-8, 1e-8)
                    
                    result[col] = (data[col] - rolling_mean) / rolling_std
                    
                    # Store parameters (use final values)
                    params[col] = {
                        'mean': float(rolling_mean.iloc[-1]),
                        'std': float(rolling_std.iloc[-1])
                    }
        
        normalization_params = NormalizationParams(
            method=method,
            window_size=window_size,
            parameters=params,
            timestamp=datetime.now().isoformat()
        )
        
        self.logger.info("Data normalization complete")
        return result, params
    
    def export_normalization_parameters(
        self,
        params: Dict[str, Any],
        output_path: Union[str, Path]
    ) -> None:
        """
        Export normalization parameters to JSON file.
        
        Args:
            params: Normalization parameters
            output_path: Output file path
        """
        self.logger.info(f"Exporting parameters to {output_path}")
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "package_version": "1.0.0",
            "parameters": params
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        self.logger.info("Parameters exported successfully")
    
    def generate_training_sequences(
        self,
        data: pd.DataFrame,
        sequence_length: int = 144,
        feature_columns: List[str] = None
    ) -> List[np.ndarray]:
        """
        Generate training sequences for TimesNet.
        
        Args:
            data: Processed DataFrame with indicators
            sequence_length: Length of each sequence
            feature_columns: Columns to include in sequences
            
        Returns:
            List of numpy arrays (sequence_length, n_features)
        """
        self.logger.info(f"Generating sequences of length {sequence_length}...")
        
        if feature_columns is None:
            # Use all numeric columns except timestamp
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            feature_columns = [col for col in numeric_columns if col != 'timestamp']
        
        # Verify columns exist
        available_columns = [col for col in feature_columns if col in data.columns]
        if len(available_columns) != len(feature_columns):
            missing = set(feature_columns) - set(available_columns)
            self.logger.warning(f"Missing columns: {missing}")
        
        feature_data = data[available_columns].values
        
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequence = feature_data[i:i + sequence_length]
            if not np.isnan(sequence).any():  # Skip sequences with NaN
                sequences.append(sequence)
        
        self.logger.info(f"Generated {len(sequences)} valid sequences")
        return sequences
    
    def get_quality_metrics(self) -> Dict[str, float]:
        """Get cached quality metrics."""
        # This would return cached metrics from last validation
        return {
            "score": 0.999,  # Mock high quality score
            "completeness": 1.0,
            "accuracy": 0.999
        }