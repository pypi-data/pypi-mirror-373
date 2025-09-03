"""
This script merges benchmarking results from multiple JSON files, calculates averages, and generates a Markdown table summarizing the performance of different language models.
"""
import argparse
import json
from collections import defaultdict
from colorama import Fore, Style
from tabulate import tabulate

# Initialize colorama
import colorama
colorama.init(autoreset=True)

def parse_arguments():
    """
    Parses command-line arguments.

    Args:
        None

    Returns:
        argparse.Namespace: An object containing the parsed arguments.  The key argument is `result_files`, which should be a comma-separated list of JSON file paths.
    """
    parser = argparse.ArgumentParser(description='Compare large language models based on benchmarking results.')
    parser.add_argument('--result-files', required=True, help='Comma-separated list of JSON file paths')
    return parser.parse_args()

def read_json_file(file_path):
    """
    Reads a JSON file and returns its contents as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file, or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] Could not read file {file_path}: No such file or directory")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}[ERROR] Could not parse file {file_path}: JSON decode error")
        return None

def extract_metrics(data):
    """
    Extracts performance metrics from a dictionary containing benchmarking data.

    Args:
        data (dict): A dictionary containing benchmarking data, expected to have a 'model_comparisons' key.

    Returns:
        defaultdict(lambda): A dictionary where keys are model names and values are dictionaries containing performance metrics.
    """
    models = defaultdict(lambda: {'avg_tokens_per_second': 0, 'avg_response_time_seconds': 0,
                                 'total_completion_tokens': 0, 'prompts_tested': 0,
                                 'avg_cpu_percent': 0, 'max_memory_used_gb': 0})
    for model in data.get('model_comparisons', []):
        name = model['model_name']
        perf_metrics = model.get('performance_metrics', {})
        res_usage = model.get('resource_usage', {})

        models[name]['avg_tokens_per_second'] += float(perf_metrics.get('avg_tokens_per_second', 0))
        models[name]['avg_response_time_seconds'] += float(perf_metrics.get('avg_response_time_seconds', 0))
        models[name]['total_completion_tokens'] += int(perf_metrics.get('total_completion_tokens', 0))
        models[name]['prompts_tested'] += int(perf_metrics.get('prompts_tested', 0))
        models[name]['avg_cpu_percent'] += float(res_usage.get('avg_cpu_percent', 0))
        models[name]['max_memory_used_gb'] = max(models[name]['max_memory_used_gb'], float(res_usage.get('max_memory_used_gb', 0)))

    return models

def generate_markdown_table(models):
    """
    Generates a Markdown table summarizing the performance metrics of different language models.

    Args:
        models (dict): A dictionary where keys are model names and values are dictionaries containing performance metrics.

    Returns:
        str: A Markdown table string.
    """
    headers = ["Model Name", "Avg Tokens/s", "Avg Response Time (s)", "Total Completion Tokens", "Prompts Tested", "Avg CPU (%)", "Max Memory Used (GB)"]
    rows = []

    for name, metrics in models.items():
        row = [
            name,
            f"{metrics['avg_tokens_per_second']:.3f}",
            f"{metrics['avg_response_time_seconds']:.3f}",
            str(metrics['total_completion_tokens']),
            str(metrics['prompts_tested']),
            f"{metrics['avg_cpu_percent']:.3f}",
            f"{metrics['max_memory_used_gb']:.3f}"
        ]
        rows.append(row)

    markdown_table = tabulate(rows, headers=headers, tablefmt="github")
    return markdown_table

def main():
    """
    Main function of the script.  Parses arguments, reads JSON files, extracts metrics, generates a Markdown table, and prints the table to the console.
    """
    print(f"{Fore.GREEN}[INFO] Starting script execution...")
    args = parse_arguments()
    file_paths = args.result_files.split(',')

    all_models = defaultdict(lambda: {'avg_tokens_per_second': 0, 'avg_response_time_seconds': 0,
                                     'total_completion_tokens': 0, 'prompts_tested': 0,
                                     'avg_cpu_percent': 0, 'max_memory_used_gb': 0})
    model_count = defaultdict(int)

    for file_path in file_paths:
        print(f"{Fore.GREEN}[INFO] Processing file: {file_path}")
        data = read_json_file(file_path)
        if data:
            models = extract_metrics(data)
            for name, metrics in models.items():
                all_models[name]['avg_tokens_per_second'] += metrics['avg_tokens_per_second']
                all_models[name]['avg_response_time_seconds'] += metrics['avg_response_time_seconds']
                all_models[name]['total_completion_tokens'] += metrics['total_completion_tokens']
                all_models[name]['prompts_tested'] += metrics['prompts_tested']
                all_models[name]['avg_cpu_percent'] += metrics['avg_cpu_percent']
                all_models[name]['max_memory_used_gb'] = max(all_models[name]['max_memory_used_gb'], metrics['max_memory_used_gb'])
                model_count[name] += 1

    for name in all_models:
        all_models[name]['avg_tokens_per_second'] /= model_count[name]
        all_models[name]['avg_response_time_seconds'] /= model_count[name]
        all_models[name]['avg_cpu_percent'] /= model_count[name]

    markdown_table = generate_markdown_table(all_models)
    print(f"{Fore.GREEN}[INFO] Generating Markdown table...")
    with open('comparison_table.md', 'w') as file:
        file.write(markdown_table)
    print(f"{Fore.GREEN}[SUCCESS] Comparison table generated successfully at: comparison_table.md")
    print(markdown_table)

if __name__ == "__main__":
    main()