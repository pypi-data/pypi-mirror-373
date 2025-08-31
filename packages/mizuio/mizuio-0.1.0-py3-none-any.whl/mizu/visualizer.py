"""
Data visualization utilities for the Mizu tool.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional, Union, Tuple
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore')


class DataVisualizer:
    """
    A comprehensive data visualization utility class.
    
    Provides methods for creating various types of plots and charts
    with customizable styling and themes.
    """
    
    def __init__(self, data: Optional[Union[pd.DataFrame, pd.Series]] = None,
                 style: str = 'default', figsize: Tuple[int, int] = (10, 6)):
        """
        Initialize the DataVisualizer.
        
        Args:
            data: Optional pandas DataFrame or Series to work with
            style: Matplotlib style to use
            figsize: Default figure size (width, height)
        """
        self.data = data
        self.style = style
        self.figsize = figsize
        self._setup_style()
    
    def _setup_style(self):
        """Setup the plotting style."""
        try:
            plt.style.use(self.style)
        except:
            plt.style.use('default')
        
        # Set default figure size
        plt.rcParams['figure.figsize'] = self.figsize
        plt.rcParams['font.size'] = 10
    
    def load_data(self, data: Union[pd.DataFrame, pd.Series]) -> 'DataVisualizer':
        """
        Load data into the visualizer.
        
        Args:
            data: pandas DataFrame or Series
            
        Returns:
            self for method chaining
        """
        self.data = data
        return self
    
    def histogram(self, column: str, bins: int = 30, 
                 title: Optional[str] = None,
                 figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a histogram for a numeric column.
        
        Args:
            column: Column name to plot
            bins: Number of bins
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        ax.hist(self.data[column].dropna(), bins=bins, alpha=0.7, edgecolor='black')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.set_title(title or f'Histogram of {column}')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def boxplot(self, column: str, by: Optional[str] = None,
                title: Optional[str] = None,
                figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a boxplot for a numeric column.
        
        Args:
            column: Column name to plot
            by: Column to group by
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        if by:
            self.data.boxplot(column=column, by=by, ax=ax)
        else:
            ax.boxplot(self.data[column].dropna())
            ax.set_xticklabels([column])
        
        ax.set_title(title or f'Boxplot of {column}')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def scatter_plot(self, x: str, y: str, 
                    color: Optional[str] = None,
                    size: Optional[str] = None,
                    title: Optional[str] = None,
                    figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a scatter plot.
        
        Args:
            x: X-axis column name
            y: Y-axis column name
            color: Column name for color coding
            size: Column name for point size
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        scatter = ax.scatter(self.data[x], self.data[y], 
                           c=self.data[color] if color else None,
                           s=self.data[size] if size else 50,
                           alpha=0.6)
        
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(title or f'Scatter Plot: {x} vs {y}')
        ax.grid(True, alpha=0.3)
        
        if color:
            plt.colorbar(scatter, ax=ax, label=color)
        
        return fig
    
    def correlation_heatmap(self, columns: Optional[List[str]] = None,
                           title: Optional[str] = None,
                           figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a correlation heatmap.
        
        Args:
            columns: List of columns to include (numeric only)
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        # Select numeric columns
        if columns:
            data_subset = self.data[columns].select_dtypes(include=[np.number])
        else:
            data_subset = self.data.select_dtypes(include=[np.number])
        
        corr_matrix = data_subset.corr()
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, ax=ax)
        
        ax.set_title(title or 'Correlation Heatmap')
        
        return fig
    
    def bar_plot(self, x: str, y: Optional[str] = None,
                 title: Optional[str] = None,
                 figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a bar plot.
        
        Args:
            x: X-axis column name
            y: Y-axis column name (if None, counts are used)
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        if y:
            self.data.plot(kind='bar', x=x, y=y, ax=ax)
        else:
            self.data[x].value_counts().plot(kind='bar', ax=ax)
        
        ax.set_title(title or f'Bar Plot: {x}')
        ax.set_xlabel(x)
        ax.set_ylabel(y or 'Count')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def line_plot(self, x: str, y: str,
                  title: Optional[str] = None,
                  figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a line plot.
        
        Args:
            x: X-axis column name
            y: Y-axis column name
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        self.data.plot(kind='line', x=x, y=y, ax=ax, marker='o')
        
        ax.set_title(title or f'Line Plot: {y} over {x}')
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def pair_plot(self, columns: Optional[List[str]] = None,
                  hue: Optional[str] = None,
                  title: Optional[str] = None) -> plt.Figure:
        """
        Create a pair plot for multiple variables.
        
        Args:
            columns: List of columns to include
            hue: Column name for color coding
            title: Plot title
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        if columns:
            data_subset = self.data[columns]
        else:
            data_subset = self.data.select_dtypes(include=[np.number])
        
        fig = sns.pairplot(data_subset, hue=hue, diag_kind='hist')
        
        if title:
            fig.fig.suptitle(title, y=1.02)
        
        return fig.fig
    
    def missing_values_plot(self, title: Optional[str] = None,
                           figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a plot showing missing values in the dataset.
        
        Args:
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        missing_data = self.data.isnull().sum()
        missing_percent = (missing_data / len(self.data)) * 100
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize or (15, 6))
        
        # Bar plot of missing values
        missing_data.plot(kind='bar', ax=ax1)
        ax1.set_title('Missing Values Count')
        ax1.set_xlabel('Columns')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)
        
        # Percentage plot
        missing_percent.plot(kind='bar', ax=ax2)
        ax2.set_title('Missing Values Percentage')
        ax2.set_xlabel('Columns')
        ax2.set_ylabel('Percentage')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if title:
            fig.suptitle(title, y=1.02)
        
        return fig
    
    def distribution_plot(self, column: str,
                         title: Optional[str] = None,
                         figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a distribution plot (histogram + KDE).
        
        Args:
            column: Column name to plot
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure object
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize)
        
        sns.histplot(self.data[column].dropna(), kde=True, ax=ax)
        
        ax.set_title(title or f'Distribution of {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Density')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def save_plot(self, fig: plt.Figure, filename: str, 
                  dpi: int = 300, bbox_inches: str = 'tight'):
        """
        Save a plot to file.
        
        Args:
            fig: matplotlib Figure object
            filename: Output filename
            dpi: DPI for the saved image
            bbox_inches: Bounding box setting
        """
        fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        plt.close(fig)
    
    def show_plot(self, fig: plt.Figure):
        """
        Display a plot.
        
        Args:
            fig: matplotlib Figure object
        """
        plt.show()
        plt.close(fig)
