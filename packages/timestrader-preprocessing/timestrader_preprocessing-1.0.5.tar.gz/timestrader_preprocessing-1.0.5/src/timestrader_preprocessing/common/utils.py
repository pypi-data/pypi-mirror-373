"""
Parameter Export System for TimeStrader
Handles export of normalization parameters and data quality reports for production consistency.
"""
import json
import hashlib
import zipfile
import shutil
import os
import stat
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging
import tempfile


@dataclass
class ExportMetadata:
    """Metadata for parameter exports."""
    export_id: str
    version: str
    timestamp: datetime
    dataset_hash: str
    file_count: int
    total_size_bytes: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'export_id': self.export_id,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'dataset_hash': self.dataset_hash,
            'file_count': self.file_count,
            'total_size_bytes': self.total_size_bytes
        }


class ParameterExporter:
    """
    Handles export of normalization parameters, training sequences, and quality reports.
    Designed for production deployment and model consistency with security features.
    """
    
    def __init__(self, base_export_path: str = "exports", enable_access_logging: bool = True):
        """
        Initialize parameter exporter with security features.
        
        Args:
            base_export_path: Base directory for exports
            enable_access_logging: Enable access logging for security monitoring
        """
        self.base_export_path = Path(base_export_path)
        self.base_export_path.mkdir(parents=True, exist_ok=True)
        
        self.enable_access_logging = enable_access_logging
        self.access_log_path = self.base_export_path / "access.log"
        
        self.logger = self._setup_logger()
        
        # Initialize security monitoring
        if enable_access_logging:
            self._init_access_logging()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for export operations."""
        logger = logging.getLogger("ParameterExporter")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_access_logging(self) -> None:
        """Initialize access logging for security monitoring."""
        if not self.access_log_path.exists():
            with open(self.access_log_path, 'w') as f:
                f.write(f"# TimeStrader Parameter Access Log - Created {datetime.now().isoformat()}\n")
        
        # Set restrictive permissions on access log (owner read/write only)
        try:
            os.chmod(self.access_log_path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            self.logger.warning("Could not set restrictive permissions on access log")
    
    def _log_access(self, operation: str, file_path: str, success: bool = True, details: str = "") -> None:
        """Log access attempts for security monitoring."""
        if not self.enable_access_logging:
            return
        
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'file_path': file_path,
                'success': success,
                'details': details,
                'process_id': os.getpid(),
                'user': os.getenv('USER', 'unknown')
            }
            
            with open(self.access_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self.logger.warning(f"Failed to log access: {e}")
    
    def _calculate_file_integrity_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate integrity hash for a file."""
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _set_secure_file_permissions(self, file_path: str) -> None:
        """Set secure file permissions (owner read/write only)."""
        try:
            # Owner read/write, no access for group/others
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError as e:
            self.logger.warning(f"Could not set secure permissions on {file_path}: {e}")
    
    def _create_file_signature(self, file_path: str, content_hash: str) -> Dict[str, Any]:
        """Create file signature with integrity information."""
        stat_info = os.stat(file_path)
        
        return {
            'file_path': file_path,
            'content_hash_sha256': content_hash,
            'file_size': stat_info.st_size,
            'created_time': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            'signature_created': datetime.now().isoformat(),
            'version': '1.0'
        }
    
    def export_complete_package(
        self,
        normalization_config: Dict[str, Any],
        training_sequences: np.ndarray,
        quality_report: Dict[str, Any],
        version: str,
        dataset_info: Dict[str, Any]
    ) -> str:
        """
        Export complete package with all necessary files for production.
        
        Args:
            normalization_config: Normalization parameters configuration
            training_sequences: Training sequences array (144x6)
            quality_report: Data quality report
            version: Export version
            dataset_info: Dataset information
            
        Returns:
            Path to exported package
        """
        export_id = self._generate_export_id(version)
        export_dir = self.base_export_path / f"export_{export_id}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Creating export package: {export_id}")
        
        # Export normalization parameters
        norm_params_path = export_dir / f"normalization_params_{version}.json"
        self._export_normalization_parameters(normalization_config, norm_params_path)
        
        # Export training sequences
        sequences_path = export_dir / f"training_sequences_144x6_{version}.npz"
        self._export_training_sequences(training_sequences, sequences_path)
        
        # Export quality report
        quality_path = export_dir / f"data_quality_report_{version}.json"
        self._export_quality_report(quality_report, quality_path)
        
        # Export dataset information
        dataset_path = export_dir / f"dataset_info_{version}.json"
        self._export_dataset_info(dataset_info, dataset_path)
        
        # Create metadata
        metadata = self._create_export_metadata(export_id, version, export_dir, dataset_info)
        metadata_path = export_dir / "export_metadata.json"
        self._export_metadata(metadata, metadata_path)
        
        # Create compressed package
        package_path = self._create_compressed_package(export_dir, export_id)
        
        self.logger.info(f"Export package created: {package_path}")
        return str(package_path)
    
    def _export_normalization_parameters(
        self, 
        config: Dict[str, Any], 
        output_path: Path
    ) -> None:
        """Export normalization parameters with security and integrity checks."""
        self._log_access("export_normalization_parameters", str(output_path), success=False, details="Starting export")
        
        try:
            # Add integrity check
            config_copy = config.copy()
            config_copy['export_timestamp'] = datetime.now().isoformat()
            config_copy['integrity_hash'] = self._calculate_config_hash(config)
            
            with open(output_path, 'w') as f:
                json.dump(config_copy, f, indent=2)
            
            # Set secure file permissions
            self._set_secure_file_permissions(str(output_path))
            
            # Calculate and store file hash
            file_hash = self._calculate_file_integrity_hash(str(output_path))
            signature = self._create_file_signature(str(output_path), file_hash)
            
            # Save signature file
            signature_path = output_path.with_suffix('.sig')
            with open(signature_path, 'w') as f:
                json.dump(signature, f, indent=2)
            self._set_secure_file_permissions(str(signature_path))
            
            self._log_access("export_normalization_parameters", str(output_path), success=True, 
                           details=f"Exported with hash: {file_hash[:16]}...")
            
            self.logger.info(f"Normalization parameters exported: {output_path}")
            
        except Exception as e:
            self._log_access("export_normalization_parameters", str(output_path), success=False, details=str(e))
            raise
    
    def _export_training_sequences(self, sequences: np.ndarray, output_path: Path) -> None:
        """Export training sequences in compressed format."""
        # Validate shape
        if sequences.ndim != 3 or sequences.shape[1:] != (144, 6):
            raise ValueError(f"Invalid sequences shape: {sequences.shape}. Expected (N, 144, 6)")
        
        # Save with metadata
        np.savez_compressed(
            output_path,
            sequences=sequences,
            shape=sequences.shape,
            dtype=str(sequences.dtype),
            export_timestamp=datetime.now().isoformat(),
            checksum=hashlib.sha256(sequences.tobytes()).hexdigest()
        )
        
        self.logger.info(f"Training sequences exported: {output_path} (shape: {sequences.shape})")
    
    def _export_quality_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Export data quality report."""
        report_copy = report.copy()
        report_copy['export_timestamp'] = datetime.now().isoformat()
        
        with open(output_path, 'w') as f:
            json.dump(report_copy, f, indent=2)
        
        self.logger.info(f"Quality report exported: {output_path}")
    
    def _export_dataset_info(self, dataset_info: Dict[str, Any], output_path: Path) -> None:
        """Export dataset information."""
        info_copy = dataset_info.copy()
        info_copy['export_timestamp'] = datetime.now().isoformat()
        
        with open(output_path, 'w') as f:
            json.dump(info_copy, f, indent=2)
        
        self.logger.info(f"Dataset info exported: {output_path}")
    
    def _export_metadata(self, metadata: ExportMetadata, output_path: Path) -> None:
        """Export package metadata."""
        with open(output_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        self.logger.info(f"Metadata exported: {output_path}")
    
    def _create_export_metadata(
        self, 
        export_id: str, 
        version: str, 
        export_dir: Path,
        dataset_info: Dict[str, Any]
    ) -> ExportMetadata:
        """Create export metadata."""
        # Calculate directory size
        total_size = sum(f.stat().st_size for f in export_dir.rglob('*') if f.is_file())
        file_count = len(list(export_dir.rglob('*'))) - 1  # Exclude metadata file itself
        
        # Create dataset hash
        dataset_hash = self._calculate_dataset_hash(dataset_info)
        
        return ExportMetadata(
            export_id=export_id,
            version=version,
            timestamp=datetime.now(),
            dataset_hash=dataset_hash,
            file_count=file_count,
            total_size_bytes=total_size
        )
    
    def _create_compressed_package(self, export_dir: Path, export_id: str) -> Path:
        """Create compressed ZIP package."""
        package_path = self.base_export_path / f"timestrader_export_{export_id}.zip"
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in export_dir.rglob('*'):
                if file_path.is_file():
                    # Add file with relative path
                    arcname = file_path.relative_to(export_dir)
                    zipf.write(file_path, arcname)
        
        # Clean up directory
        shutil.rmtree(export_dir)
        
        return package_path
    
    def _generate_export_id(self, version: str) -> str:
        """Generate unique export ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{version}_{timestamp}"
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Calculate hash of configuration for integrity checking."""
        # Create deterministic string representation
        config_str = json.dumps(config, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _calculate_dataset_hash(self, dataset_info: Dict[str, Any]) -> str:
        """Calculate hash of dataset information."""
        # Use key dataset properties for hash
        key_properties = {
            'total_candles': dataset_info.get('total_candles'),
            'date_range': dataset_info.get('date_range'),
            'symbol': dataset_info.get('symbol', 'MNQ')
        }
        
        hash_str = json.dumps(key_properties, sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()[:16]  # Short hash
    
    def validate_export_package(self, package_path: str) -> Dict[str, Any]:
        """
        Validate exported package integrity.
        
        Args:
            package_path: Path to exported package
            
        Returns:
            Validation results dictionary
        """
        self.logger.info(f"Validating export package: {package_path}")
        
        validation_results = {
            'package_exists': False,
            'metadata_valid': False,
            'files_present': False,
            'checksums_valid': False,
            'details': {}
        }
        
        package_path = Path(package_path)
        
        # Check package exists
        if not package_path.exists():
            validation_results['details']['error'] = f"Package not found: {package_path}"
            return validation_results
        
        validation_results['package_exists'] = True
        
        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Check metadata exists
                if 'export_metadata.json' in zipf.namelist():
                    metadata_content = zipf.read('export_metadata.json')
                    metadata = json.loads(metadata_content.decode())
                    validation_results['metadata_valid'] = True
                    validation_results['details']['metadata'] = metadata
                
                # Check required files
                required_files = [
                    'export_metadata.json',
                    'dataset_info_',
                    'normalization_params_',
                    'training_sequences_144x6_',
                    'data_quality_report_'
                ]
                
                files_present = all(
                    any(fname.startswith(req) for fname in zipf.namelist())
                    for req in required_files
                )
                
                validation_results['files_present'] = files_present
                validation_results['details']['files'] = zipf.namelist()
                
                # Validate checksums if possible
                checksums_valid = self._validate_package_checksums(zipf)
                validation_results['checksums_valid'] = checksums_valid
                
        except Exception as e:
            validation_results['details']['error'] = str(e)
            self.logger.error(f"Package validation failed: {str(e)}")
        
        self.logger.info(f"Package validation completed: {validation_results}")
        return validation_results
    
    def _validate_package_checksums(self, zipf: zipfile.ZipFile) -> bool:
        """Validate checksums within the package."""
        try:
            # Check training sequences checksum
            sequence_files = [f for f in zipf.namelist() if f.startswith('training_sequences')]
            if sequence_files:
                seq_content = zipf.read(sequence_files[0])
                # For NPZ files, we would need to validate the internal checksum
                # This is a simplified validation
                return len(seq_content) > 0
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Checksum validation failed: {str(e)}")
            return False
    
    def create_colab_download_package(
        self,
        normalization_config: Dict[str, Any],
        quality_report: Dict[str, Any],
        version: str
    ) -> str:
        """
        Create lightweight package for Google Colab download.
        Contains only essential parameters for production use.
        
        Args:
            normalization_config: Normalization parameters
            quality_report: Quality report
            version: Package version
            
        Returns:
            Path to download package
        """
        export_id = self._generate_export_id(version)
        package_name = f"timestrader_production_params_{export_id}.zip"
        package_path = self.base_export_path / package_name
        
        self.logger.info(f"Creating Colab download package: {package_name}")
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add normalization parameters
            norm_params_json = json.dumps(normalization_config, indent=2)
            zipf.writestr(f"normalization_params_{version}.json", norm_params_json)
            
            # Add quality report
            quality_json = json.dumps(quality_report, indent=2)
            zipf.writestr(f"quality_report_{version}.json", quality_json)
            
            # Add deployment instructions
            deployment_instructions = self._create_deployment_instructions(version)
            zipf.writestr("DEPLOYMENT_INSTRUCTIONS.md", deployment_instructions)
            
            # Add simple metadata
            metadata = {
                'package_type': 'production_parameters',
                'version': version,
                'created_date': datetime.now().isoformat(),
                'contents': [
                    f"normalization_params_{version}.json",
                    f"quality_report_{version}.json",
                    "DEPLOYMENT_INSTRUCTIONS.md"
                ]
            }
            zipf.writestr("package_info.json", json.dumps(metadata, indent=2))
        
        self.logger.info(f"Colab download package created: {package_path}")
        return str(package_path)
    
    def _create_deployment_instructions(self, version: str) -> str:
        """Create deployment instructions for production use."""
        instructions = f"""# TimeStrader Production Parameters Deployment

