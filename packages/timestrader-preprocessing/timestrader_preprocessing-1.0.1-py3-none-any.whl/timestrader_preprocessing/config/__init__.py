"""
Configuration Management

Default configurations and parameter management for different environments
including Google Colab and production settings.
"""

from .defaults import (
    ParameterManager,
    ColabConfig,
    ProductionConfig,
    get_default_config
)

__all__ = [
    "ParameterManager",
    "ColabConfig", 
    "ProductionConfig",
    "get_default_config"
]