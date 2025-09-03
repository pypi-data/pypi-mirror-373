"""
Data Validation Framework for TimeStrader
Comprehensive validation system for historical and real-time trading data.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.preprocessing import RobustScaler
import json


@dataclass
class ValidationRule:
    """Represents a single validation rule."""
    name: str
    description: str
    rule_type: str  # 'range', 'relationship', 'statistical', 'temporal'
    parameters: Dict[str, Any]
    severity: str  # 'error', 'warning', 'info'


@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule_name: str
    passed: bool
    errors_count: int
    warnings_count: int
    message: str
    affected_records: Optional[List[int]] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment."""
    total_records: int
    validation_results: List[ValidationResult]
    quality_score: float
    outliers_detected: int
    missing_values: int
    duplicate_records: int
    temporal_gaps: int
    recommendations: List[str]
    timestamp: datetime


class DataValidator:
    """
    Comprehensive data validation framework with outlier detection,
    missing value handling, and quality scoring system.
    """
    
    def __init__(self, target_quality_score: float = 0.995):
        """
        Initialize validator with quality targets.
        
        Args:
            target_quality_score: Target quality score (default: 99.5%)
        """
        self.target_quality_score = target_quality_score
        self.logger = self._setup_logger()
        self.validation_rules = self._initialize_default_rules()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for validation operations."""
        logger = logging.getLogger("DataValidator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_default_rules(self) -> List[ValidationRule]:
        """Initialize default validation rules for MNQ trading data."""
        rules = [
            ValidationRule(
                name="price_range_check",
                description="Validate price values are within reasonable range for MNQ",
                rule_type="range",
                parameters={"min_price": 1000, "max_price": 50000, "columns": ["open", "high", "low", "close"]},
                severity="error"
            ),
            ValidationRule(
                name="volume_validation",
                description="Validate volume values are positive",
                rule_type="range",
                parameters={"min_value": 0, "column": "volume"},
                severity="error"
            ),
            ValidationRule(
                name="ohlc_relationship",
                description="Validate OHLC relationships (high >= max(o,c), low <= min(o,c))",
                rule_type="relationship",
                parameters={},
                severity="error"
            ),
            ValidationRule(
                name="price_outliers",
                description="Detect price outliers using 3-sigma rule",
                rule_type="statistical",
                parameters={"sigma_threshold": 3, "columns": ["open", "high", "low", "close"]},
                severity="warning"
            ),
            ValidationRule(
                name="volume_outliers",
                description="Detect volume outliers using IQR method",
                rule_type="statistical",
                parameters={"iqr_multiplier": 2.5, "column": "volume"},
                severity="warning"
            ),
            ValidationRule(
                name="temporal_continuity",
                description="Check for temporal gaps in 5-minute data",
                rule_type="temporal",
                parameters={"expected_interval_minutes": 5, "max_gap_multiplier": 2},
                severity="warning"
            ),
            ValidationRule(
                name="missing_values",
                description="Check for missing values in critical columns",
                rule_type="completeness",
                parameters={"critical_columns": ["timestamp", "open", "high", "low", "close", "volume"]},
                severity="error"
            ),
            ValidationRule(
                name="duplicate_timestamps",
                description="Check for duplicate timestamp entries",
                rule_type="uniqueness",
                parameters={"column": "timestamp"},
                severity="error"
            )
        ]
        
        return rules
    
    def add_custom_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.validation_rules.append(rule)
        self.logger.info(f"Added custom validation rule: {rule.name}")
    
    def validate_data(self, data: pd.DataFrame) -> DataQualityReport:
        """
        Perform comprehensive data validation.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataQualityReport with validation results
        """
        self.logger.info(f"Starting validation of {len(data)} records")
        
        validation_results = []
        total_errors = 0
        total_warnings = 0
        
        # Execute all validation rules
        for rule in self.validation_rules:
            try:
                result = self._execute_validation_rule(data, rule)
                validation_results.append(result)
                
                if result.severity == "error":
                    total_errors += result.errors_count
                elif result.severity == "warning":
                    total_warnings += result.warnings_count
                    
            except Exception as e:
                self.logger.error(f"Failed to execute rule {rule.name}: {str(e)}")
                validation_results.append(ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    errors_count=1,
                    warnings_count=0,
                    message=f"Rule execution failed: {str(e)}"
                ))
                total_errors += 1
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(data)
        
        # Calculate overall quality score
        total_records = len(data)
        total_issues = (total_errors * 2) + total_warnings  # Errors weighted more heavily
        quality_score = max(0, 1 - (total_issues / total_records))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results, quality_score)
        
        report = DataQualityReport(
            total_records=total_records,
            validation_results=validation_results,
            quality_score=quality_score,
            outliers_detected=quality_metrics['outliers'],
            missing_values=quality_metrics['missing_values'],
            duplicate_records=quality_metrics['duplicates'],
            temporal_gaps=quality_metrics['temporal_gaps'],
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
        self.logger.info(f"Validation completed - Quality Score: {quality_score:.4f}")
        
        return report
    
    def _execute_validation_rule(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Execute a single validation rule."""
        if rule.rule_type == "range":
            return self._validate_range(data, rule)
        elif rule.rule_type == "relationship":
            return self._validate_relationship(data, rule)
        elif rule.rule_type == "statistical":
            return self._validate_statistical(data, rule)
        elif rule.rule_type == "temporal":
            return self._validate_temporal(data, rule)
        elif rule.rule_type == "completeness":
            return self._validate_completeness(data, rule)
        elif rule.rule_type == "uniqueness":
            return self._validate_uniqueness(data, rule)
        else:
            raise ValueError(f"Unknown rule type: {rule.rule_type}")
    
    def _validate_range(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Validate values are within specified ranges."""
        errors = 0
        affected_records = []
        
        if "columns" in rule.parameters:
            # Multi-column range check
            columns = rule.parameters["columns"]
            min_val = rule.parameters["min_price"]
            max_val = rule.parameters["max_price"]
            
            for col in columns:
                if col in data.columns:
                    invalid_mask = (data[col] < min_val) | (data[col] > max_val)
                    column_errors = invalid_mask.sum()
                    errors += column_errors
                    affected_records.extend(data[invalid_mask].index.tolist())
        else:
            # Single column range check
            col = rule.parameters["column"]
            min_val = rule.parameters["min_value"]
            max_val = rule.parameters.get("max_value", float('inf'))
            
            if col in data.columns:
                invalid_mask = (data[col] < min_val) | (data[col] > max_val)
                errors = invalid_mask.sum()
                affected_records = data[invalid_mask].index.tolist()
        
        return ValidationResult(
            rule_name=rule.name,
            passed=errors == 0,
            errors_count=errors if rule.severity == "error" else 0,
            warnings_count=errors if rule.severity == "warning" else 0,
            message=f"Found {errors} records outside valid range",
            affected_records=affected_records
        )
    
    def _validate_relationship(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Validate OHLC relationships."""
        if rule.name == "ohlc_relationship":
            # Check high >= max(open, close)
            high_valid = data['high'] >= data[['open', 'close']].max(axis=1)
            # Check low <= min(open, close) 
            low_valid = data['low'] <= data[['open', 'close']].min(axis=1)
            
            invalid_high = (~high_valid).sum()
            invalid_low = (~low_valid).sum()
            total_errors = invalid_high + invalid_low
            
            affected_records = data[~(high_valid & low_valid)].index.tolist()
            
            return ValidationResult(
                rule_name=rule.name,
                passed=total_errors == 0,
                errors_count=total_errors if rule.severity == "error" else 0,
                warnings_count=total_errors if rule.severity == "warning" else 0,
                message=f"Found {invalid_high} invalid high values, {invalid_low} invalid low values",
                affected_records=affected_records,
                details={"invalid_high": invalid_high, "invalid_low": invalid_low}
            )
    
    def _validate_statistical(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Validate using statistical methods for outlier detection."""
        outliers = 0
        affected_records = []
        
        if rule.name == "price_outliers":
            # 3-sigma rule for price outliers
            sigma_threshold = rule.parameters["sigma_threshold"]
            columns = rule.parameters["columns"]
            
            for col in columns:
                if col in data.columns:
                    mean_val = data[col].mean()
                    std_val = data[col].std()
                    outlier_mask = np.abs(data[col] - mean_val) > (sigma_threshold * std_val)
                    column_outliers = outlier_mask.sum()
                    outliers += column_outliers
                    affected_records.extend(data[outlier_mask].index.tolist())
        
        elif rule.name == "volume_outliers":
            # IQR method for volume outliers
            col = rule.parameters["column"]
            iqr_multiplier = rule.parameters["iqr_multiplier"]
            
            if col in data.columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR
                
                outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
                outliers = outlier_mask.sum()
                affected_records = data[outlier_mask].index.tolist()
        
        return ValidationResult(
            rule_name=rule.name,
            passed=outliers == 0,
            errors_count=outliers if rule.severity == "error" else 0,
            warnings_count=outliers if rule.severity == "warning" else 0,
            message=f"Detected {outliers} statistical outliers",
            affected_records=affected_records
        )
    
    def _validate_temporal(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Validate temporal continuity."""
        if rule.name == "temporal_continuity" and "timestamp" in data.columns:
            expected_interval = timedelta(minutes=rule.parameters["expected_interval_minutes"])
            max_gap_multiplier = rule.parameters["max_gap_multiplier"]
            max_allowed_gap = expected_interval * max_gap_multiplier
            
            # Calculate time differences
            time_diffs = data['timestamp'].diff()
            
            # Find gaps larger than allowed
            large_gaps = time_diffs > max_allowed_gap
            gaps_count = large_gaps.sum()
            
            affected_records = data[large_gaps].index.tolist()
            
            return ValidationResult(
                rule_name=rule.name,
                passed=gaps_count == 0,
                errors_count=gaps_count if rule.severity == "error" else 0,
                warnings_count=gaps_count if rule.severity == "warning" else 0,
                message=f"Found {gaps_count} temporal gaps > {max_allowed_gap}",
                affected_records=affected_records
            )
        
        return ValidationResult(rule.name, True, 0, 0, "No temporal validation needed")
    
    def _validate_completeness(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Validate data completeness."""
        if rule.name == "missing_values":
            critical_columns = rule.parameters["critical_columns"]
            missing_count = 0
            affected_records = []
            
            for col in critical_columns:
                if col in data.columns:
                    col_missing = data[col].isnull()
                    col_missing_count = col_missing.sum()
                    missing_count += col_missing_count
                    affected_records.extend(data[col_missing].index.tolist())
            
            return ValidationResult(
                rule_name=rule.name,
                passed=missing_count == 0,
                errors_count=missing_count if rule.severity == "error" else 0,
                warnings_count=missing_count if rule.severity == "warning" else 0,
                message=f"Found {missing_count} missing values in critical columns",
                affected_records=list(set(affected_records))  # Remove duplicates
            )
    
    def _validate_uniqueness(self, data: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        """Validate data uniqueness."""
        if rule.name == "duplicate_timestamps":
            col = rule.parameters["column"]
            if col in data.columns:
                duplicates = data.duplicated(subset=[col])
                duplicate_count = duplicates.sum()
                affected_records = data[duplicates].index.tolist()
                
                return ValidationResult(
                    rule_name=rule.name,
                    passed=duplicate_count == 0,
                    errors_count=duplicate_count if rule.severity == "error" else 0,
                    warnings_count=duplicate_count if rule.severity == "warning" else 0,
                    message=f"Found {duplicate_count} duplicate timestamps",
                    affected_records=affected_records
                )
    
    def _calculate_quality_metrics(self, data: pd.DataFrame) -> Dict[str, int]:
        """Calculate additional quality metrics."""
        metrics = {}
        
        # Count outliers using 3-sigma rule on all numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        outliers = 0
        for col in numeric_cols:
            if col in ['open', 'high', 'low', 'close', 'volume']:
                mean_val = data[col].mean()
                std_val = data[col].std()
                outliers += (np.abs(data[col] - mean_val) > 3 * std_val).sum()
        
        metrics['outliers'] = outliers
        metrics['missing_values'] = data.isnull().sum().sum()
        metrics['duplicates'] = data.duplicated().sum()
        
        # Calculate temporal gaps
        if 'timestamp' in data.columns:
            expected_interval = timedelta(minutes=5)
            time_diffs = data['timestamp'].diff()
            metrics['temporal_gaps'] = (time_diffs > expected_interval * 2).sum()
        else:
            metrics['temporal_gaps'] = 0
        
        return metrics
    
    def _generate_recommendations(
        self, 
        validation_results: List[ValidationResult], 
        quality_score: float
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Quality score recommendations
        if quality_score < self.target_quality_score:
            recommendations.append(
                f"Quality score {quality_score:.4f} is below target {self.target_quality_score:.3f}. "
                "Consider data cleaning before training."
            )
        
        # Specific recommendations based on validation results
        for result in validation_results:
            if not result.passed:
                if result.rule_name == "price_outliers" and result.warnings_count > 0:
                    recommendations.append(
                        "Consider using robust normalization methods to handle price outliers."
                    )
                elif result.rule_name == "volume_outliers" and result.warnings_count > 0:
                    recommendations.append(
                        "Volume outliers detected. Consider volume-based filtering or normalization."
                    )
                elif result.rule_name == "temporal_continuity" and result.warnings_count > 0:
                    recommendations.append(
                        "Temporal gaps detected. Consider interpolation or gap filling strategies."
                    )
                elif result.rule_name == "missing_values" and result.errors_count > 0:
                    recommendations.append(
                        "Missing values in critical columns must be addressed before processing."
                    )
                elif result.rule_name == "ohlc_relationship" and result.errors_count > 0:
                    recommendations.append(
                        "OHLC relationship violations indicate data corruption. Manual review required."
                    )
        
        if not recommendations:
            recommendations.append("Data quality is excellent. Ready for processing.")
        
        return recommendations
    
    def export_validation_report(self, report: DataQualityReport, output_path: str) -> None:
        """Export validation report to JSON file."""
        report_dict = {
            "validation_summary": {
                "total_records": report.total_records,
                "quality_score": report.quality_score,
                "target_quality_score": self.target_quality_score,
                "quality_threshold_met": report.quality_score >= self.target_quality_score,
                "timestamp": report.timestamp.isoformat()
            },
            "quality_metrics": {
                "outliers_detected": report.outliers_detected,
                "missing_values": report.missing_values,
                "duplicate_records": report.duplicate_records,
                "temporal_gaps": report.temporal_gaps
            },
            "validation_results": [
                {
                    "rule_name": result.rule_name,
                    "passed": result.passed,
                    "errors_count": result.errors_count,
                    "warnings_count": result.warnings_count,
                    "message": result.message,
                    "affected_records_count": len(result.affected_records) if result.affected_records else 0
                }
                for result in report.validation_results
            ],
            "recommendations": report.recommendations
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        self.logger.info(f"Validation report exported to {output_path}")


class OutlierDetector:
    """
    Specialized outlier detection methods for financial time series data.
    """
    
    @staticmethod
    def detect_price_outliers_zscore(
        data: pd.DataFrame, 
        columns: List[str], 
        threshold: float = 3.0
    ) -> Dict[str, pd.Series]:
        """
        Detect outliers using Z-score method.
        
        Args:
            data: DataFrame with price data
            columns: Columns to check for outliers
            threshold: Z-score threshold (default: 3.0)
            
        Returns:
            Dictionary with boolean masks for outliers
        """
        outliers = {}
        
        for col in columns:
            if col in data.columns:
                z_scores = np.abs(stats.zscore(data[col].dropna()))
                outliers[col] = z_scores > threshold
            
        return outliers
    
    @staticmethod
    def detect_volume_outliers_iqr(
        data: pd.DataFrame, 
        column: str = 'volume',
        multiplier: float = 2.5
    ) -> pd.Series:
        """
        Detect volume outliers using IQR method.
        
        Args:
            data: DataFrame with volume data
            column: Volume column name
            multiplier: IQR multiplier (default: 2.5)
            
        Returns:
            Boolean mask for outliers
        """
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        return (data[column] < lower_bound) | (data[column] > upper_bound)
    
    @staticmethod
    def detect_multivariate_outliers(
        data: pd.DataFrame,
        columns: List[str],
        contamination: float = 0.1
    ) -> pd.Series:
        """
        Detect multivariate outliers using Isolation Forest.
        
        Args:
            data: DataFrame with data
            columns: Columns to use for outlier detection
            contamination: Expected proportion of outliers
            
        Returns:
            Boolean mask for outliers
        """
        try:
            from sklearn.ensemble import IsolationForest
            
            clf = IsolationForest(contamination=contamination, random_state=42)
            outlier_labels = clf.fit_predict(data[columns])
            
            return outlier_labels == -1
            
        except ImportError:
            # Fallback to statistical method if sklearn not available
            return OutlierDetector.detect_price_outliers_zscore(
                data, columns, threshold=3.0
            )[columns[0]]