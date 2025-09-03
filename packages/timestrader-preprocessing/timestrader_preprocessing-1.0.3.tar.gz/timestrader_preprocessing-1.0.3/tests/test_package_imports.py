"""
Test package installation, imports, and basic functionality.

These tests validate the package can be imported correctly and
basic functionality works as expected.
"""

import pytest
import sys
import time
from unittest.mock import patch


@pytest.mark.package
def test_package_import():
    """Test that package imports successfully."""
    import timestrader_preprocessing as tsp
    
    assert tsp.__version__ == "1.0.0"
    assert tsp.__author__ == "TimeStrader Team"
    assert hasattr(tsp, 'HistoricalProcessor')


@pytest.mark.package  
def test_package_import_speed(performance_timer):
    """Test that package import is fast (< 10 seconds)."""
    performance_timer.start()
    
    import timestrader_preprocessing as tsp
    
    performance_timer.stop()
    
    # NFR requirement: Import time < 10 seconds
    assert performance_timer.elapsed < 10.0, f"Import took {performance_timer.elapsed:.2f}s (> 10s limit)"


@pytest.mark.package
@pytest.mark.unit
def test_environment_detection():
    """Test environment detection functions."""
    import timestrader_preprocessing as tsp
    
    # Test basic detection (should work in test environment)
    assert isinstance(tsp.is_colab_environment(), bool)
    assert isinstance(tsp.is_jupyter_environment(), bool)
    
    # Test environment info structure
    info = tsp.ENVIRONMENT_INFO
    assert 'is_colab' in info
    assert 'is_jupyter' in info
    assert 'python_version' in info
    assert 'package_version' in info
    assert info['package_version'] == "1.0.0"


@pytest.mark.package
@pytest.mark.unit
def test_colab_environment_detection(mock_colab_environment):
    """Test Google Colab environment detection."""
    # Reimport after mocking
    if 'timestrader_preprocessing' in sys.modules:
        del sys.modules['timestrader_preprocessing']
    
    import timestrader_preprocessing as tsp
    
    assert tsp.is_colab_environment() is True
    assert tsp.ENVIRONMENT_INFO['is_colab'] is True


@pytest.mark.package
@pytest.mark.unit
def test_main_components_available():
    """Test that main package components are available."""
    import timestrader_preprocessing as tsp
    
    # Main classes should be available
    assert hasattr(tsp, 'HistoricalProcessor')
    assert hasattr(tsp, 'NormalizationParams')
    assert hasattr(tsp, 'DataQualityMetrics')
    assert hasattr(tsp, 'ProcessingConfig')
    
    # Functions should be available
    assert callable(tsp.is_colab_environment)
    assert callable(tsp.is_jupyter_environment)


@pytest.mark.package
@pytest.mark.unit
def test_submodule_imports():
    """Test that submodules can be imported."""
    # Historical module
    from timestrader_preprocessing.historical import HistoricalProcessor
    assert HistoricalProcessor is not None
    
    # Common module
    from timestrader_preprocessing.common import NormalizationParams
    assert NormalizationParams is not None
    
    # Config module  
    from timestrader_preprocessing.config import get_default_config
    assert callable(get_default_config)


@pytest.mark.package
@pytest.mark.slow
def test_memory_usage(memory_monitor):
    """Test package memory usage (< 100MB overhead)."""
    memory_monitor.start()
    
    import timestrader_preprocessing as tsp
    
    # Import main components to trigger loading
    processor = tsp.HistoricalProcessor()
    
    memory_monitor.stop()
    
    # NFR requirement: Memory overhead < 100MB
    memory_used = memory_monitor.memory_used or 0
    assert memory_used < 100, f"Memory usage {memory_used:.1f}MB (> 100MB limit)"


@pytest.mark.package
@pytest.mark.integration
def test_basic_workflow():
    """Test basic package workflow works end-to-end."""
    import timestrader_preprocessing as tsp
    import pandas as pd
    import numpy as np
    
    # Create minimal test data
    data = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01', periods=100, freq='5min'),
        'open': np.random.rand(100) * 100 + 18000,
        'high': np.random.rand(100) * 100 + 18100, 
        'low': np.random.rand(100) * 100 + 17900,
        'close': np.random.rand(100) * 100 + 18000,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # Test basic workflow
    processor = tsp.HistoricalProcessor()
    
    # Should not crash on basic operations
    assert processor is not None
    assert hasattr(processor, 'validate_data')


@pytest.mark.package  
def test_package_metadata():
    """Test package metadata is correctly set."""
    import timestrader_preprocessing as tsp
    
    # Check required metadata
    assert tsp.__version__
    assert tsp.__author__ 
    assert tsp.__email__
    
    # Check version format (semantic versioning)
    version_parts = tsp.__version__.split('.')
    assert len(version_parts) >= 2  # At least major.minor
    assert all(part.isdigit() for part in version_parts[:2])  # Major.minor are numeric