#!/usr/bin/env python3
"""
Sokrates Smart Test Generator CLI Command

This script provides a command-line interface for automatically generating 
unit tests for Python functions using LLM analysis.
"""

import argparse
import os
from sokrates.coding.test_generator import TestGenerator
from sokrates.output_printer import OutputPrinter
from sokrates.colors import Colors
from sokrates.config import Config


def main():
    """
    Main function that orchestrates the test generation process:
      - Parses CLI arguments
      - Configures LLM parameters  
      - Runs the test generation workflow
      - Reports results to stdout
    """
    OutputPrinter.print_header("🚀 Sokrates Smart Test Generator 🚀", Colors.BRIGHT_CYAN, 50)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Automatically generate unit tests for Python functions using LLM analysis.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests for a directory of Python files
  sokrates-generate-tests --source-directory ./src/myproject --output-dir ./tests

  # Generate tests for specific files with a specific model
  sokrates-generate-tests --files ./src/module1.py,./src/module2.py --model gpt-4

  # Generate tests with custom LLM endpoint
  sokrates-generate-tests --source-directory ./src --api-endpoint http://localhost:1234/v1 --output-dir ./generated_tests
        """
    )
    
    # Input arguments
    parser.add_argument('--source-directory', '-sd', type=str,
                        help='Directory containing Python files to generate tests for')
    parser.add_argument('--files', '-f', type=str,
                        help='Comma-separated list of specific Python files to generate tests for')
    
    # Output arguments
    parser.add_argument('--output-dir', '-o', type=str, required=False, default="tests",
                        help='Directory for output test files (default: tests/)')
    
    # LLM configuration arguments
    parser.add_argument('--model', '-m', type=str, default=None, required=False,
                        help='LLM model name to use for test generation')
    parser.add_argument('--api-endpoint', '-ae', type=str, default=None, required=False,
                        help='Custom API endpoint for LLM service')
    parser.add_argument('--api-key', '-ak', type=str, default=None, required=False,
                        help='API key for authentication with LLM service')
    parser.add_argument('--temperature', '-temp', type=float, default=0.7,
                        help='Sampling temperature for responses (default: 0.7)')
    parser.add_argument('--max-tokens', '-mt', type=int, default=2000,
                        help='Maximum tokens for test generation (default: 2000)')
    
    # Test generation strategy
    parser.add_argument('--strategy', '-s', type=str, default="all",
                        choices=['all', 'base', 'edge_cases', 'error_handling', 'validation'],
                        help='Test generation strategy to use (default: base)')
    
    # Utility arguments
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output for the script execution')
    
    args = parser.parse_args()
    
    # Configuration setup
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
        # Run the test generation workflow
        generator = TestGenerator(
            model=model,
            api_endpoint=api_endpoint,
            api_key=api_key,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            verbose=args.verbose
        )
        
        results = generator.generate_tests(
            directory_path=directory_path,
            file_paths=file_paths,
            output_dir=args.output_dir,
            strategy=args.strategy
        )
        
        # Print summary of results
        OutputPrinter.print_success("Test generation completed successfully!")
        if args.source_directory:
            print(f"   Directory processed: {args.source_directory}")
        elif file_paths:
            print(f"   Files processed: {', '.join(file_paths)}")
        print(f"   Output directory: {args.output_dir}")
        print(f"   Strategy used: {args.strategy}")
        print(f"   Tests generated: {results['tests_generated']}")
        print(f"   Test files created: {len(results['files_created'])}")

        if results['errors']:
            print(f"{Colors.YELLOW}⚠️  Errors encountered: {len(results['errors'])}{Colors.RESET}")
            for error in results['errors']:
                print(f"   - {error['file']}: {error['error']}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during test generation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test generation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)