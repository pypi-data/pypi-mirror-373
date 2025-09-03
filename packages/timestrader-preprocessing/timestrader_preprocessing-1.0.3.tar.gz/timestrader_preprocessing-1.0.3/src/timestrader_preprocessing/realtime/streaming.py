"""
Real-Time Normalization System
Applies Story 1.1a parameters for consistent real-time normalization with <1ms latency
"""
import time
import numpy as np
from typing import Dict, Any, Optional
import logging
from .parameter_manager import ParameterManager
from .normalizers import ProductionNormalizer


class RealtimeNormalizer:
    """
    Ultra-fast real-time normalizer using pre-calculated parameters from Story 1.1a.
    
    Optimized for sub-millisecond normalization with parameter consistency validation.
    Applies exact same Z-score normalization as training but with single-point updates.
    
    Performance targets:
    - Normalization latency: < 1ms
    - Memory usage: < 5MB
    - Parameter drift detection: Real-time alerts
    """
    
    def __init__(self, parameter_manager: ParameterManager):
        """
        Initialize real-time normalizer with parameter manager
        
        Args:
            parameter_manager: ParameterManager instance with loaded parameters
        """
        self.parameter_manager = parameter_manager
        self.logger = logging.getLogger(f"{__name__}")
        
        # Pre-computed normalization parameters for ultra-fast access
        self._norm_params = {}
        
        # Performance tracking
        self._normalization_stats = {
            'total_normalizations': 0,
            'avg_latency_ms': 0,
            'max_latency_ms': 0,
            'parameter_errors': 0,
            'drift_alerts': 0
        }
        
        # Expected indicator order for consistency
        self.indicator_order = ['vwap', 'rsi', 'atr', 'ema9', 'ema21', 'stochastic']
        
        # Initialize parameters
        self._initialize_parameters()
        
        self.logger.info("RealtimeNormalizer initialized")
    
    def _initialize_parameters(self) -> None:
        """Initialize and cache normalization parameters for fast access"""
        try:
            if not self.parameter_manager.is_loaded():
                raise ValueError("ParameterManager must have loaded parameters")
            
            # Extract and cache all parameters
            all_params = self.parameter_manager.get_all_normalization_params()
            
            for indicator in self.indicator_order:
                if indicator in all_params:
                    params = all_params[indicator]
                    self._norm_params[indicator] = {
                        'mean': float(params['mean']),
                        'std': float(params['std'])
                    }
                    
                    # Validate parameters
                    if params['std'] <= 0:
                        raise ValueError(f"Invalid std for {indicator}: {params['std']}")
                    
                    if np.isnan(params['mean']) or np.isnan(params['std']):
                        raise ValueError(f"NaN parameters for {indicator}")
                else:
                    self.logger.error(f"Missing normalization parameters for {indicator}")
                    raise ValueError(f"Missing parameters for required indicator: {indicator}")
            
            self.logger.info(f"Cached normalization parameters for {len(self._norm_params)} indicators")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize parameters: {e}")
            raise
    
    def normalize_indicators(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize technical indicators using cached parameters
        
        Args:
            indicators: Dict with raw indicator values {indicator_name: value}
            
        Returns:
            Dict with normalized values {indicator_name_norm: normalized_value}
        """
        start_time = time.time()
        
        try:
            normalized = {}
            
            # Normalize each indicator using cached parameters
            for indicator in self.indicator_order:
                if indicator not in indicators:
                    self.logger.warning(f"Missing indicator in input: {indicator}")
                    normalized[f"{indicator}_norm"] = 0.0  # Default to neutral
                    continue
                
                if indicator not in self._norm_params:
                    self._normalization_stats['parameter_errors'] += 1
                    self.logger.error(f"No cached parameters for {indicator}")
                    normalized[f"{indicator}_norm"] = 0.0  # Default to neutral
                    continue
                
                # Ultra-fast Z-score normalization
                raw_value = float(indicators[indicator])
                params = self._norm_params[indicator]
                
                # Apply Z-score: (value - mean) / std
                z_score = (raw_value - params['mean']) / params['std']
                
                # Cap extreme values to [-3, 3] range (99.7% of normal distribution)
                normalized_value = max(-3.0, min(3.0, z_score))
                
                # Handle edge cases
                if np.isnan(normalized_value) or np.isinf(normalized_value):
                    self.logger.warning(f"Invalid normalized value for {indicator}: {normalized_value}")
                    normalized_value = 0.0  # Default to neutral
                
                normalized[f"{indicator}_norm"] = normalized_value
            
            # Update performance statistics
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self._update_performance_stats(processing_time)
            
            # Log performance warning if exceeding target
            if processing_time > 1.0:
                self.logger.warning(f"Normalization took {processing_time:.2f}ms (>1ms target)")
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing indicators: {e}")
            return self._get_default_normalized_values()
    
    def normalize_single_indicator(self, indicator: str, value: float) -> float:
        """
        Normalize single indicator value for maximum performance
        
        Args:
            indicator: Indicator name (e.g., 'vwap', 'rsi')
            value: Raw indicator value
            
        Returns:
            Normalized value
        """
        try:
            if indicator not in self._norm_params:
                self.logger.error(f"No parameters for indicator: {indicator}")
                return 0.0
            
            params = self._norm_params[indicator]
            z_score = (float(value) - params['mean']) / params['std']
            
            # Cap extreme values
            normalized = max(-3.0, min(3.0, z_score))
            
            # Handle edge cases
            if np.isnan(normalized) or np.isinf(normalized):
                return 0.0
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing {indicator}: {e}")
            return 0.0
    
    def validate_input_consistency(self, indicators: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate input indicators for consistency and quality
        
        Args:
            indicators: Raw indicator values
            
        Returns:
            Validation results with quality metrics
        """
        try:
            validation = {
                'valid': True,
                'issues': [],
                'quality_score': 1.0,
                'indicators_status': {}
            }
            
            for indicator in self.indicator_order:
                indicator_status = {
                    'present': indicator in indicators,
                    'valid_value': False,
                    'in_expected_range': False,
                    'z_score': None
                }
                
                if indicator in indicators:
                    value = indicators[indicator]
                    
                    # Check for valid numeric value
                    try:
                        float_value = float(value)
                        indicator_status['valid_value'] = not (np.isnan(float_value) or np.isinf(float_value))
                        
                        if indicator_status['valid_value'] and indicator in self._norm_params:
                            # Calculate Z-score for range validation
                            params = self._norm_params[indicator]
                            z_score = abs((float_value - params['mean']) / params['std'])
                            indicator_status['z_score'] = z_score
                            
                            # Flag if more than 4 standard deviations (extreme outlier)
                            indicator_status['in_expected_range'] = z_score <= 4.0
                            
                            if z_score > 4.0:
                                validation['issues'].append(f"{indicator} is {z_score:.1f} std devs from training mean")
                                validation['quality_score'] *= 0.9  # Reduce quality score
                        
                    except (ValueError, TypeError):
                        indicator_status['valid_value'] = False
                        validation['issues'].append(f"{indicator} has invalid numeric value: {value}")
                        validation['quality_score'] *= 0.8
                
                else:
                    validation['issues'].append(f"Missing required indicator: {indicator}")
                    validation['quality_score'] *= 0.7
                
                validation['indicators_status'][indicator] = indicator_status
            
            # Overall validation status
            validation['valid'] = validation['quality_score'] > 0.5 and len(validation['issues']) == 0
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Error validating input consistency: {e}")
            return {
                'valid': False,
                'error': str(e),
                'quality_score': 0.0
            }
    
    def detect_parameter_drift(self, indicators: Dict[str, float]) -> Dict[str, Any]:
        """
        Detect parameter drift in real-time by comparing current values to training distribution
        
        Args:
            indicators: Current raw indicator values
            
        Returns:
            Drift analysis results
        """
        try:
            drift_results = {
                'overall_drift_detected': False,
                'drift_indicators': [],
                'drift_scores': {},
                'max_drift_score': 0.0,
                'timestamp': time.time()
            }
            
            for indicator, value in indicators.items():
                if indicator not in self._norm_params:
                    continue
                
                params = self._norm_params[indicator]
                
                # Calculate Z-score (how many std devs from training mean)
                z_score = abs((float(value) - params['mean']) / params['std'])
                
                # Convert to drift score (0-1 scale, where 1 = 3+ std devs away)
                drift_score = min(z_score / 3.0, 1.0)
                
                drift_results['drift_scores'][indicator] = {
                    'z_score': z_score,
                    'drift_score': drift_score,
                    'current_value': float(value),
                    'training_mean': params['mean'],
                    'training_std': params['std']
                }
                
                # Flag significant drift (>2 std devs = drift_score > 0.67)
                if drift_score > 0.67:
                    drift_results['overall_drift_detected'] = True
                    drift_results['drift_indicators'].append(indicator)
                    
                    # Log drift warning
                    self.logger.warning(
                        f"Parameter drift detected for {indicator}: "
                        f"current={value:.4f}, training_mean={params['mean']:.4f}, "
                        f"z_score={z_score:.2f}"
                    )
                
                # Track maximum drift
                drift_results['max_drift_score'] = max(drift_results['max_drift_score'], drift_score)
            
            # Update drift statistics
            if drift_results['overall_drift_detected']:
                self._normalization_stats['drift_alerts'] += 1
            
            return drift_results
            
        except Exception as e:
            self.logger.error(f"Error detecting parameter drift: {e}")
            return {'error': str(e)}
    
    def _update_performance_stats(self, processing_time_ms: float) -> None:
        """Update performance statistics"""
        try:
            self._normalization_stats['total_normalizations'] += 1
            
            # Update running average
            count = self._normalization_stats['total_normalizations']
            current_avg = self._normalization_stats['avg_latency_ms']
            
            # Exponential moving average for recent performance
            alpha = min(0.1, 2.0 / (count + 1))  # Adaptive learning rate
            self._normalization_stats['avg_latency_ms'] = (
                alpha * processing_time_ms + (1 - alpha) * current_avg
            )
            
            # Track maximum latency
            self._normalization_stats['max_latency_ms'] = max(
                self._normalization_stats['max_latency_ms'],
                processing_time_ms
            )
            
        except Exception as e:
            self.logger.error(f"Error updating performance stats: {e}")
    
    def _get_default_normalized_values(self) -> Dict[str, float]:
        """Get default normalized values for error cases"""
        return {f"{indicator}_norm": 0.0 for indicator in self.indicator_order}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for monitoring"""
        try:
            metrics = self._normalization_stats.copy()
            
            # Add parameter information
            metrics['parameter_info'] = {
                'version': self.parameter_manager.get_version(),
                'parameter_age_hours': self.parameter_manager.get_age_hours(),
                'indicators_count': len(self._norm_params),
                'indicators': list(self._norm_params.keys())
            }
            
            # Performance assessment
            metrics['performance_assessment'] = {
                'latency_compliant': metrics['avg_latency_ms'] < 1.0,
                'error_rate_pct': (
                    (metrics['parameter_errors'] / max(metrics['total_normalizations'], 1)) * 100
                ),
                'drift_rate_pct': (
                    (metrics['drift_alerts'] / max(metrics['total_normalizations'], 1)) * 100
                )
            }
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def refresh_parameters(self) -> bool:
        """
        Refresh parameters from parameter manager (hot reload support)
        
        Returns:
            True if parameters were successfully refreshed
        """
        try:
            self.logger.info("Refreshing normalization parameters")
            
            # Check if parameter manager has updated parameters
            if not self.parameter_manager.is_loaded():
                self.logger.error("ParameterManager not loaded during refresh")
                return False
            
            # Re-initialize parameters
            old_version = self.parameter_manager.get_version()
            self._initialize_parameters()
            new_version = self.parameter_manager.get_version()
            
            self.logger.info(f"Parameters refreshed: {old_version} -> {new_version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh parameters: {e}")
            return False
    
    def get_normalization_summary(self) -> Dict[str, Any]:
        """Get comprehensive normalization system summary"""
        try:
            return {
                'status': 'active',
                'parameter_version': self.parameter_manager.get_version(),
                'indicators_configured': len(self._norm_params),
                'expected_indicators': self.indicator_order,
                'performance_metrics': self.get_performance_metrics(),
                'parameter_manager_health': self.parameter_manager.get_health_status()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


class BatchRealtimeNormalizer:
    """
    Batch processor for real-time normalization of multiple data points
    Optimized for high-throughput scenarios with vectorized operations
    """
    
    def __init__(self, parameter_manager: ParameterManager):
        self.parameter_manager = parameter_manager
        self.logger = logging.getLogger(f"{__name__}.batch")
        
        # Initialize base normalizer
        self._base_normalizer = RealtimeNormalizer(parameter_manager)
    
    def normalize_batch(self, indicators_batch: list[Dict[str, float]]) -> list[Dict[str, float]]:
        """
        Normalize a batch of indicator dictionaries
        
        Args:
            indicators_batch: List of indicator dictionaries
            
        Returns:
            List of normalized indicator dictionaries
        """
        try:
            start_time = time.time()
            
            normalized_batch = []
            for indicators in indicators_batch:
                normalized = self._base_normalizer.normalize_indicators(indicators)
                normalized_batch.append(normalized)
            
            processing_time = (time.time() - start_time) * 1000
            avg_per_item = processing_time / len(indicators_batch) if indicators_batch else 0
            
            self.logger.debug(
                f"Batch normalized {len(indicators_batch)} items in {processing_time:.2f}ms "
                f"({avg_per_item:.2f}ms per item)"
            )
            
            return normalized_batch
            
        except Exception as e:
            self.logger.error(f"Error in batch normalization: {e}")
            return [self._base_normalizer._get_default_normalized_values()] * len(indicators_batch)
    
    def validate_batch_consistency(
        self, 
        indicators_batch: list[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Validate consistency across a batch of indicators
        
        Args:
            indicators_batch: List of indicator dictionaries
            
        Returns:
            Batch validation results
        """
        try:
            if not indicators_batch:
                return {'valid': False, 'error': 'Empty batch'}
            
            batch_validation = {
                'valid': True,
                'batch_size': len(indicators_batch),
                'consistent_indicators': True,
                'quality_scores': [],
                'avg_quality': 0.0,
                'problematic_items': []
            }
            
            # Check first item for expected structure
            expected_indicators = set(indicators_batch[0].keys())
            
            for idx, indicators in enumerate(indicators_batch):
                # Validate individual item
                validation = self._base_normalizer.validate_input_consistency(indicators)
                batch_validation['quality_scores'].append(validation['quality_score'])
                
                # Check indicator consistency across batch
                if set(indicators.keys()) != expected_indicators:
                    batch_validation['consistent_indicators'] = False
                    batch_validation['problematic_items'].append({
                        'index': idx,
                        'issue': 'inconsistent_indicators',
                        'expected': list(expected_indicators),
                        'actual': list(indicators.keys())
                    })
                
                # Flag low quality items
                if validation['quality_score'] < 0.8:
                    batch_validation['problematic_items'].append({
                        'index': idx,
                        'issue': 'low_quality',
                        'quality_score': validation['quality_score'],
                        'issues': validation.get('issues', [])
                    })
            
            # Calculate overall metrics
            batch_validation['avg_quality'] = np.mean(batch_validation['quality_scores'])
            batch_validation['valid'] = (
                batch_validation['consistent_indicators'] and 
                batch_validation['avg_quality'] > 0.7 and
                len(batch_validation['problematic_items']) < len(indicators_batch) * 0.1  # <10% problematic
            )
            
            return batch_validation
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }