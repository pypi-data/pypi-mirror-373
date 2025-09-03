"""
Real-time Processing Module

Provides real-time data processing components for production environments.
Note: Most real-time functionality requires production dependencies.

From Story 1.1b: Real-Time Processing Pipeline (VPS Production)
"""

from .streaming import RealtimeNormalizer

__all__ = [
    "RealtimeNormalizer"
]