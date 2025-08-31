"""
Tests for the DataCleaner class.
"""

import unittest
import pandas as pd
import numpy as np
from mizuio.cleaner import DataCleaner


class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner class."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample data with various issues
        self.sample_data = pd.DataFrame({
            'id': [1, 2, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 30, np.nan, 35, 40],
            'salary': [50000, 60000, 60000, 70000, 80000, 90000],
            'department': ['IT', 'HR', 'HR', 'IT', 'Finance', 'IT'],
            'score': [85, 90, 90, 88, 92, 95]
        })
        
        self.cleaner = DataCleaner()
    
    def test_load_data(self):
        """Test loading data into cleaner."""
        self.cleaner.load_data(self.sample_data)
        self.assertIsNotNone(self.cleaner.data)
        self.assertEqual(len(self.cleaner.data), 6)
        self.assertEqual(len(self.cleaner.original_data), 6)
    
    def test_remove_duplicates(self):
        """Test removing duplicate rows."""
        self.cleaner.load_data(self.sample_data)
        self.cleaner.remove_duplicates()
        
        # Should remove one duplicate row (id=2, name='Bob')
        self.assertEqual(len(self.cleaner.data), 5)
    
    def test_remove_duplicates_subset(self):
        """Test removing duplicates based on specific columns."""
        self.cleaner.load_data(self.sample_data)
        self.cleaner.remove_duplicates(subset=['name'])
        
        # Should remove duplicate names
        self.assertEqual(len(self.cleaner.data), 5)
    
    def test_handle_missing_values_drop(self):
        """Test dropping missing values."""
        self.cleaner.load_data(self.sample_data)
        self.cleaner.handle_missing_values(strategy='drop')
        
        # Should remove row with missing age
        self.assertEqual(len(self.cleaner.data), 5)
    
    def test_handle_missing_values_fill(self):
        """Test filling missing values."""
        self.cleaner.load_data(self.sample_data)
        self.cleaner.handle_missing_values(strategy='fill', columns=['age'])
        
        # Should fill missing age with mean
        self.assertFalse(self.cleaner.data['age'].isnull().any())
    
    def test_handle_missing_values_fill_value(self):
        """Test filling missing values with specific value."""
        self.cleaner.load_data(self.sample_data)
        self.cleaner.handle_missing_values(strategy='fill', fill_value=0)
        
        # Should fill all missing values with 0
        self.assertFalse(self.cleaner.data.isnull().any().any())
    
    def test_convert_data_types(self):
        """Test converting data types."""
        self.cleaner.load_data(self.sample_data)
        type_mapping = {'id': 'int64', 'age': 'float64'}
        self.cleaner.convert_data_types(type_mapping)
        
        self.assertEqual(self.cleaner.data['id'].dtype, 'int64')
        self.assertEqual(self.cleaner.data['age'].dtype, 'float64')
    
    def test_remove_outliers_iqr(self):
        """Test removing outliers using IQR method."""
        # Create data with outliers
        outlier_data = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is an outlier
        })
        
        self.cleaner.load_data(outlier_data)
        self.cleaner.remove_outliers(columns=['values'], method='iqr')
        
        # Should remove the outlier (100)
        self.assertEqual(len(self.cleaner.data), 9)
        self.assertNotIn(100, self.cleaner.data['values'].values)
    
    def test_remove_outliers_zscore(self):
        """Test removing outliers using z-score method."""
        # Create data with outliers
        outlier_data = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is an outlier
        })
        
        self.cleaner.load_data(outlier_data)
        self.cleaner.remove_outliers(columns=['values'], method='zscore', threshold=2)
        
        # Should remove the outlier (100)
        self.assertEqual(len(self.cleaner.data), 9)
        self.assertNotIn(100, self.cleaner.data['values'].values)
    
    def test_normalize_text(self):
        """Test text normalization."""
        text_data = pd.DataFrame({
            'text': ['  Hello World  ', '  PYTHON  ', '  Data Science  ']
        })
        
        self.cleaner.load_data(text_data)
        self.cleaner.normalize_text(columns=['text'])
        
        expected = ['hello world', 'python', 'data science']
        self.assertEqual(list(self.cleaner.data['text']), expected)
    
    def test_get_cleaning_summary(self):
        """Test getting cleaning summary."""
        self.cleaner.load_data(self.sample_data)
        self.cleaner.remove_duplicates()
        self.cleaner.handle_missing_values(strategy='drop')
        
        summary = self.cleaner.get_cleaning_summary()
        
        self.assertIn('original_rows', summary)
        self.assertIn('current_rows', summary)
        self.assertIn('rows_removed', summary)
        self.assertEqual(summary['original_rows'], 6)
        self.assertEqual(summary['current_rows'], 4)  # 2 rows removed
        self.assertEqual(summary['rows_removed'], 2)
    
    def test_reset(self):
        """Test resetting data to original state."""
        self.cleaner.load_data(self.sample_data)
        original_length = len(self.cleaner.data)
        
        self.cleaner.remove_duplicates()
        self.assertLess(len(self.cleaner.data), original_length)
        
        self.cleaner.reset()
        self.assertEqual(len(self.cleaner.data), original_length)
    
    def test_get_data(self):
        """Test getting cleaned data."""
        self.cleaner.load_data(self.sample_data)
        data = self.cleaner.get_data()
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 6)
    
    def test_no_data_loaded_error(self):
        """Test error when no data is loaded."""
        with self.assertRaises(ValueError):
            self.cleaner.remove_duplicates()
        
        with self.assertRaises(ValueError):
            self.cleaner.handle_missing_values()
        
        with self.assertRaises(ValueError):
            self.cleaner.convert_data_types({})
    
    def test_chaining(self):
        """Test method chaining."""
        result = (self.cleaner
                 .load_data(self.sample_data)
                 .remove_duplicates()
                 .handle_missing_values(strategy='fill'))
        
        self.assertIsInstance(result, DataCleaner)
        self.assertEqual(len(result.data), 5)  # One duplicate removed


if __name__ == '__main__':
    unittest.main()