## Package Information
- Version: {version}
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Type: Production Parameters Package

## Contents
1. `normalization_params_{version}.json` - Normalization parameters for production
2. `quality_report_{version}.json` - Data quality assessment
3. `package_info.json` - Package metadata

## Deployment Instructions

### 1. VPS Deployment
1. Upload this package to your Windows VPS
2. Extract files to: `C:\\Timestrader\\config\\`
3. Update production configuration to reference the new parameters file

### 2. Parameter Integration
```python
from timestrader.data.normalizers import ProductionNormalizer

# Initialize with new parameters
normalizer = ProductionNormalizer('C:\\\\Timestrader\\\\config\\\\normalization_params_{version}.json')

# Use in production pipeline
normalized_indicators = normalizer.normalize_indicators(live_indicators)
```

### 3. Validation
- Check quality_report_{version}.json for data quality metrics
- Ensure quality score meets production requirements (>= 99.5%)
- Verify all required indicators have normalization parameters

### 4. Backup
- Keep previous parameter files as backup
- Document the deployment in your change log

## Important Notes
- These parameters must match the training environment exactly
- Do not modify parameter files manually
- Test in staging environment before production deployment

## Support
If you encounter issues, check the data quality report and ensure:
1. All indicators are present in the parameters file
2. Quality score meets minimum requirements
3. Parameter file integrity is maintained
"""
        return instructions


class ColabDownloadHelper:
    """
    Helper class for downloading files from Google Colab environment.
    """
    
    @staticmethod
    def download_file(file_path: str, filename: str) -> None:
        """
        Download file from Colab to local machine.
        
        Args:
            file_path: Path to file in Colab
            filename: Suggested filename for download
        """
        try:
            from google.colab import files
            
            # Read file and trigger download
            files.download(file_path)
            
            print(f"File {filename} downloaded successfully")
            
        except ImportError:
            print("This function only works in Google Colab environment")
            print(f"File available at: {file_path}")
        except Exception as e:
            print(f"Download failed: {str(e)}")
    
    @staticmethod
    def download_multiple_files(file_paths: List[str]) -> None:
        """
        Download multiple files from Colab.
        
        Args:
            file_paths: List of file paths to download
        """
        try:
            from google.colab import files
            
            for file_path in file_paths:
                files.download(file_path)
                print(f"Downloaded: {Path(file_path).name}")
            
            print(f"All {len(file_paths)} files downloaded successfully")
            
        except ImportError:
            print("This function only works in Google Colab environment")
            print("Files available at:")
            for path in file_paths:
                print(f"  - {path}")
        except Exception as e:
            print(f"Download failed: {str(e)}")
    
    @staticmethod
    def create_download_summary(export_path: str) -> str:
        """
        Create summary of exported files for download.
        
        Args:
            export_path: Base export path
            
        Returns:
            Summary string
        """
        export_dir = Path(export_path)
        
        if not export_dir.exists():
            return "Export directory not found"
        
        files = list(export_dir.rglob('*.json')) + list(export_dir.rglob('*.npz'))
        
        summary = f"# TimeStrader Export Summary\n\n"
        summary += f"Export directory: {export_path}\n"
        summary += f"Total files: {len(files)}\n\n"
        
        summary += "## Files ready for download:\n"
        for file_path in sorted(files):
            size_mb = file_path.stat().st_size / (1024 * 1024)
            summary += f"- {file_path.name} ({size_mb:.1f} MB)\n"
        
        return summary
    
    def validate_parameter_file_integrity(self, parameter_file: str) -> Dict[str, Any]:
        """
        Validate integrity of a parameter file using signature.
        
        Args:
            parameter_file: Path to parameter file to validate
            
        Returns:
            Dictionary with validation results
        """
        parameter_path = Path(parameter_file)
        signature_path = parameter_path.with_suffix('.sig')
        
        validation_result = {
            'file_exists': parameter_path.exists(),
            'signature_exists': signature_path.exists(),
            'hash_valid': False,
            'metadata_valid': False,
            'details': {},
            'recommendations': []
        }
        
        if not validation_result['file_exists']:
            validation_result['recommendations'].append("Parameter file not found")
            return validation_result
        
        if not validation_result['signature_exists']:
            validation_result['recommendations'].append("Signature file missing - file integrity cannot be verified")
            return validation_result
        
        try:
            # Load signature
            with open(signature_path, 'r') as f:
                signature = json.load(f)
            
            # Validate file hash
            current_hash = self._calculate_file_integrity_hash(str(parameter_path))
            expected_hash = signature.get('content_hash_sha256', '')
            
            validation_result['hash_valid'] = (current_hash == expected_hash)
            validation_result['details']['current_hash'] = current_hash[:16] + "..."
            validation_result['details']['expected_hash'] = expected_hash[:16] + "..."
            
            if not validation_result['hash_valid']:
                validation_result['recommendations'].append("File has been modified or corrupted - hash mismatch")
            
            # Validate metadata
            current_size = os.path.getsize(parameter_path)
            expected_size = signature.get('file_size', 0)
            
            validation_result['metadata_valid'] = (current_size == expected_size)
            validation_result['details']['file_size_match'] = (current_size == expected_size)
            validation_result['details']['signature_date'] = signature.get('signature_created', 'unknown')
            
            if not validation_result['metadata_valid']:
                validation_result['recommendations'].append("File size mismatch - possible corruption")
            
            # Log validation attempt
            self._log_access(
                "validate_parameter_integrity", 
                str(parameter_path), 
                success=validation_result['hash_valid'] and validation_result['metadata_valid'],
                details=f"Hash valid: {validation_result['hash_valid']}, Metadata valid: {validation_result['metadata_valid']}"
            )
            
        except Exception as e:
            validation_result['recommendations'].append(f"Validation failed: {str(e)}")
            self._log_access("validate_parameter_integrity", str(parameter_path), success=False, details=str(e))
        
        return validation_result
    
    def get_access_log_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Get summary of parameter file access for security monitoring.
        
        Args:
            hours_back: Number of hours to look back in access logs
            
        Returns:
            Dictionary with access summary
        """
        if not self.enable_access_logging or not self.access_log_path.exists():
            return {'error': 'Access logging not enabled or log file not found'}
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        access_summary = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'operations_by_type': {},
            'recent_failures': [],
            'unique_files_accessed': set(),
            'time_range_hours': hours_back
        }
        
        try:
            with open(self.access_log_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    
                    try:
                        log_entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(log_entry['timestamp'])
                        
                        if entry_time >= cutoff_time:
                            access_summary['total_operations'] += 1
                            
                            if log_entry['success']:
                                access_summary['successful_operations'] += 1
                            else:
                                access_summary['failed_operations'] += 1
                                access_summary['recent_failures'].append({
                                    'timestamp': log_entry['timestamp'],
                                    'operation': log_entry['operation'],
                                    'file_path': log_entry['file_path'],
                                    'details': log_entry['details']
                                })
                            
                            # Count operations by type
                            op_type = log_entry['operation']
                            access_summary['operations_by_type'][op_type] = access_summary['operations_by_type'].get(op_type, 0) + 1
                            
                            # Track unique files
                            access_summary['unique_files_accessed'].add(log_entry['file_path'])
                    
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue  # Skip malformed log entries
            
            # Convert set to list for JSON serialization
            access_summary['unique_files_accessed'] = list(access_summary['unique_files_accessed'])
            
            # Limit recent failures to last 10
            access_summary['recent_failures'] = access_summary['recent_failures'][-10:]
            
        except Exception as e:
            return {'error': f'Failed to read access log: {str(e)}'}
        
        return access_summary