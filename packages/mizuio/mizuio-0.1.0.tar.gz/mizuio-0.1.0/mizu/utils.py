"""
Utility functions for the Mizu tool.
"""

import pandas as pd
import numpy as np
import json
import csv
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import logging


class DataUtils:
    """
    A utility class providing various data processing and file handling functions.
    
    Includes methods for data loading, saving, validation, and transformation.
    """
    
    def __init__(self):
        """Initialize the DataUtils class."""
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('mizu_utils')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_data(self, file_path: str, 
                  file_type: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from various file formats.
        
        Args:
            file_path: Path to the data file
            file_type: Type of file ('csv', 'json', 'excel', 'parquet', 'pickle')
                       If None, will be inferred from file extension
            
        Returns:
            pandas DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_type is None:
            file_type = file_path.suffix.lower().lstrip('.')
        
        try:
            if file_type in ['csv', 'txt']:
                return pd.read_csv(file_path)
            elif file_type == 'json':
                return pd.read_json(file_path)
            elif file_type in ['xlsx', 'xls']:
                return pd.read_excel(file_path)
            elif file_type == 'parquet':
                return pd.read_parquet(file_path)
            elif file_type == 'pickle':
                return pd.read_pickle(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def save_data(self, data: pd.DataFrame, file_path: str,
                  file_type: Optional[str] = None, **kwargs) -> None:
        """
        Save data to various file formats.
        
        Args:
            data: pandas DataFrame to save
            file_path: Output file path
            file_type: Type of file ('csv', 'json', 'excel', 'parquet', 'pickle')
                       If None, will be inferred from file extension
            **kwargs: Additional arguments for the save function
        """
        file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_type is None:
            file_type = file_path.suffix.lower().lstrip('.')
        
        try:
            if file_type == 'csv':
                data.to_csv(file_path, index=False, **kwargs)
            elif file_type == 'json':
                data.to_json(file_path, orient='records', **kwargs)
            elif file_type in ['xlsx', 'xls']:
                data.to_excel(file_path, index=False, **kwargs)
            elif file_type == 'parquet':
                data.to_parquet(file_path, **kwargs)
            elif file_type == 'pickle':
                data.to_pickle(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            self.logger.info(f"Data saved successfully to {file_path}")
        
        except Exception as e:
            self.logger.error(f"Error saving file {file_path}: {e}")
            raise
    
    def get_data_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive information about a DataFrame.
        
        Args:
            data: pandas DataFrame
            
        Returns:
            Dictionary containing data information
        """
        info = {
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'memory_usage': data.memory_usage(deep=True).sum(),
            'missing_values': data.isnull().sum().to_dict(),
            'missing_percentage': (data.isnull().sum() / len(data) * 100).to_dict(),
            'numeric_columns': list(data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(data.select_dtypes(include=['object']).columns),
            'datetime_columns': list(data.select_dtypes(include=['datetime']).columns),
            'duplicates': data.duplicated().sum(),
            'unique_counts': {col: data[col].nunique() for col in data.columns}
        }
        
        return info
    
    def validate_data(self, data: pd.DataFrame, 
                     required_columns: Optional[List[str]] = None,
                     data_types: Optional[Dict[str, str]] = None,
                     value_ranges: Optional[Dict[str, Tuple[Any, Any]]] = None) -> Dict[str, Any]:
        """
        Validate data against specified criteria.
        
        Args:
            data: pandas DataFrame to validate
            required_columns: List of required column names
            data_types: Dictionary mapping column names to expected data types
            value_ranges: Dictionary mapping column names to (min, max) value ranges
            
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required columns
        if required_columns:
            missing_columns = set(required_columns) - set(data.columns)
            if missing_columns:
                validation_results['is_valid'] = False
                validation_results['errors'].append(
                    f"Missing required columns: {list(missing_columns)}"
                )
        
        # Check data types
        if data_types:
            for column, expected_type in data_types.items():
                if column in data.columns:
                    actual_type = str(data[column].dtype)
                    if actual_type != expected_type:
                        validation_results['warnings'].append(
                            f"Column '{column}' has type '{actual_type}', expected '{expected_type}'"
                        )
        
        # Check value ranges
        if value_ranges:
            for column, (min_val, max_val) in value_ranges.items():
                if column in data.columns:
                    if data[column].min() < min_val or data[column].max() > max_val:
                        validation_results['warnings'].append(
                            f"Column '{column}' has values outside expected range [{min_val}, {max_val}]"
                        )
        
        return validation_results
    
    def sample_data(self, data: pd.DataFrame, 
                   sample_size: Union[int, float],
                   method: str = 'random',
                   seed: Optional[int] = None) -> pd.DataFrame:
        """
        Create a sample from the dataset.
        
        Args:
            data: pandas DataFrame
            sample_size: Number of rows or fraction of data
            method: Sampling method ('random', 'systematic', 'stratified')
            seed: Random seed for reproducibility
            
        Returns:
            Sampled pandas DataFrame
        """
        if seed is not None:
            np.random.seed(seed)
        
        if method == 'random':
            if isinstance(sample_size, float):
                return data.sample(frac=sample_size, random_state=seed)
            else:
                return data.sample(n=sample_size, random_state=seed)
        
        elif method == 'systematic':
            if isinstance(sample_size, float):
                step = int(1 / sample_size)
            else:
                step = len(data) // sample_size
            
            indices = range(0, len(data), step)
            return data.iloc[indices]
        
        elif method == 'stratified':
            # This is a simplified stratified sampling
            # In practice, you'd need to specify the stratification column
            return data.sample(n=sample_size, random_state=seed)
        
        else:
            raise ValueError(f"Unknown sampling method: {method}")
    
    def split_data(self, data: pd.DataFrame,
                   target_column: str,
                   test_size: float = 0.2,
                   validation_size: float = 0.0,
                   random_state: Optional[int] = None) -> Tuple[pd.DataFrame, ...]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            data: pandas DataFrame
            target_column: Name of the target column
            test_size: Fraction of data for test set
            validation_size: Fraction of data for validation set
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (train_data, test_data) or (train_data, val_data, test_data)
        """
        from sklearn.model_selection import train_test_split
        
        if validation_size > 0:
            # Split into train+val and test
            train_val, test = train_test_split(
                data, test_size=test_size, random_state=random_state
            )
            
            # Split train+val into train and val
            train, val = train_test_split(
                train_val, test_size=validation_size/(1-test_size), random_state=random_state
            )
            
            return train, val, test
        else:
            train, test = train_test_split(
                data, test_size=test_size, random_state=random_state
            )
            return train, test
    
    def encode_categorical(self, data: pd.DataFrame,
                          columns: Optional[List[str]] = None,
                          method: str = 'label',
                          drop_first: bool = False) -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Args:
            data: pandas DataFrame
            columns: List of categorical columns to encode
            method: Encoding method ('label', 'onehot', 'ordinal')
            drop_first: Whether to drop first category in one-hot encoding
            
        Returns:
            DataFrame with encoded categorical variables
        """
        if columns is None:
            columns = list(data.select_dtypes(include=['object']).columns)
        
        data_encoded = data.copy()
        
        if method == 'label':
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            for col in columns:
                if col in data_encoded.columns:
                    data_encoded[col] = le.fit_transform(data_encoded[col].astype(str))
        
        elif method == 'onehot':
            data_encoded = pd.get_dummies(data_encoded, columns=columns, drop_first=drop_first)
        
        elif method == 'ordinal':
            # Simple ordinal encoding based on value frequency
            for col in columns:
                if col in data_encoded.columns:
                    value_counts = data_encoded[col].value_counts()
                    value_map = {val: idx for idx, val in enumerate(value_counts.index)}
                    data_encoded[col] = data_encoded[col].map(value_map)
        
        return data_encoded
    
    def scale_features(self, data: pd.DataFrame,
                      columns: Optional[List[str]] = None,
                      method: str = 'standard',
                      return_scaler: bool = False) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Any]]:
        """
        Scale numerical features.
        
        Args:
            data: pandas DataFrame
            columns: List of numerical columns to scale
            method: Scaling method ('standard', 'minmax', 'robust')
            return_scaler: Whether to return the fitted scaler
            
        Returns:
            DataFrame with scaled features and optionally the scaler
        """
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
        
        if columns is None:
            columns = list(data.select_dtypes(include=[np.number]).columns)
        
        data_scaled = data.copy()
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        data_scaled[columns] = scaler.fit_transform(data_scaled[columns])
        
        if return_scaler:
            return data_scaled, scaler
        else:
            return data_scaled
    
    def create_summary_report(self, data: pd.DataFrame,
                             output_file: Optional[str] = None) -> str:
        """
        Create a comprehensive data summary report.
        
        Args:
            data: pandas DataFrame
            output_file: Optional file path to save the report
            
        Returns:
            Report as string
        """
        info = self.get_data_info(data)
        
        report = []
        report.append("=" * 50)
        report.append("DATA SUMMARY REPORT")
        report.append("=" * 50)
        report.append(f"Dataset Shape: {info['shape']}")
        report.append(f"Memory Usage: {info['memory_usage'] / 1024**2:.2f} MB")
        report.append(f"Duplicate Rows: {info['duplicates']}")
        report.append("")
        
        report.append("COLUMN INFORMATION:")
        report.append("-" * 30)
        for col in data.columns:
            dtype = info['dtypes'][col]
            missing = info['missing_values'][col]
            missing_pct = info['missing_percentage'][col]
            unique = info['unique_counts'][col]
            
            report.append(f"{col}:")
            report.append(f"  Type: {dtype}")
            report.append(f"  Missing: {missing} ({missing_pct:.1f}%)")
            report.append(f"  Unique Values: {unique}")
            
            if dtype in ['int64', 'float64']:
                report.append(f"  Min: {data[col].min()}")
                report.append(f"  Max: {data[col].max()}")
                report.append(f"  Mean: {data[col].mean():.2f}")
                report.append(f"  Std: {data[col].std():.2f}")
            
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self.logger.info(f"Report saved to {output_file}")
        
        return report_text
