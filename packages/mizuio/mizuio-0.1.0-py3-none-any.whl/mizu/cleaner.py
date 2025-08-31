"""
Data cleaning utilities for the Mizu tool.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union


class DataCleaner:
    """
    A comprehensive data cleaning utility class.
    
    Provides methods for handling missing values, duplicates,
    data type conversions, and data validation.
    """
    
    def __init__(self, data: Optional[Union[pd.DataFrame, pd.Series]] = None):
        """
        Initialize the DataCleaner.
        
        Args:
            data: Optional pandas DataFrame or Series to work with
        """
        self.data = data
        self.original_data = data.copy() if data is not None else None
    
    def load_data(self, data: Union[pd.DataFrame, pd.Series]) -> 'DataCleaner':
        """
        Load data into the cleaner.
        
        Args:
            data: pandas DataFrame or Series
            
        Returns:
            self for method chaining
        """
        self.data = data
        self.original_data = data.copy()
        return self
    
    def remove_duplicates(self, subset: Optional[List[str]] = None, 
                         keep: str = 'first') -> 'DataCleaner':
        """
        Remove duplicate rows from the dataset.
        
        Args:
            subset: Column names to consider for duplicates
            keep: Which duplicates to keep ('first', 'last', False)
            
        Returns:
            self for method chaining
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        self.data = self.data.drop_duplicates(subset=subset, keep=keep)
        return self
    
    def handle_missing_values(self, strategy: str = 'drop', 
                            fill_value: Any = None,
                            columns: Optional[List[str]] = None) -> 'DataCleaner':
        """
        Handle missing values in the dataset.
        
        Args:
            strategy: 'drop', 'fill', or 'interpolate'
            fill_value: Value to fill missing values with
            columns: Specific columns to apply the strategy to
            
        Returns:
            self for method chaining
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        target_data = self.data[columns] if columns else self.data
        
        if strategy == 'drop':
            self.data = self.data.dropna(subset=columns)
        elif strategy == 'fill':
            if fill_value is not None:
                self.data = self.data.fillna(fill_value)
            else:
                # Use appropriate fill methods based on data type
                for col in target_data.columns:
                    if target_data[col].dtype in ['int64', 'float64']:
                        self.data[col] = self.data[col].fillna(self.data[col].mean())
                    else:
                        self.data[col] = self.data[col].fillna(self.data[col].mode()[0])
        elif strategy == 'interpolate':
            self.data = self.data.interpolate()
        
        return self
    
    def convert_data_types(self, type_mapping: Dict[str, str]) -> 'DataCleaner':
        """
        Convert data types of specified columns.
        
        Args:
            type_mapping: Dictionary mapping column names to target data types
            
        Returns:
            self for method chaining
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        for column, dtype in type_mapping.items():
            if column in self.data.columns:
                try:
                    self.data[column] = self.data[column].astype(dtype)
                except Exception as e:
                    print(f"Warning: Could not convert {column} to {dtype}: {e}")
        
        return self
    
    def remove_outliers(self, columns: List[str], 
                       method: str = 'iqr',
                       threshold: float = 1.5) -> 'DataCleaner':
        """
        Remove outliers from specified columns.
        
        Args:
            columns: List of column names to process
            method: 'iqr' (Interquartile Range) or 'zscore'
            threshold: Threshold for outlier detection
            
        Returns:
            self for method chaining
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        for column in columns:
            if column not in self.data.columns:
                continue
                
            if method == 'iqr':
                Q1 = self.data[column].quantile(0.25)
                Q3 = self.data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                self.data = self.data[
                    (self.data[column] >= lower_bound) & 
                    (self.data[column] <= upper_bound)
                ]
            
            elif method == 'zscore':
                z_scores = np.abs((self.data[column] - self.data[column].mean()) / 
                                self.data[column].std())
                self.data = self.data[z_scores < threshold]
        
        return self
    
    def normalize_text(self, columns: List[str]) -> 'DataCleaner':
        """
        Normalize text data in specified columns.
        
        Args:
            columns: List of text column names to normalize
            
        Returns:
            self for method chaining
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        for column in columns:
            if column in self.data.columns:
                # Convert to string, lowercase, and strip whitespace
                self.data[column] = (self.data[column]
                                   .astype(str)
                                   .str.lower()
                                   .str.strip())
        
        return self
    
    def get_cleaning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the cleaning operations performed.
        
        Returns:
            Dictionary containing cleaning statistics
        """
        if self.data is None or self.original_data is None:
            return {}
        
        summary = {
            'original_rows': len(self.original_data),
            'current_rows': len(self.data),
            'rows_removed': len(self.original_data) - len(self.data),
            'missing_values': self.data.isnull().sum().to_dict(),
            'duplicates_removed': len(self.original_data) - len(self.original_data.drop_duplicates())
        }
        
        return summary
    
    def reset(self) -> 'DataCleaner':
        """
        Reset data to original state.
        
        Returns:
            self for method chaining
        """
        if self.original_data is not None:
            self.data = self.original_data.copy()
        return self
    
    def get_data(self) -> Union[pd.DataFrame, pd.Series]:
        """
        Get the cleaned data.
        
        Returns:
            The cleaned pandas DataFrame or Series
        """
        return self.data
