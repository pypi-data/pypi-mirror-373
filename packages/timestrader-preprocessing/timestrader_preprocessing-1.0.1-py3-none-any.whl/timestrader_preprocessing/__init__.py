"""
TimeStrader Preprocessing - PyPI Package for Google Colab

A pip-installable package providing TimeStrader data processing capabilities
for Google Colab training and retraining workflows.
"""

__version__ = "1.0.0"
__author__ = "TimeStrader Team"
__email__ = "team@timestrader.ai"

# Main package imports for easy access
from timestrader_preprocessing.historical.processor import HistoricalProcessor
from timestrader_preprocessing.common.models import (
    NormalizationParams,
    DataQualityMetrics,
    ProcessingConfig
)

# Environment detection for Google Colab
import sys
import os

def is_colab_environment() -> bool:
    """Detect if running in Google Colab environment."""
    return 'google.colab' in sys.modules

def is_jupyter_environment() -> bool:
    """Detect if running in Jupyter notebook environment."""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False

# Package-level configuration
ENVIRONMENT_INFO = {
    "is_colab": is_colab_environment(),
    "is_jupyter": is_jupyter_environment(),
    "python_version": sys.version,
    "package_version": __version__
}

# Export main components
__all__ = [
    "HistoricalProcessor",
    "NormalizationParams", 
    "DataQualityMetrics",
    "ProcessingConfig",
    "is_colab_environment",
    "is_jupyter_environment",
    "ENVIRONMENT_INFO"
]