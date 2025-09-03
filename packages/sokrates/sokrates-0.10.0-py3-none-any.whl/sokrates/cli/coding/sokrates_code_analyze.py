#!/usr/bin/env python3
"""
Sokrates Code Analysis CLI Command

This script provides a command-line interface for performing automated code analysis 
on source code using LLMs and the sokrates library's analysis capabilities.
"""

import argparse
import os
import sys
from sokrates.coding.analyze_repository_workflow import AnalyzeRepositoryWorkflow
from sokrates.output_printer import OutputPrinter
from sokrates.colors import Colors
from sokrates.config import Config
from sokrates.cli.helper import Helper
from sokrates.file_helper import FileHelper


def main():
    """
    Orchestrates code analysis process by:
      - Validating CLI arguments
      - Configuring LLM parameters
      - Running the analysis workflow
      - Reporting results to stdout
    """
    OutputPrinter.print_header("🚀 Sokrates Code Analysis 🚀", Colors.BRIGHT_CYAN, 50)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Perform automated code analysis on source code. This is very handy to dive into an unknown code base')
    parser.add_argument('--source-directory', '-sd', type=str,
                        help='Directory containing source files to review (usually the root directory of a git repository)', required=True)
    parser.add_argument('--output', '-o', type=str, required=False, default="docs/code_analysis.md",
                        help='File path for output markdown file with the report')
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

    directory_path = None
    
    if args.source_directory:
        if not os.path.isdir(args.source_directory):
            print(f"❌ Error: Path '{args.source_directory}' is not a directory")
            return 1
        directory_path = args.source_directory

    Helper.print_configuration_section(config=config, args=args)
    OutputPrinter.print_info("Model", str(model))
    
    try:
        # run the analysis
        workflow = AnalyzeRepositoryWorkflow(api_endpoint=str(api_endpoint), api_key=str(api_key))
        analysis_result = workflow.analyze_repository(
            source_directory=str(directory_path), 
            model=str(model), 
            temperature=args.temperature,
            max_tokens=args.max_tokens 
        )
        FileHelper.write_to_file(args.output, analysis_result)
        
        # Print summary of results
        OutputPrinter.print_success("Code analysis completed successfully!")
        OutputPrinter.print_info("Analyzed directory", args.source_directory)
        OutputPrinter.print_file_created(args.output)
        if args.verbose:
            OutputPrinter.print_section("Resulting report")
            print(analysis_result)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during code analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Code analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)