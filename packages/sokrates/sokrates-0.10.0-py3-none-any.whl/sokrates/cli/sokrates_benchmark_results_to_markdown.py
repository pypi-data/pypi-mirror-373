#!/usr/bin/env python3
"""
Model Comparison Report Generator

This script parses a JSON file containing model comparison results and 
generates a colorful markdown table showing performance metrics.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ModelMetrics:
    """Data class to hold model performance metrics"""
    model_name: str
    avg_tokens_per_second: float
    avg_response_time_seconds: float
    max_memory_used_gb: float
    avg_cpu_percent: float
    avg_memory_percent: float
    total_completion_tokens: int
    prompts_tested: int


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def calculate_avg_memory_percent(system_monitoring: List[Dict]) -> float:
    """Calculate average memory percentage from system monitoring data"""
    if not system_monitoring:
        return 0.0
    memory_percentages = [entry.get('memory_percent', 0) for entry in system_monitoring]
    return sum(memory_percentages) / len(memory_percentages)


def parse_model_data(model_data: Dict[str, Any]) -> ModelMetrics:
    """Parse individual model data and extract metrics"""
    performance = model_data.get('performance_metrics', {})
    resource_usage = model_data.get('resource_usage', {})
    system_monitoring = model_data.get('system_monitoring', [])
    
    return ModelMetrics(
        model_name=model_data.get('model_name', 'Unknown'),
        avg_tokens_per_second=performance.get('avg_tokens_per_second', 0.0),
        avg_response_time_seconds=performance.get('avg_response_time_seconds', 0.0),
        max_memory_used_gb=resource_usage.get('max_memory_used_gb', 0.0),
        avg_cpu_percent=resource_usage.get('avg_cpu_percent', 0.0),
        avg_memory_percent=calculate_avg_memory_percent(system_monitoring),
        total_completion_tokens=performance.get('total_completion_tokens', 0),
        prompts_tested=performance.get('prompts_tested', 0)
    )


def format_number(value: float, decimals: int = 2) -> str:
    """Format numbers with appropriate decimal places"""
    return f"{value:.{decimals}f}"


def get_performance_color(value: float, metric_type: str) -> str:
    """Get color based on performance value and metric type"""
    thresholds = {
        'tokens_per_second': {'good': 50, 'fair': 30},
        'response_time': {'good': 5, 'fair': 15},
        'cpu_percent': {'good': 20, 'fair': 50},
        'memory_gb': {'good': 10, 'fair': 20},
        'memory_percent': {'good': 20, 'fair': 50}
    }
    
    if metric_type in thresholds:
        if value >= thresholds[metric_type]['good']:
            return Colors.OKGREEN
        elif value >= thresholds[metric_type]['fair']:
            return Colors.WARNING
        else:
            return Colors.FAIL
    return Colors.ENDC


def print_colored_markdown_table(models: List[ModelMetrics], metadata: Dict[str, Any]):
    """Print a colorful markdown table with model comparison results"""
    
    # Print header with metadata
    print(f"{Colors.BOLD}{Colors.HEADER}# Model Performance Comparison Report{Colors.ENDC}")
    print()
    print(f"**Benchmark Date:** {metadata.get('timestamp', 'Unknown')}")
    print(f"**Total Models Tested:** {metadata.get('total_models_tested', 'Unknown')}")
    print(f"**Temperatures Tested:** {', '.join(map(str, metadata.get('temperatures_tested', [])))}")
    print(f"**Benchmark Version:** {metadata.get('benchmark_version', 'Unknown')}")
    print()
    
    # Table headers
    headers = [
        "Rank", 
        "Model Name", 
        "Tokens/Sec", 
        "Response Time (s)", 
        "Memory (GB)", 
        "CPU %", 
        "Memory %", 
        "Total Tokens", 
        "Prompts"
    ]
    
    # Print markdown table header
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join([":---:" for _ in headers]) + "|")
    
    # Print data rows
    for rank, model in enumerate(models, 1):
        tokens_color = get_performance_color(model.avg_tokens_per_second, 'tokens_per_second')
        time_color = get_performance_color(model.avg_response_time_seconds, 'response_time')
        memory_color = get_performance_color(model.max_memory_used_gb, 'memory_gb')
        cpu_color = get_performance_color(model.avg_cpu_percent, 'cpu_percent')
        mem_percent_color = get_performance_color(model.avg_memory_percent, 'memory_percent')
        
        row = [
            f"{Colors.BOLD}{rank}{Colors.ENDC}",
            f"{Colors.OKCYAN}{model.model_name}{Colors.ENDC}",
            f"{tokens_color}{format_number(model.avg_tokens_per_second)}{Colors.ENDC}",
            f"{time_color}{format_number(model.avg_response_time_seconds)}{Colors.ENDC}",
            f"{memory_color}{format_number(model.max_memory_used_gb)}{Colors.ENDC}",
            f"{cpu_color}{format_number(model.avg_cpu_percent)}{Colors.ENDC}",
            f"{mem_percent_color}{format_number(model.avg_memory_percent)}{Colors.ENDC}",
            f"{model.total_completion_tokens:,}",
            f"{model.prompts_tested}"
        ]
        
        print("| " + " | ".join(row) + " |")
    
    # Performance legend
    print()
    print(f"{Colors.BOLD}## Performance Legend{Colors.ENDC}")
    print()
    print(f"{Colors.OKGREEN}🟢 Excellent{Colors.ENDC} | {Colors.WARNING}🟡 Good{Colors.ENDC} | {Colors.FAIL}🔴 Needs Improvement{Colors.ENDC}")
    print()
    print("**Tokens/Sec:** 🟢 ≥50 | 🟡 30-49 | 🔴 <30")
    print("**Response Time:** 🟢 ≤5s | 🟡 5-15s | 🔴 >15s")
    print("**CPU Usage:** 🟢 ≤20% | 🟡 20-50% | 🔴 >50%")
    print("**Memory Usage:** 🟢 ≤10GB | 🟡 10-20GB | 🔴 >20GB")
    print("**Memory %:** 🟢 ≤20% | 🟡 20-50% | 🔴 >50%")


def main():
    """Main function to parse arguments and generate report"""
    parser = argparse.ArgumentParser(
        description="Generate a colorful markdown report from model comparison JSON results"
    )
    parser.add_argument(
        "--model-comparison",
        required=True,
        help="Path to the JSON file containing model comparison results"
    )
    
    args = parser.parse_args()
    
    json_file = Path(args.model_comparison)
    if not json_file.exists():
        print(f"{Colors.FAIL}Error: File '{json_file}' not found.{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        metadata = data.get('comparison_metadata', {})
        model_comparisons = data.get('model_comparisons', [])
        
        if not model_comparisons:
            print(f"{Colors.WARNING}Warning: No model comparisons found in the JSON file.{Colors.ENDC}")
            sys.exit(1)
        
        models = [parse_model_data(model_data) for model_data in model_comparisons]
        models.sort(key=lambda x: x.avg_tokens_per_second, reverse=True)
        
        print_colored_markdown_table(models, metadata)
    
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}Error: Invalid JSON file. {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"{Colors.FAIL}Error: Missing required field in JSON: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
