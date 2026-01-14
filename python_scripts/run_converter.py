# -*- coding: utf-8 -*-
"""
TSP Converter - Command Line Interface
======================================
Convert Excel/CSV files to LKH TSP format and back.

Usage:
    py -3 run_converter.py convert <input_file> [options]
    py -3 run_converter.py export <tour_file> --data <original_data> [options]
    py -3 run_converter.py --help
"""

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tsp_converter import ExcelToTSPConverter, TourToExcelConverter, detect_columns


def convert_to_tsp(args):
    """Convert Excel/CSV to TSP format."""
    print("=" * 60)
    print("TSP CONVERTER - Excel/CSV → LKH TSP")
    print("=" * 60)
    
    # Determine output directory
    output_dir = args.output_dir or os.path.dirname(os.path.abspath(args.input_file)) or '.'
    
    # Create converter
    converter = ExcelToTSPConverter(
        input_path=args.input_file,
        id_col=args.id_col,
        lat_col=args.lat_col,
        lon_col=args.lon_col,
        scale=args.scale
    )
    
    # Perform conversion
    tsp_path, par_path = converter.convert(output_dir, args.name)
    
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  TSP: {tsp_path}")
    print(f"  PAR: {par_path}")
    print(f"\nTo run LKH:")
    print(f"  .\\LKH.exe {par_path}")
    

def export_to_excel(args):
    """Export tour file to Excel/CSV."""
    print("=" * 60)
    print("TSP CONVERTER - LKH Tour → Excel/CSV")
    print("=" * 60)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(args.tour_file)[0]
        output_path = base + '_result.' + args.format
    
    # Create converter
    converter = TourToExcelConverter(
        tour_path=args.tour_file,
        original_data_path=args.data,
        id_col=args.id_col,
        lat_col=args.lat_col,
        lon_col=args.lon_col
    )
    
    # Generate output
    result_path, response_path = converter.generate_output(output_path, args.format)
    
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  Full results: {result_path}")
    print(f"  Response only: {response_path}")


def auto_detect_and_show(args):
    """Auto-detect columns in input file."""
    import pandas as pd
    
    print("=" * 60)
    print("AUTO-DETECT COLUMNS")
    print("=" * 60)
    
    ext = os.path.splitext(args.input_file)[1].lower()
    if ext in ['.xlsx', '.xls']:
        df = pd.read_excel(args.input_file)
    else:
        df = pd.read_csv(args.input_file)
    
    print(f"\nFile: {args.input_file}")
    print(f"Shape: {df.shape}")
    print(f"\nColumns found:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. '{col}' ({df[col].dtype})")
    
    id_col, lat_col, lon_col = detect_columns(df)
    print(f"\nAuto-detected:")
    print(f"  ID column: '{id_col}'")
    print(f"  Latitude column: '{lat_col}'")
    print(f"  Longitude column: '{lon_col}'")
    
    if lat_col and lon_col:
        print(f"\nSuggested command:")
        print(f"  py -3 run_converter.py convert \"{args.input_file}\" --id-col \"{id_col}\" --lat-col \"{lat_col}\" --lon-col \"{lon_col}\"")


def main():
    parser = argparse.ArgumentParser(
        description='TSP Converter - Convert Excel/CSV ↔ LKH TSP format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert Excel to TSP (with explicit columns)
  py -3 run_converter.py convert data.xlsx --id-col commune --lat-col latitude --lon-col longitude
  
  # Auto-detect columns
  py -3 run_converter.py detect data.xlsx
  
  # Export tour to Excel
  py -3 run_converter.py export solution.tour --data data.xlsx --format xlsx
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert Excel/CSV to TSP format')
    convert_parser.add_argument('input_file', help='Input Excel (.xlsx) or CSV file')
    convert_parser.add_argument('--output-dir', '-o', help='Output directory (default: same as input)')
    convert_parser.add_argument('--name', '-n', help='Problem name (default: derived from filename)')
    convert_parser.add_argument('--id-col', default='commune', help='ID column name (default: commune)')
    convert_parser.add_argument('--lat-col', default='latitude', help='Latitude column name (default: latitude)')
    convert_parser.add_argument('--lon-col', default='longitude', help='Longitude column name (default: longitude)')
    convert_parser.add_argument('--scale', type=int, default=10000, help='Distance scaling factor (default: 10000)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export tour file to Excel/CSV')
    export_parser.add_argument('tour_file', help='LKH tour file (.tour)')
    export_parser.add_argument('--data', '-d', required=True, help='Original data file (Excel/CSV)')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--format', '-f', choices=['xlsx', 'csv'], default='xlsx', help='Output format')
    export_parser.add_argument('--id-col', default='commune', help='ID column name')
    export_parser.add_argument('--lat-col', default='latitude', help='Latitude column name')
    export_parser.add_argument('--lon-col', default='longitude', help='Longitude column name')
    
    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Auto-detect columns in input file')
    detect_parser.add_argument('input_file', help='Input file to analyze')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        convert_to_tsp(args)
    elif args.command == 'export':
        export_to_excel(args)
    elif args.command == 'detect':
        auto_detect_and_show(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
