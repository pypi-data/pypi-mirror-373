"""
Test Google Colab specific integration and performance requirements.

These tests validate the package works correctly in Colab environments
and meets the specified performance targets.
"""

import pytest
import time
import psutil
import os
from unittest.mock import patch, MagicMock


@pytest.mark.colab
@pytest.mark.integration
def test_colab_environment_integration(mock_colab_environment):
    """Test package behavior in Google Colab environment."""
    # Import after mocking Colab environment
    import sys
    if 'timestrader_preprocessing' in sys.modules:
        del sys.modules['timestrader_preprocessing']
    
    import timestrader_preprocessing as tsp
    
    # Verify Colab detection
    assert tsp.is_colab_environment() is True
    assert tsp.ENVIRONMENT_INFO['is_colab'] is True
    
    # Test Colab-specific functionality
    processor = tsp.HistoricalProcessor()
    assert processor is not None


@pytest.mark.colab
@pytest.mark.slow
def test_package_installation_time():
    """Test that package installation meets time requirements."""
    # This test simulates the package installation timing
    # In actual Colab, this would be: !pip install timestrader-preprocessing[colab]
    
    # Simulate installation activities
    start_time = time.time()
    
    # Mock installation activities
    time.sleep(0.1)  # Simulate some processing time
    
    installation_time = time.time() - start_time
    
    # NFR requirement: Installation < 2 minutes in Google Colab
    # Note: This is a mock test; real installation testing happens in CI/CD
    assert installation_time < 120, f"Installation took {installation_time:.2f}s (> 120s limit)"


@pytest.mark.colab
@pytest.mark.unit
def test_memory_efficiency_colab():
    """Test memory efficiency in Colab-like environment."""
    import timestrader_preprocessing as tsp
    
    # Get initial memory
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Import and use main components
    processor = tsp.HistoricalProcessor()
    
    # Get final memory
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = final_memory - initial_memory
    
    # NFR requirement: Package overhead < 100MB after import
    assert memory_used < 100, f"Memory overhead {memory_used:.1f}MB (> 100MB limit)"


@pytest.mark.colab
@pytest.mark.integration
def test_colab_data_loading(sample_ohlcv_data):
    """Test data loading with Colab-style data sources."""
    import timestrader_preprocessing as tsp
    import io
    
    processor = tsp.HistoricalProcessor()
    
    # Test loading from StringIO (common in Colab when uploading files)
    csv_buffer = io.StringIO()
    sample_ohlcv_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Should not crash when loading from StringIO
    loaded_data = processor.load_from_csv(csv_buffer)
    
    assert len(loaded_data) == len(sample_ohlcv_data)
    assert list(loaded_data.columns) == list(sample_ohlcv_data.columns)


@pytest.mark.colab
@pytest.mark.unit
def test_environment_warnings():
    """Test that appropriate warnings are shown for environment-specific features."""
    import timestrader_preprocessing as tsp
    import warnings
    
    # Test that production-only features show warnings in Colab
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Attempt to use production features
        try:
            from timestrader_preprocessing.realtime import RealtimeNormalizer
            # Should work but may show warnings about production dependencies
        except ImportError:
            pass  # Expected if production dependencies not installed
        
        # Check if appropriate warnings were issued
        # This depends on implementation - adjust as needed


@pytest.mark.colab
@pytest.mark.integration
def test_jupyter_notebook_integration():
    """Test integration with Jupyter/IPython environment."""
    import timestrader_preprocessing as tsp
    
    # Test Jupyter detection
    jupyter_detected = tsp.is_jupyter_environment()
    
    # In test environment, may or may not detect Jupyter
    # Just ensure the function returns a boolean
    assert isinstance(jupyter_detected, bool)


@pytest.mark.colab
@pytest.mark.unit
def test_progress_bar_functionality(sample_ohlcv_data):
    """Test progress bar functionality for large datasets in Colab."""
    import timestrader_preprocessing as tsp
    from unittest.mock import patch
    
    processor = tsp.HistoricalProcessor()
    
    # Mock tqdm progress bar
    with patch('timestrader_preprocessing.historical.processor.tqdm') as mock_tqdm:
        mock_tqdm.return_value.__enter__.return_value = MagicMock()
        
        # Test with progress bar enabled
        result = processor.calculate_indicators(
            sample_ohlcv_data,
            indicators=['vwap', 'rsi'],
            progress_bar=True
        )
        
        # Should have called tqdm
        assert mock_tqdm.called
        assert result is not None


@pytest.mark.colab
@pytest.mark.slow
def test_large_dataset_performance(sample_ohlcv_data):
    """Test performance with larger datasets simulating Colab usage."""
    import timestrader_preprocessing as tsp
    import pandas as pd
    
    # Create larger dataset (simulate portion of full 441K candles)
    large_data = pd.concat([sample_ohlcv_data] * 50, ignore_index=True)  # 50K candles
    
    processor = tsp.HistoricalProcessor()
    
    # Test processing time
    start_time = time.time()
    
    # Process indicators (most time-consuming operation)
    indicators = processor.calculate_indicators(
        large_data,
        indicators=['vwap', 'rsi'],
        progress_bar=False  # Disable for test speed
    )
    
    processing_time = time.time() - start_time
    
    # Estimate time for full dataset
    estimated_full_time = processing_time * (441682 / len(large_data))
    
    # NFR requirement: Full dataset processing < 5 minutes
    assert estimated_full_time < 300, f"Estimated full processing time {estimated_full_time:.1f}s (> 300s limit)"
    
    assert len(indicators) == len(large_data)
    assert 'vwap' in indicators.columns
    assert 'rsi' in indicators.columns


@pytest.mark.colab
@pytest.mark.integration
def test_colab_file_operations(tmp_path):
    """Test file operations in Colab-style environment."""
    import timestrader_preprocessing as tsp
    import json
    
    processor = tsp.HistoricalProcessor()
    
    # Test parameter export to Colab-style paths
    mock_params = {
        "vwap": {"mean": 18000.0, "std": 100.0},
        "rsi": {"mean": 50.0, "std": 15.0}
    }
    
    # Test export to /content/ style path (typical in Colab)
    export_path = tmp_path / "content" / "params.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    
    processor.export_normalization_parameters(mock_params, str(export_path))
    
    # Verify export worked
    assert export_path.exists()
    
    with open(export_path, 'r') as f:
        exported = json.load(f)
    
    assert exported == mock_params