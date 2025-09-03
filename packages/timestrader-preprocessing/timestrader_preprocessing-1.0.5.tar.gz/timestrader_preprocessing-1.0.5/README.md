# TimeStrader Preprocessing

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/timestrader-preprocessing.svg)](https://badge.fury.io/py/timestrader-preprocessing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pip-installable package providing TimeStrader data processing capabilities optimized for Google Colab training and retraining workflows.

## 🚀 Quick Start

### Installation

#### For Google Colab (Recommended)
```bash
pip install timestrader-preprocessing[colab]
```

#### Basic Installation
```bash
pip install timestrader-preprocessing
```

#### Production Environment
```bash
pip install timestrader-preprocessing[production]
```

### Basic Usage

> **⚠️ Important**: As of v1.0.3, the API has been simplified for better Google Colab compatibility. Use `HistoricalProcessor` as the main entry point.

```python
import timestrader_preprocessing as tsp

# Check environment
print(f"Running in Colab: {tsp.is_colab_environment()}")
print(f"Environment info: {tsp.ENVIRONMENT_INFO}")

# Load and process historical data
processor = tsp.HistoricalProcessor()
data = processor.load_from_csv("mnq_historical.csv")
indicators = processor.calculate_indicators(data)
normalized, params = processor.normalize_data(indicators)

print(f"Processed {len(data)} candles")
print(f"Data quality: {processor.get_quality_metrics()}")
```

## 🔄 Version 1.0.3 Updates

### API Simplification
The package API has been streamlined for better Google Colab compatibility:

```python
# ✅ Correct Usage (v1.0.3+)
from timestrader_preprocessing import HistoricalProcessor

processor = HistoricalProcessor()

# Step-by-step processing
validation_results = processor.validate_data(raw_data)
indicators_data = processor.calculate_indicators(raw_data, indicators=['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stoch'])
normalized_data, params = processor.normalize_data(indicators_data, window_size=288, method='zscore')
sequences = processor.generate_training_sequences(normalized_data, sequence_length=144)
```

### Deprecated Usage
```python
# ❌ No longer available (caused import errors in Colab)
from timestrader_preprocessing import UnifiedDataProcessor, TechnicalIndicators
from timestrader_preprocessing.core.config import ProcessingMode
from timestrader_preprocessing.core.data_structures import MarketData
```

### Method Changes
| Old Method (v1.0.0-1.0.2) | New Method (v1.0.3+) | Status |
|---------------------------|----------------------|---------|
| `UnifiedDataProcessor()` | `HistoricalProcessor()` | ✅ Simplified |
| `process_historical_data()` | `calculate_indicators()` + `normalize_data()` | ✅ Split for clarity |
| `MarketData` dataclass | pandas DataFrame | ✅ Standard format |
| `ProcessingMode.TRAINING` | Direct method calls | ✅ Simplified |

## 📋 Features

### Historical Data Processing
- **OHLCV Data Loading**: CSV and pandas DataFrame support
- **Technical Indicators**: VWAP, RSI, ATR, EMA9, EMA21, Stochastic
- **Data Validation**: Comprehensive outlier detection and quality scoring
- **Normalization**: Z-score normalization with rolling windows
- **Parameter Export**: Export normalization parameters for production consistency

### Google Colab Optimization
- **Fast Installation**: < 2 minutes in Colab environment
- **Quick Import**: < 10 seconds package initialization
- **CPU-Only Dependencies**: No CUDA/GPU requirements for basic functionality
- **Memory Efficient**: < 100MB package overhead after import
- **Environment Detection**: Automatic Colab/Jupyter detection

### Real-time Components (Production)
- **Streaming Normalization**: Real-time data processing with exported parameters
- **Production Integration**: Compatible with TimeStrader VPS deployment

## 📖 Detailed Documentation

### Historical Processor API

```python
from timestrader_preprocessing import HistoricalProcessor

# Initialize processor
processor = HistoricalProcessor(config_path="config.yaml")

# Load data (supports file paths, StringIO for Colab)
data = processor.load_from_csv(
    file_path="data.csv",
    progress_bar=True  # Show progress for large files
)

# Calculate technical indicators
indicators = processor.calculate_indicators(
    data=data,
    indicators=['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stoch']
)

# Normalize data with rolling window
normalized, params = processor.normalize_data(
    data=indicators,
    window_size=288,  # 24 hours for 5-min candles
    method='zscore'
)

# Export parameters for production
processor.export_normalization_parameters(
    params=params,
    output_path="normalization_params.json"
)

# Get data quality metrics
quality = processor.get_quality_metrics()
print(f"Quality score: {quality.score:.2%}")
```

### Environment Detection

```python
import timestrader_preprocessing as tsp

# Check environment
if tsp.is_colab_environment():
    print("Running in Google Colab")
    # Colab-specific optimizations
elif tsp.is_jupyter_environment():
    print("Running in Jupyter notebook")
else:
    print("Running in standard Python environment")

# Access environment information
info = tsp.ENVIRONMENT_INFO
print(f"Python version: {info['python_version']}")
print(f"Package version: {info['package_version']}")
```

### Configuration Management

```python
from timestrader_preprocessing.config import get_default_config

# Get default configuration for current environment
config = get_default_config()

# Colab-specific configuration
colab_config = get_default_config(environment='colab')

# Production configuration  
prod_config = get_default_config(environment='production')
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Fast unit tests
pytest -m integration   # Integration tests  
pytest -m colab        # Colab-specific tests
pytest -m package      # Package installation tests

# Run with coverage
pytest --cov=timestrader_preprocessing --cov-report=html
```

## 📊 Performance Benchmarks

| Metric | Target | Typical |
|--------|--------|---------|
| Installation Time (Colab) | < 2 minutes | ~1.5 minutes |
| Import Time | < 10 seconds | ~3 seconds |
| Package Size | < 50MB | ~35MB |
| Memory Overhead | < 100MB | ~65MB |
| Processing Speed | 441K candles < 5 min | ~3.5 minutes |

## 🔧 Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/timestrader/timestrader-v05
cd timestrader-v05/timestrader-preprocessing

# Install development dependencies
pip install -e .[dev]

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

### Building and Publishing

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (requires authentication)
twine upload dist/*

# Test installation
pip install timestrader-preprocessing
```

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: https://timestrader.readthedocs.io
- **Issues**: https://github.com/timestrader/timestrader-v05/issues
- **Discussions**: https://github.com/timestrader/timestrader-v05/discussions

## 🏗️ Architecture

This package is part of the TimeStrader AI trading system:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Google Colab   │    │  PyPI Package    │    │   VPS Production │
│                 │    │                  │    │                 │
│ Model Training  │◄───┤ timestrader-     │───►│  Real-time      │
│ Data Processing │    │ preprocessing    │    │  Trading        │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

- **Training Phase**: Use this package in Google Colab for historical data processing and model training
- **Production Phase**: Export parameters and models to VPS for real-time trading
- **Retraining**: Weekly updates using the same preprocessing pipeline for consistency

---

**TimeStrader Team** - Building the future of AI-powered trading