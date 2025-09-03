"""
Pytest configuration and fixtures for timestrader-preprocessing tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing."""
    np.random.seed(42)  # Reproducible test data
    
    # Generate 1000 5-minute candles (about 3.5 days)
    start_time = datetime(2025, 1, 1, 9, 30)  # Market open
    timestamps = [start_time + timedelta(minutes=5*i) for i in range(1000)]
    
    # Generate realistic price data with trend and volatility
    base_price = 18000.0
    prices = []
    current_price = base_price
    
    for _ in range(1000):
        # Random walk with small drift
        change = np.random.normal(0, 10)  # $10 average move
        current_price += change
        
        # Ensure positive prices
        current_price = max(current_price, 1000.0)
        
        # Generate OHLC from this price
        open_price = current_price + np.random.normal(0, 2)
        close_price = current_price + np.random.normal(0, 2)
        high_price = max(open_price, close_price) + abs(np.random.normal(0, 5))
        low_price = min(open_price, close_price) - abs(np.random.normal(0, 5))
        volume = int(np.random.lognormal(8, 0.5))  # Realistic volume
        
        prices.append({
            'timestamp': timestamps[len(prices)],
            'open': round(open_price, 2),
            'high': round(high_price, 2), 
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
    
    return pd.DataFrame(prices)


@pytest.fixture  
def sample_csv_file(sample_ohlcv_data, tmp_path):
    """Create temporary CSV file with sample data."""
    csv_path = tmp_path / "test_data.csv"
    sample_ohlcv_data.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary configuration file."""
    config = {
        "processing": {
            "window_size": 288,
            "indicators": ["vwap", "rsi", "atr", "ema9", "ema21", "stoch"],
            "normalization_method": "zscore"
        },
        "validation": {
            "min_records": 100,
            "max_outlier_ratio": 0.05,
            "required_columns": ["timestamp", "open", "high", "low", "close", "volume"]
        }
    }
    
    config_path = tmp_path / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    return str(config_path)


@pytest.fixture
def mock_colab_environment(monkeypatch):
    """Mock Google Colab environment for testing."""
    import sys
    
    # Mock google.colab module
    class MockColab:
        pass
    
    sys.modules['google.colab'] = MockColab()
    
    # Cleanup after test
    yield
    
    if 'google.colab' in sys.modules:
        del sys.modules['google.colab']


@pytest.fixture
def performance_timer():
    """Timer fixture for performance tests."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


@pytest.fixture
def memory_monitor():
    """Memory monitoring fixture."""
    import psutil
    import os
    
    class MemoryMonitor:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.start_memory = None
            self.end_memory = None
        
        def start(self):
            self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        def stop(self):
            self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        @property
        def memory_used(self):
            if self.start_memory and self.end_memory:
                return self.end_memory - self.start_memory
            return None
    
    return MemoryMonitor()


# Pytest markers configuration (also in pyproject.toml)
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]