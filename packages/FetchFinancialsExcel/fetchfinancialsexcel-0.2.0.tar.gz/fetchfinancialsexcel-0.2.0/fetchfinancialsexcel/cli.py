import argparse
import sys
import os
from pathlib import Path

from .core import FundamentalDataFetcher

def validate_api_key(api_key: str) -> bool:
    if not api_key or len(api_key) < 10:
        return False
    return True

def validate_excel_file(file_path: str) -> bool:

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False
    
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        print(f"Error: File '{file_path}' is not an Excel file (.xlsx or .xls).")
        return False
    
    return True

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch fundamental financial data for stocks listed in an Excel file.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument(
        '--api-key',
        required=True,
        help='Your EODHD API key (required)'
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to input Excel file containing tickers'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Path to output Excel file for results'
    )
    
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=10,
        help='Number of concurrent workers for data fetching (default: 10)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='FetchFinancialsExcel 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Validate API key
    if not validate_api_key(args.api_key):
        print("Error: Invalid API key. Please provide a valid EODHD API key.")
        sys.exit(1)
    
    # Validate input file
    if not validate_excel_file(args.input):
        sys.exit(1)
    
    # Validate workers parameter
    if args.workers < 1 or args.workers > 50:
        print("Error: Number of workers must be between 1 and 50.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize the fetcher
        print("Initializing Fundamental Data Fetcher...")
        fetcher = FundamentalDataFetcher(api_key=args.api_key)
        
        # Process the file
        fetcher.process_excel_file(
            input_file=args.input,
            output_file=args.output,
            max_workers=args.workers
        )
        
        print(f"\n Success! Results saved to: {args.output}")
        
    except Exception as e:
        print(f"\n Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 