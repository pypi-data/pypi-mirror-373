#!/usr/bin/env python3
"""
Python Summarizer command
Summarizes the class and function signatures and according docstrings in a markdown file
The result can be fed to a large language model as context for understanding how to use the documented code
"""

import argparse
import sys
from sokrates.coding.python_analyzer import PythonAnalyzer
from sokrates.output_printer import OutputPrinter
from sokrates.colors import Colors

def main():
    """Main execution function"""
    OutputPrinter.print_header("🚀 Python summarize code 🚀", Colors.BRIGHT_CYAN, 50)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create a summary document for a given python source code directory.')
    parser.add_argument('--source-directory', '-sd', type=str, required=True,
                       help='Directory containing python code files to summarize')
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='Destination of the summary document to generate')
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for the script execution'
    )
    args = parser.parse_args()
    PythonAnalyzer.create_markdown_documentation_for_directory(directory_path=args.source_directory, 
                                                               target_file=args.output, verbose=args.verbose)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Python summary workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)