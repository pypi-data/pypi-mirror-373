#!/usr/bin/env python3

import argparse
from sokrates.llm_api import LLMApi
from sokrates.config import Config
from sokrates.output_printer import OutputPrinter
from sokrates.cli.helper import Helper

def main():
    """
    Main function to list available models from the LLM API.
    
    This function initializes the LLMApi instance, retrieves the list of available models,
    and prints them to the console. It handles exceptions and prints error messages.
    
    Parameters:
        None
    
    Returns:
        None
    """
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Lists available models for an llm endpoint',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
 list_models.py --api-endpoint http://localhost:1234/v1 --api-key not-required
 list_models.py # for localhost:1234/v1
  
        """
    )

    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=None,
        help=f"LLM server API endpoint."
    )
    
    parser.add_argument(
        '--api-key',
        required=False,
        default=None,
        help='API key for authentication (many local servers don\'t require this)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        config = Config(verbose=args.verbose)
        api_endpoint = config.api_endpoint
        api_key = config.api_key
        
        if args.api_endpoint:
            api_endpoint = args.api_endpoint
        if args.api_key:
            api_key = args.api_key
        
        llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
        models = llm_api.list_models()
        Helper.print_configuration_section(config, args)

        OutputPrinter.print_section("Available models:")
        for model in models:
            print(model)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
