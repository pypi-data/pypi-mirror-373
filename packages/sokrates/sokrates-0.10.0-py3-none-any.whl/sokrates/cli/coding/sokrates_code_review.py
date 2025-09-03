#!/usr/bin/env python3
"""
Sokrates Code Review CLI Command

This script provides a command-line interface for performing automated code reviews 
on Python source code using LLMs and the sokrates library's analysis capabilities.
"""

import argparse
import os
import sys
from sokrates.coding.code_review_workflow import run_code_review
from sokrates.output_printer import OutputPrinter
from sokrates.colors import Colors
from sokrates.config import Config


def main():
    """
    Orchestrates code review process by:
      - Validating CLI arguments
      - Configuring LLM parameters
      - Running the review workflow
      - Reporting results to stdout
    """
    OutputPrinter.print_header("🚀 Sokrates Code Review 🚀", Colors.BRIGHT_CYAN, 50)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Perform automated code reviews on Python source code.')
    parser.add_argument('--source-directory', '-sd', type=str,
                        help='Directory containing Python files to review')
    parser.add_argument('--files', '-f', type=str,
                        help='Comma-separated list of specific Python files to review')
    parser.add_argument('--output-dir', '-o', type=str, required=False, default="docs/code_reviews",
                        help='Directory for output markdown files')
    parser.add_argument('--review-type', '-t', type=str, default='quality',
                        choices=['style', 'security', 'performance', 'quality', 'all'],
                        help='Type of review to perform (default: all)')
    parser.add_argument('--model', '-m', type=str, default=None, required=False,
                        help='LLM model name to use for reviews')
    parser.add_argument('--api-endpoint', '-ae', type=str, default=None, required=False,
                        help='Custom API endpoint for LLM service')
    parser.add_argument('--api-key', '-ak', type=str, default=None, required=False,
                        help='API key for authentication with LLM service')
    parser.add_argument('--temperature', '-temp', type=float, default=0.7,
                        help='Sampling temperature for responses (default: 0.7)')
    parser.add_argument('--max-tokens', '-mt', type=int, default=30000,
                        help='The maximum number of output tokens for a review (default: 30000)')
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for the script execution'
    )
    
    args = parser.parse_args()
    config = Config(verbose=args.verbose)
    api_endpoint = args.api_endpoint or config.api_endpoint
    api_key = args.api_key or config.api_key
    model = args.model or config.default_model
    
    # Validate arguments
    if not args.source_directory and not args.files:
        print("❌ Error: Either --source-directory or --files must be specified. Use --help for details.")
        return 1
    
    if args.source_directory and args.files:
        print("❌ Error: Only one of --source-directory or --files can be specified. Use --help for details.")
        return 1
        
    # Prepare file paths
    file_paths = None
    directory_path = None
    
    if args.source_directory:
        if not os.path.isdir(args.source_directory):
            print(f"❌ Error: Path '{args.source_directory}' is not a directory")
            return 1
        directory_path = args.source_directory
    elif args.files:
        file_paths = [f.strip() for f in args.files.split(',')]
        # Validate that files exist
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"❌ Error: File '{file_path}' does not exist")
                return 1
    
    try:
        # Run the code review workflow
        reviews = run_code_review(
            directory_path=directory_path,
            file_paths=file_paths,
            output_dir=args.output_dir,
            review_type=args.review_type,
            model=model,
            api_endpoint=api_endpoint,
            api_key=api_key,
            max_tokens=args.max_tokens,
            verbose=args.verbose
        )
        
        # Print summary of results
        OutputPrinter.print_success("Code review completed successfully!")
        if args.source_directory:
            print(f"   Directory reviewed: {args.source_directory}")
        elif file_paths:
            print(f"   Files reviewed: {', '.join(file_paths)}")
        print(f"   Output directory: {args.output_dir}")
        print(f"   Review type: {args.review_type}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during code review: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Code review interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)