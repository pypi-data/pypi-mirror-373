# Changelog

All notable changes to the timestrader-preprocessing package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- TestPyPI staging environment for safer releases
- Package usage analytics and monitoring
- Automated security scanning for dependencies
- Enhanced Jupyter notebook integration

## [1.0.0] - 2025-09-02

### Added
- Initial release of timestrader-preprocessing package
- Historical data processing pipeline for Google Colab
- Technical indicators calculation (VWAP, RSI, ATR, EMA9, EMA21, Stochastic)
- Z-score normalization with rolling window support
- Data validation and quality scoring system
- Parameter export functionality for production consistency
- Google Colab environment detection and optimization
- CPU-only dependencies for Colab compatibility
- Real-time processing components for production integration
- Comprehensive test suite with multiple test categories
- Package size optimization (< 50MB target)
- Fast import performance (< 10 seconds)
- Memory-efficient design (< 100MB overhead)

### Package Structure
- `timestrader_preprocessing.historical`: Historical data processing
- `timestrader_preprocessing.realtime`: Real-time processing components
- `timestrader_preprocessing.common`: Shared models and utilities
- `timestrader_preprocessing.config`: Configuration management

### Dependencies
- Core: pandas>=1.5.0, numpy>=1.21.0, pydantic>=1.10.0, pyyaml>=6.0
- Colab extras: matplotlib>=3.5.0, jupyter>=1.0.0, ipywidgets>=8.0.0
- Production extras: redis>=4.5.0, psutil>=5.9.0, fastapi>=0.100.0

### Documentation
- Comprehensive README with usage examples
- API documentation for all public functions
- Google Colab integration guide
- Performance benchmarks and targets
- Development setup instructions

### Testing
- Unit tests for core functionality
- Integration tests for data processing workflows  
- Colab-specific compatibility tests
- Package installation and import validation
- Performance benchmark tests

### Security
- No embedded secrets or sensitive information
- Dependency security validation
- Package integrity with checksums
- Secure PyPI token management setup

---

## Version History

- **1.0.0**: Initial release with core functionality
- Future versions will follow semantic versioning:
  - **MAJOR**: Incompatible API changes
  - **MINOR**: Backward-compatible functionality additions
  - **PATCH**: Backward-compatible bug fixes

## Migration Guide

### From TimeStrader Main Package

If migrating from using TimeStrader main package modules directly:

```python
# Old (direct module usage)
from src.timestrader.data.historical_processor import HistoricalProcessor

# New (pip package)
from timestrader_preprocessing import HistoricalProcessor
```

### Dependency Changes

The package uses more conservative dependency version ranges for better compatibility:

- pandas: `>=1.5.0,<3.0.0` (was `^2.0.0`)
- numpy: `>=1.21.0,<2.0.0` (was `^1.24.0`)
- pydantic: `>=1.10.0,<3.0.0` (was `^2.0.0`)

## Support

For questions about specific versions or upgrade paths:
- Check the [README](README.md) for current usage patterns
- Open an issue at https://github.com/timestrader/timestrader-v05/issues
- Review test files for examples of new functionality