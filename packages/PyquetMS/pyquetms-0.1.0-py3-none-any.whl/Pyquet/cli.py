#!/usr/bin/env python3
"""
CLI for Pyquet - mzML to Parquet converter.
"""

import argparse
import sys
import os
from pathlib import Path

from .mzml_converter import convert_mzml_to_parquet_streaming, get_file_info


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert mzML files to Parquet format with memory efficiency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyquet input.mzML                           # Convert to input_converted.parquet
  pyquet input.mzML -o output.parquet         # Convert to specific output file
  pyquet input.mzML --batch-size 5000         # Use smaller batch size
  pyquet input.mzML --compression gzip        # Use gzip compression
  pyquet input.mzML --info                    # Show file info without converting
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input mzML file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Path to output Parquet file (default: input_converted.parquet)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10000,
        help='Number of data points to process in each batch (default: 10000)'
    )
    
    parser.add_argument(
        '--compression',
        type=str,
        choices=['snappy', 'gzip', 'lz4', 'brotli'],
        default='snappy',
        help='Parquet compression type (default: snappy)'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show file information without converting'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not args.input_file.lower().endswith('.mzml'):
        print(f"Warning: Input file '{args.input_file}' does not have .mzML extension", file=sys.stderr)
    
    try:
        # Get file info
        print(f"Analyzing file: {args.input_file}")
        info = get_file_info(args.input_file)
        print(f"File size: {info['file_size_mb']} MB")
        print(f"Data type: {info['data_type']}")
        print(f"Recommended batch size: {info['recommended_batch_size']}")
        
        if args.info:
            print("File analysis complete.")
            return
        
        # Determine output path
        output_path = args.output
        if output_path is None:
            input_path = Path(args.input_file)
            # Remove the existing extension and add _converted.parquet
            output_path = str(input_path.with_suffix('')) + '_converted.parquet'
        
        # Use recommended batch size if default is used
        batch_size = args.batch_size
        if args.batch_size == 10000:  # User didn't specify, use recommended
            batch_size = info['recommended_batch_size']
        
        print(f"Converting to: {output_path}")
        print(f"Using batch size: {batch_size}")
        print(f"Using compression: {args.compression}")
        print()
        
        # Convert file
        result_path = convert_mzml_to_parquet_streaming(
            file_path=args.input_file,
            output_path=output_path,
            batch_size=batch_size,
            compression=args.compression
        )
        
        print(f"\nConversion successful!")
        print(f"Output file: {result_path}")
        
        # Show output file info
        output_size = os.path.getsize(result_path) / (1024 * 1024)
        print(f"Output file size: {output_size:.2f} MB")
        
    except KeyboardInterrupt:
        print("\nConversion interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
