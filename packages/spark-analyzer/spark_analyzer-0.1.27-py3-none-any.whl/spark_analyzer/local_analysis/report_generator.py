#!/usr/bin/env python3
"""
Report Generator for Spark Acceleration Analysis

This module generates comprehensive acceleration reports from Spark diagnostics data
or pre-existing analysis output files.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

from .local_acceleration_analyzer import (
    get_input_files, get_output_files, analyze_spark_diagnostics
)
from .data_models import SparkDiagnosticsPayload


def validate_input_data(data: Dict[str, Any]) -> bool:
    """Validate that input data has the required structure for report generation."""
    # Check if this is a raw Spark diagnostics payload
    if 'stages' in data and 'application_id' in data:
        return True
    
    # Check if this is already processed analysis output
    if 'total_metrics' in data and 'workflow_breakdown' in data:
        return True
    
    return False


def detect_input_type(data: Dict[str, Any]) -> str:
    """Detect whether input is raw diagnostics or processed analysis."""
    if 'stages' in data and 'application_id' in data:
        return 'diagnostics'
    elif 'total_metrics' in data and 'workflow_breakdown' in data:
        return 'analysis'
    else:
        return 'unknown'


def process_input_file(input_file: str) -> Dict[str, Any]:
    """Process input file and return analysis data."""
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        input_type = detect_input_type(data)
        
        if input_type == 'diagnostics':
            # Process raw diagnostics data
            return analyze_spark_diagnostics(data)
        elif input_type == 'analysis':
            # Already processed, return as-is
            return data
        else:
            raise ValueError(f"Unsupported input format: {input_type}")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file: {e}")


def generate_report(input_file: str, output_file: str, output_format: str = 'excel', verbose: bool = False) -> tuple[bool, str]:
    """Generate acceleration report from input file.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        if verbose:
            print(f"📋 Processing input file: {input_file}")
        
        # Process the input file
        analysis_data = process_input_file(input_file)
        
        if verbose:
            print(f"📊 Analysis data loaded successfully")
            print(f"📈 Application ID: {analysis_data.get('application_id', 'N/A')}")
        
        # Save the report using the existing output functions
        from .local_acceleration_analyzer import save_output_file
        save_output_file(output_file, analysis_data)
        
        if verbose:
            print(f"✅ Report saved to: {output_file}")
        
        return True, ""
        
    except Exception as e:
        error_msg = f"Error generating report: {e}"
        if verbose:
            print(f"❌ {error_msg}")
        return False, error_msg


def main():
    """Main function for standalone report generation."""
    parser = argparse.ArgumentParser(
        description="Generate Spark acceleration reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Excel report
  python -m report_generator --input data.json --output report.xlsx

  # Batch processing
  python -m report_generator --input "*.json" --output-dir ./reports/
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file(s) containing Spark diagnostics payload or analysis output'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for the report (default: auto-generated based on input)'
    )
    
    parser.add_argument(
        '--output-dir', '-d',
        help='Output directory for batch processing'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['excel'],
        default='excel',
        help='Output format for the report (Excel only)'
    )
    

    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    output_format = 'excel'
    
    try:
        input_files = get_input_files(args.input)
        output_files = get_output_files(input_files, args.output, args.output_dir)
        
        if args.verbose:
            print(f"📋 Found {len(input_files)} input file(s)")
            print(f"📁 Will generate {len(output_files)} {output_format.upper()} output file(s)")
        
        successful = 0
        failed = 0
        
        for i, (input_file, output_file) in enumerate(zip(input_files, output_files)):
            if args.verbose:
                print(f"\n🔄 Processing file {i+1}/{len(input_files)}")
            
            success, error_msg = generate_report(input_file, output_file, output_format, args.verbose)
            if success:
                successful += 1
            else:
                failed += 1
                if error_msg:
                    print(f"❌ {error_msg}")
        
        print(f"\n📊 Report Generation Summary:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Total files processed: {len(input_files)}")
        print(f"📄 Output format: {output_format.upper()}")
        
        if failed > 0:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
