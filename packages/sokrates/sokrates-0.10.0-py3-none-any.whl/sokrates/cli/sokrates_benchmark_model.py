#!/usr/bin/env python3
"""
LM Studio Benchmark Script
Benchmarks LLM performance through LM Studio's OpenAI-compatible API
"""

import requests
import json
import argparse
import os
from datetime import datetime
from sokrates import LMStudioBenchmark

# Test prompts of varying complexity
DEFAULT_TEST_PROMPTS = [
    "Hello, who are you?",
    "Explain the phenomenon of a Black hole in simple terms so that a 5 year old could understand.",
    "Write a short story that takes place in a world where pizzas are the dominant race on the planet and pizzas are ordering humans for lunch via telephone.",
    "Write a shell script that displays the list of open network ports on the system and their according running process ids and names",
    "Create a Python function that implements a binary search algorithm with comments."
]

DEFAULT_ENDPOINT="http://localhost:1234/v1"

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Benchmark LLM performance in LM Studio')
    parser.add_argument('--store-results', action='store_true', 
                       help='Store benchmark results as JSON file')
    parser.add_argument('--results-directory', type=str, 
                       help='Directory to store results (default: current directory)')
    parser.add_argument('--model', type=str, 
                       help='Specific model name to benchmark')
    parser.add_argument('--models', type=str,
                       help='Comma-separated list of models to benchmark (e.g., llama3.1,deepseek-r1)')
    parser.add_argument('--max-tokens', type=int, default=5000,
                       help='Maximum tokens to generate per prompt (default: 150)')
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='Temperature for text generation (default: 0.7). Ignored if --temperatures is provided.')
    parser.add_argument('--temperatures', type=str,
                       help='Comma-separated list of temperature values (e.g., "0.15,0.333,0.7"). Values must be between 0.0 and 1.0. Overrides --temperature.')
    parser.add_argument('--input-directory', type=str,
                       help='Directory containing .md files to use as prompts instead of default test prompts')
    parser.add_argument('--all-available-models', action='store_true',
                       help='Benchmark all models available via the LM Studio API endpoint')
    parser.add_argument('--timeout', type=int, default=240,
                        help='Timeout for requests to the benchmarked models')
    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=DEFAULT_ENDPOINT,
        help=f"LLM server API endpoint. Default is {DEFAULT_ENDPOINT}"
    )
    
    parser.add_argument(
        '--api-key',
        required=False,
        default=None,
        help='API key for authentication (many local servers don\'t require this)'
    )
    args = parser.parse_args()

    # Parse and validate temperatures
    temperatures_to_test = []
    if args.temperatures:
        try:
            temperatures_to_test = [float(t.strip()) for t in args.temperatures.split(',')]
            for temp in temperatures_to_test:
                if not (0.0 <= temp <= 1.0):
                    raise ValueError("Temperature values must be between 0.0 and 1.0.")
        except ValueError as e:
            print(f"Error: Invalid --temperatures format or value: {e}")
            return
    else:
        temperatures_to_test = [args.temperature] # Use the single temperature if --temperatures is not provided
    
    # Function to load prompts from .md files in a directory
    def load_prompts_from_directory(directory):
        prompts = []
        if not os.path.isdir(directory):
            print(f"Error: Input directory '{directory}' not found.")
            return []
        
        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        prompts.append(f.read())
                    print(f"Loaded prompt from: {filepath}")
                except Exception as e:
                    print(f"Error reading file {filepath}: {e}")
        
        if not prompts:
            print(f"Warning: No .md files found in '{directory}'. Using default prompts.")
        return prompts

    # Validate arguments
    if args.model and args.models:
        print("Error: Cannot specify both --model and --models. Please use one or the other.")
        return
    
    if args.all_available_models and (args.model or args.models):
        print("Error: Cannot specify --all-available-models with --model or --models.")
        return

    # Validate results directory if provided
    if args.results_directory:
        if not args.store_results:
            print("Warning: --results-directory provided but --store-results not set. Results will not be saved.")
        elif not os.path.isdir(args.results_directory) and not os.path.exists(args.results_directory):
            try:
                os.makedirs(args.results_directory)
                print(f"Created results directory: {args.results_directory}")
            except Exception as e:
                print(f"Error creating results directory: {e}")
                return
    
    # Determine prompts to use
    if args.input_directory:
        prompts_to_use = load_prompts_from_directory(args.input_directory)
        if not prompts_to_use: # Fallback to default if no prompts loaded from directory
            raise Exception(f"No prompts present within {args.input_directory}")
    else:
        prompts_to_use = DEFAULT_TEST_PROMPTS
    
    benchmark = LMStudioBenchmark(api_endpoint=args.api_endpoint)
    
    # Test if LM Studio server is running
    try:
        response = requests.get(f"{benchmark.api_endpoint}/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            available_models = [model.get('id', 'Unknown') for model in models.get('data', [])]
            available_models.sort()
            print("Available models:")
            for model in available_models:
                print(f"  - {model}")
        else:
            print("LM Studio server not responding properly")
            return
    except requests.exceptions.RequestException:
        print("Error: Cannot connect to LM Studio server.")
        print("Please ensure LM Studio is running with a model loaded and server started.")
        return
    
    # Determine which models to benchmark
    models_to_test = []
    
    if args.all_available_models:
        models_to_test = available_models
        if not models_to_test:
            print("No models available from the API endpoint to benchmark.")
            return
        print(f"\nBenchmarking all available models: {', '.join(models_to_test)}")
    elif args.models:
        # Multiple models specified
        models_to_test = [model.strip() for model in args.models.split(',') if model.strip()]
        print(f"\nMultiple models specified: {models_to_test}")
        
        # Validate models exist
        missing_models = []
        for model in models_to_test:
            if model not in available_models:
                missing_models.append(model)
        
        if missing_models:
            print(f"Warning: The following models are not available: {missing_models}")
            print("Available models are:", available_models)
            confirm = input("Continue with available models only? (y/n): ")
            if confirm.lower() != 'y':
                return
            models_to_test = [m for m in models_to_test if m not in missing_models]
        
        if not models_to_test:
            print("No valid models to test.")
            return
            
    elif args.model:
        # Single model specified
        models_to_test = [args.model]
        if args.model not in available_models:
            print(f"Warning: Model '{args.model}' not found in available models.")
            print("Available models are:", available_models)
            confirm = input("Continue anyway? (y/n): ")
            if confirm.lower() != 'y':
                return
    else:
        # No model specified, get from user input or use first available
        model_name = input("\nEnter the model name to benchmark (or press Enter for default): ").strip()
        if not model_name:
            if available_models:
                model_name = available_models[0]
                print(f"Using first available model: {model_name}")
            else:
                print("No models available")
                return
        models_to_test = [model_name]
    
    print(f"\nBenchmarking configuration:")
    print(f"\nBenchmarking configuration:")
    print(f"  Models: {', '.join(models_to_test)}")
    print(f"  Max tokens: {args.max_tokens}")
    print(f"  Temperatures: {temperatures_to_test}")
    print(f"  Base URL: {args.api_endpoint}")
    print(f"  Store results: {args.store_results}")
    if args.store_results:
        results_path = args.results_directory if args.results_directory else "current directory"
        print(f"  Results location: {results_path}")
    
    # Run benchmarks
    all_overall_results = [] # To store results for all models and all temperatures
    
    for current_temperature in temperatures_to_test:
        print(f"\n--- Running benchmarks for Temperature: {current_temperature} ---")
        if len(models_to_test) > 1:
            # Multiple model benchmark
            all_results = benchmark.benchmark_multiple_models(
                models_to_test,
                prompts_to_use, # Use prompts_to_use here
                max_tokens=args.max_tokens,
                temperature=current_temperature, # Use current_temperature
                store_results=args.store_results,
                results_directory=args.results_directory,
                timeout=args.timeout
            )
            
            if all_results:
                # Create and display comparison table
                comparison_table, comparison_data = benchmark.create_comparison_table(all_results)
                
                if comparison_table:
                    print(f"\n{'='*80}")
                    print(f"MODEL COMPARISON RESULTS (Temperature: {current_temperature})")
                    print(f"{'='*80}")
                    print(comparison_table)
                    
                    # Print performance insights
                    print(f"\n🏆 PERFORMANCE INSIGHTS:")
                    if comparison_data and comparison_data.get('performance_ranking'):
                        ranking = comparison_data['performance_ranking']
                        best_model = ranking[0]
                        print(f"   Best performing model: {best_model['model_name']} ({best_model['tokens_per_second']:.2f} tokens/s)")
                        
                        if len(ranking) > 1:
                            worst_model = ranking[-1]
                            performance_gap = ((best_model['tokens_per_second'] - worst_model['tokens_per_second']) / worst_model['tokens_per_second']) * 100
                            print(f"   Performance gap: {performance_gap:.1f}% faster than slowest model")
                    
                    # Save comparison results if requested
                    if args.store_results and comparison_data:
                        # Modify filename to include temperature
                        comparison_data['comparison_metadata']['temperature'] = current_temperature
                        benchmark.save_comparison_results(comparison_data, args.results_directory)
                else:
                    print("\n❌ Could not generate comparison table - no valid results obtained")
            else:
                print("\n❌ No successful benchmarks completed")
                
            all_overall_results.extend(all_results) # Add to overall results
                
        else:
            # Single model benchmark
            model_name = models_to_test[0]
            results = benchmark.benchmark_model(
                model_name,
                prompts_to_use, # Use prompts_to_use here
                max_tokens=args.max_tokens,
                temperature=current_temperature, # Use current_temperature
                results_directory=args.results_directory # Pass results_directory here
            )
            
            benchmark.analyze_results(
                results,
                store_results=args.store_results,
                results_directory=args.results_directory
            )
            
            # Legacy behavior - always save with timestamp if no specific storage requested
            if not args.store_results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"lm_studio_benchmark_{timestamp}_temp_{current_temperature}.json"
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nBasic results saved to: {filename}")
            
            all_overall_results.append(results) # Add to overall results
            
    # Final comparison across all models and temperatures if multiple temperatures were tested
    if len(temperatures_to_test) > 1 and all_overall_results:
        print(f"\n{'='*80}")
        print("OVERALL MODEL AND TEMPERATURE COMPARISON RESULTS")
        print(f"{'='*80}")
        overall_comparison_table, overall_comparison_data = benchmark.create_comparison_table(all_overall_results)
        if overall_comparison_table:
            print(overall_comparison_table)
            if args.store_results and overall_comparison_data:
                # Save overall comparison with a distinct filename
                overall_comparison_data['comparison_metadata']['temperatures_tested'] = temperatures_to_test
                benchmark.save_comparison_results(overall_comparison_data, args.results_directory, filename_prefix="overall_")
        else:
            print("\n❌ Could not generate overall comparison table - no valid results obtained")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()