"""
Command line interface for Mizu.
"""

import argparse
import sys
import pandas as pd
from pathlib import Path

from .cleaner import DataCleaner
from .visualizer import DataVisualizer
from .utils import DataUtils


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Mizu - Python Data Processing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mizu clean data.csv --output cleaned_data.csv
  mizu visualize data.csv --plot histogram --column age
  mizu info data.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean data')
    clean_parser.add_argument('input', help='Input file path')
    clean_parser.add_argument('--output', '-o', help='Output file path')
    clean_parser.add_argument('--remove-duplicates', action='store_true', help='Remove duplicate rows')
    clean_parser.add_argument('--fill-missing', action='store_true', help='Fill missing values')
    clean_parser.add_argument('--remove-outliers', action='store_true', help='Remove outliers')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Visualize data')
    viz_parser.add_argument('input', help='Input file path')
    viz_parser.add_argument('--plot', choices=['histogram', 'boxplot', 'scatter', 'correlation'], 
                           help='Type of plot')
    viz_parser.add_argument('--column', help='Column to plot')
    viz_parser.add_argument('--output', '-o', help='Output image file')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get data information')
    info_parser.add_argument('input', help='Input file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        utils = DataUtils()
        
        if args.command == 'clean':
            # Load data
            data = utils.load_data(args.input)
            print(f"Loaded data: {data.shape}")
            
            # Clean data
            cleaner = DataCleaner(data)
            
            if args.remove_duplicates:
                cleaner.remove_duplicates()
                print("Removed duplicates")
            
            if args.fill_missing:
                cleaner.handle_missing_values(strategy='fill')
                print("Filled missing values")
            
            if args.remove_outliers:
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    cleaner.remove_outliers(columns=numeric_cols)
                    print(f"Removed outliers from columns: {numeric_cols}")
            
            # Save cleaned data
            output_path = args.output or f"cleaned_{Path(args.input).name}"
            utils.save_data(cleaner.get_data(), output_path)
            print(f"Saved cleaned data to: {output_path}")
            
        elif args.command == 'visualize':
            # Load data
            data = utils.load_data(args.input)
            print(f"Loaded data: {data.shape}")
            
            # Create visualizer
            visualizer = DataVisualizer(data)
            
            if args.plot == 'histogram':
                if not args.column:
                    print("Error: --column is required for histogram plot")
                    return
                fig = visualizer.histogram(args.column)
                output = args.output or f"{args.column}_histogram.png"
                visualizer.save_plot(fig, output)
                print(f"Saved histogram to: {output}")
                
            elif args.plot == 'correlation':
                fig = visualizer.correlation_heatmap()
                output = args.output or "correlation_heatmap.png"
                visualizer.save_plot(fig, output)
                print(f"Saved correlation heatmap to: {output}")
                
            else:
                print("Plot type not implemented yet")
                
        elif args.command == 'info':
            # Load data
            data = utils.load_data(args.input)
            
            # Get info
            info = utils.get_data_info(data)
            
            print("=" * 50)
            print("DATA INFORMATION")
            print("=" * 50)
            print(f"Shape: {info['shape']}")
            print(f"Memory Usage: {info['memory_usage'] / 1024**2:.2f} MB")
            print(f"Columns: {len(info['columns'])}")
            print(f"Missing Values: {sum(info['missing_values'].values())}")
            print(f"Duplicate Rows: {info['duplicates']}")
            print()
            
            print("COLUMN TYPES:")
            for col, dtype in info['dtypes'].items():
                missing = info['missing_values'][col]
                print(f"  {col}: {dtype} (missing: {missing})")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
