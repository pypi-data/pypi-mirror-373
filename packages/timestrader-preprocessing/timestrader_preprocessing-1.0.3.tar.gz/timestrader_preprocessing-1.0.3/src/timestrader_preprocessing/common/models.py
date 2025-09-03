"""
Common data models and classes for timestrader-preprocessing package.

Provides shared data structures used across historical and real-time processing.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np


@dataclass
class MarketDataRecord:
    """Single market data record (OHLCV)."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def validate(self) -> List[str]:
        """Validate the record and return list of issues."""
        issues = []
        
        if self.high < max(self.open, self.close):
            issues.append("High price less than max(open, close)")
            
        if self.low > min(self.open, self.close):
            issues.append("Low price greater than min(open, close)")
            
        if self.volume < 0:
            issues.append("Negative volume")
            
        return issues


@dataclass
class DataQualityMetrics:
    """Data quality metrics for validation results."""
    score: float
    total_records: int
    valid_records: int
    outliers: int
    missing_values: int
    issues: List[str]
    
    def is_acceptable(self, threshold: float = 0.995) -> bool:
        """Check if quality meets acceptance threshold."""
        return self.score >= threshold


@dataclass  
class NormalizationParams:
    """Normalization parameters for production consistency."""
    method: str
    window_size: int
    parameters: Dict[str, Dict[str, float]]
    timestamp: str
    version: str = "1.0.0"
    
    def get_parameter(self, column: str) -> Optional[Dict[str, float]]:
        """Get normalization parameters for a specific column."""
        return self.parameters.get(column)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "method": self.method,
            "window_size": self.window_size,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "version": self.version
        }


@dataclass
class ProcessingConfig:
    """Configuration for data processing operations."""
    indicators: List[str]
    window_size: int = 288
    normalization_method: str = "zscore"
    quality_threshold: float = 0.995
    
    @classmethod
    def colab_default(cls) -> 'ProcessingConfig':
        """Get default configuration optimized for Google Colab."""
        return cls(
            indicators=['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stoch'],
            window_size=288,  # 24 hours of 5-min candles
            normalization_method="zscore",
            quality_threshold=0.995
        )
    
    @classmethod
    def production_default(cls) -> 'ProcessingConfig':
        """Get default configuration for production environment."""
        return cls(
            indicators=['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stoch'],
            window_size=288,
            normalization_method="zscore",
            quality_threshold=0.999  # Higher threshold for production
        )


class DataValidator:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_ohlcv_dataframe(data: pd.DataFrame) -> DataQualityMetrics:
        """Validate OHLCV DataFrame and return quality metrics."""
        issues = []
        total_records = len(data)
        
        # Check required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = set(required_columns) - set(data.columns)
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")
        
        # Count missing values
        missing_values = data.isnull().sum().sum()
        if missing_values > 0:
            issues.append(f"Found {missing_values} missing values")
        
        # Validate OHLC relationships
        ohlc_issues = 0
        if all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            invalid_high = (data['high'] < data[['open', 'close']].max(axis=1)).sum()
            invalid_low = (data['low'] > data[['open', 'close']].min(axis=1)).sum()
            ohlc_issues = invalid_high + invalid_low
            
            if invalid_high > 0:
                issues.append(f"Found {invalid_high} records with invalid high prices")
            if invalid_low > 0:
                issues.append(f"Found {invalid_low} records with invalid low prices")
        
        # Detect outliers
        outliers = 0
        if 'close' in data.columns:
            z_scores = np.abs((data['close'] - data['close'].mean()) / data['close'].std())
            outliers = (z_scores > 3).sum()
            if outliers > 0:
                issues.append(f"Found {outliers} potential outliers (z-score > 3)")
        
        valid_records = total_records - missing_values - ohlc_issues
        quality_score = valid_records / total_records if total_records > 0 else 0.0
        
        return DataQualityMetrics(
            score=quality_score,
            total_records=total_records,
            valid_records=valid_records,
            outliers=outliers,
            missing_values=missing_values,
            issues=issues
        )
    
    @staticmethod
    def validate_indicators_dataframe(data: pd.DataFrame, required_indicators: List[str] = None) -> bool:
        """Validate that DataFrame contains required indicators."""
        if required_indicators is None:
            return True
            
        missing_indicators = set(required_indicators) - set(data.columns)
        return len(missing_indicators) == 0


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    
    def __init__(self, message: str, quality_metrics: Optional[DataQualityMetrics] = None):
        super().__init__(message)
        self.quality_metrics = quality_metrics