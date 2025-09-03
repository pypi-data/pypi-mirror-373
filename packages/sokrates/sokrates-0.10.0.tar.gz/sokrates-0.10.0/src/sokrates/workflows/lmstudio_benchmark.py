# This script defines the `LMStudioBenchmark` class, which provides
# comprehensive functionality for benchmarking Large Language Models (LLMs),
# particularly those served by LM Studio. It includes features for:
# - Monitoring system resources (CPU, memory, and optionally GPU) during benchmarks.
# - Running individual benchmarks with specified prompts and parameters.
# - Analyzing and displaying detailed benchmark results, including performance metrics
#   and resource usage.
# - Saving benchmark results and comparative analyses to JSON files for later review.
# - Benchmarking multiple models sequentially and generating comparative tables.

import platform
import time
import psutil
import threading
import requests
import os
from datetime import datetime
import json
from tabulate import tabulate

class LMStudioBenchmark:
    """
    A class designed for benchmarking Large Language Models (LLMs),
    especially those compatible with LM Studio's OpenAI-like API.
    It provides tools for performance measurement, resource monitoring,
    and results analysis and storage.
    """
    def __init__(self, api_endpoint: str = "http://localhost:1234/v1"):
        """
        Initializes the LMStudioBenchmark with the target API endpoint.

        Args:
            api_endpoint (str): The URL of the LLM API endpoint to benchmark against.
                                Defaults to "http://localhost:1234/v1" (LM Studio's default).
        """
        self.api_endpoint = api_endpoint
        self.system_stats = []
        self.monitoring = False
        
    def monitor_system(self) -> None:
        """
        Monitors system resources (CPU, memory, and optionally GPU) at regular intervals
        and stores the statistics. This method runs in a separate thread during benchmarking.
        Requires `psutil` for CPU/memory and `pynvml` (if NVIDIA GPU is present) for GPU stats.
        """
        while self.monitoring:
            stats = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_gb': psutil.virtual_memory().used / (1024**3)
            }
            
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                stats['gpu_memory_used_gb'] = gpu_info.used / (1024**3)
                stats['gpu_memory_total_gb'] = gpu_info.total / (1024**3)
                stats['gpu_utilization'] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            except Exception:
                # pynvml might not be installed or no NVIDIA GPU found
                pass
                
            self.system_stats.append(stats)
            time.sleep(0.5)
    
    def benchmark_model(self, model_name: str, prompts: list[str], max_tokens: int = 100, temperature: float = 0.7, results_directory: str = None, timeout: int = 240) -> dict:
        """
        Benchmarks a single LLM model using a list of prompts.
        Measures response time, tokens per second, and captures system resource usage.

        Args:
            model_name (str): The name of the model to benchmark.
            prompts (list[str]): A list of text prompts to use for benchmarking.
            max_tokens (int): The maximum number of tokens the model should generate per response. Defaults to 100.
            temperature (float): The sampling temperature for text generation. Defaults to 0.7.
            results_directory (str, optional): Directory to save detailed response files. Defaults to None.
            timeout (int): Timeout in seconds for each API request. Defaults to 240.

        Returns:
            dict: A dictionary containing benchmark results, including individual prompt results
                  and captured system statistics.
        """
        print(f"\n=== Benchmarking {model_name} ===")
        
        results = {
            'model': model_name,
            'prompts_tested': len(prompts),
            'max_tokens': max_tokens,
            'temperature': temperature,
            'individual_results': [],
            'system_stats': []
        }
        
        self.system_stats = []
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            for i, prompt in enumerate(prompts):
                print(f"Testing prompt {i+1}/{len(prompts)}...")
                
                start_time = time.time()
                
                response = requests.post(
                    f"{self.api_endpoint}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": False
                    },
                    timeout=timeout
                )
                
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    total_time = end_time - start_time
                    
                    usage = data.get('usage', {})
                    completion_tokens = usage.get('completion_tokens', 0)
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    
                    tokens_per_second = completion_tokens / total_time if total_time > 0 else 0
                    
                    result = {
                        'prompt_length': len(prompt),
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens,
                        'total_time': total_time,
                        'tokens_per_second': tokens_per_second,
                        'response_text': data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100] + "..."
                    }
                    
                    results['individual_results'].append(result)
                    print(f"  Time: {total_time:.2f}s | Tokens/s: {tokens_per_second:.2f} | Tokens: {completion_tokens}")
                    self._save_response_to_file(results_directory, model_name, i, data, temperature)
                else:
                    print(f"  Error: {response.status_code} - {response.text}")
                    
                time.sleep(1)
                
        finally:
            self.monitoring = False
            if monitor_thread.is_alive():
                monitor_thread.join(timeout=1)
            
            results['system_stats'] = self.system_stats.copy()
        
        return results
    
    def _save_response_to_file(self, results_directory: str, model_name: str, prompt_index: int, response_data: dict, temperature: float) -> None:
        """
        Helper function to save the full LLM response content to a Markdown file.

        Args:
            results_directory (str): The directory where the response file will be saved.
            model_name (str): The name of the model that generated the response.
            prompt_index (int): The index of the prompt used (for naming the file).
            response_data (dict): The raw JSON response data from the LLM API.
            temperature (float): The temperature setting used for the generation.
        """
        if results_directory:
            temperature_safe = str(temperature).replace('.', '_').replace(',', '_')
            model_name_safe = model_name.replace('/', '_').replace('\\', '_').replace(':', '_')
            prompt_number_str = f"{prompt_index+1:02d}"
            filename = f"prompt_{prompt_number_str}_{model_name_safe}_t{temperature_safe}.md"
            filepath = os.path.join(results_directory, filename)
            
            os.makedirs(results_directory, exist_ok=True)
            
            full_response_text = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_response_text)
            print(f"  Saved response to: {filepath}")

    def analyze_results(self, results: dict, store_results: bool = False, results_directory: str = None) -> None:
        """
        Analyzes and displays the benchmark results for a single model.
        Calculates averages for performance metrics and summarizes system resource usage.

        Args:
            results (dict): The dictionary containing benchmark results for a model.
            store_results (bool): If True, saves the comprehensive results to a JSON file. Defaults to False.
            results_directory (str, optional): Directory to save the comprehensive results JSON.
                                               Required if store_results is True. Defaults to None.
        """
        individual = results['individual_results']
        if not individual:
            print("No successful results to analyze")
            return
            
        avg_tokens_per_second = sum(r['tokens_per_second'] for r in individual) / len(individual)
        avg_total_time = sum(r['total_time'] for r in individual) / len(individual)
        total_completion_tokens = sum(r['completion_tokens'] for r in individual)
        total_prompt_tokens = sum(r['prompt_tokens'] for r in individual)
        
        print(f"\n=== Results Summary for {results['model']} ===")
        print(f"Prompts tested: {results['prompts_tested']}")
        print(f"Average tokens/second: {avg_tokens_per_second:.2f}")
        print(f"Average response time: {avg_total_time:.2f}s")
        print(f"Total completion tokens: {total_completion_tokens}")
        print(f"Total prompt tokens: {total_prompt_tokens}")
        
        if results['system_stats']:
            stats = results['system_stats']
            avg_cpu = sum(s.get('cpu_percent', 0) for s in stats) / len(stats)
            max_memory = max(s.get('memory_used_gb', 0) for s in stats)
            
            print(f"\nSystem Resource Usage:")
            print(f"Average CPU: {avg_cpu:.1f}%")
            print(f"Peak Memory: {max_memory:.2f} GB")
            
            if any('gpu_memory_used_gb' in s for s in stats):
                max_gpu_memory = max(s.get('gpu_memory_used_gb', 0) for s in stats)
                avg_gpu_util = sum(s.get('gpu_utilization', 0) for s in stats) / len(stats)
                print(f"Peak GPU Memory: {max_gpu_memory:.2f} GB")
                print(f"Average GPU Utilization: {avg_gpu_util:.1f}%")
        
        if store_results:
            self.save_results(results, results_directory)
    
    def save_results(self, results: dict, results_directory: str = None) -> None:
        """
        Saves comprehensive benchmark results for a single model to a JSON file.
        Includes metadata about the benchmark run, system information, model details,
        performance summary, detailed individual results, and system monitoring data.

        Args:
            results (dict): The dictionary containing benchmark results for a model.
            results_directory (str, optional): The directory where the JSON file will be saved.
                                               Defaults to the current directory if None.
        """
        comprehensive_results = {
            'benchmark_metadata': {
                'timestamp': datetime.now().isoformat(),
                'benchmark_version': '1.0',
                'system_info': {
                    'platform': platform.platform(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version(),
                    'total_memory_gb': psutil.virtual_memory().total / (1024**3),
                    'cpu_count': psutil.cpu_count(),
                    'cpu_count_logical': psutil.cpu_count(logical=True)
                }
            },
            'model_info': {
                'model_name': results['model'],
                'max_tokens': results['max_tokens'],
                'temperature': results['temperature'],
                'prompts_tested': results['prompts_tested']
            },
            'performance_summary': {},
            'detailed_results': results['individual_results'],
            'system_monitoring': results['system_stats'],
            'raw_results': results
        }
        
        try:
            import pynvml
            pynvml.nvmlInit()
            gpu_count = pynvml.nvmlDeviceGetCount()
            gpu_info = []
            for i in range(gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info.append({
                    'index': i,
                    'name': name,
                    'memory_total_gb': memory_info.total / (1024**3),
                    'memory_free_gb': memory_info.free / (1024**3)
                })
            comprehensive_results['benchmark_metadata']['system_info']['gpu_info'] = gpu_info
        except:
            comprehensive_results['benchmark_metadata']['system_info']['gpu_info'] = "Not available"
        
        individual = results['individual_results']
        if individual:
            tokens_per_second_list = [r['tokens_per_second'] for r in individual]
            total_times = [r['total_time'] for r in individual]
            
            comprehensive_results['performance_summary'] = {
                'avg_tokens_per_second': sum(tokens_per_second_list) / len(tokens_per_second_list),
                'min_tokens_per_second': min(tokens_per_second_list),
                'max_tokens_per_second': max(tokens_per_second_list),
                'avg_response_time_seconds': sum(total_times) / len(total_times),
                'min_response_time_seconds': min(total_times),
                'max_response_time_seconds': max(total_times),
                'total_completion_tokens': sum(r['completion_tokens'] for r in individual),
                'total_prompt_tokens': sum(r['prompt_tokens'] for r in individual),
                'total_benchmark_duration_seconds': sum(total_times)
            }
        
        if results['system_stats']:
            stats = results['system_stats']
            comprehensive_results['performance_summary']['system_resources'] = {
                'avg_cpu_percent': sum(s.get('cpu_percent', 0) for s in stats) / len(stats) if stats else 0,
                'max_cpu_percent': max(s.get('cpu_percent', 0) for s in stats) if stats else 0,
                'avg_memory_used_gb': sum(s.get('memory_used_gb', 0) for s in stats) / len(stats) if stats else 0,
                'max_memory_used_gb': max(s.get('memory_used_gb', 0) for s in stats) if stats else 0,
                'monitoring_samples': len(stats)
            }
            
            gpu_stats = [s for s in stats if 'gpu_memory_used_gb' in s]
            if gpu_stats:
                comprehensive_results['performance_summary']['system_resources']['gpu'] = {
                    'avg_gpu_memory_used_gb': sum(s['gpu_memory_used_gb'] for s in gpu_stats) / len(gpu_stats),
                    'max_gpu_memory_used_gb': max(s['gpu_memory_used_gb'] for s in gpu_stats),
                    'avg_gpu_utilization_percent': sum(s.get('gpu_utilization', 0) for s in gpu_stats) / len(gpu_stats),
                    'max_gpu_utilization_percent': max(s.get('gpu_utilization', 0) for s in gpu_stats)
                }
        
        model_name_safe = results['model'].replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f"{model_name_safe}_results.json"
        
        if results_directory:
            if not os.path.exists(results_directory):
                os.makedirs(results_directory)
                print(f"Created directory: {results_directory}")
            filepath = os.path.join(results_directory, filename)
        else:
            filepath = filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(comprehensive_results, f, indent=2, default=str)
            print(f"\nComprehensive results saved to: {filepath}")
            
            file_size = os.path.getsize(filepath)
            print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def create_comparison_table(self, all_model_results: list[dict]) -> tuple[str, dict]:
        """
        Creates a human-readable comparison table and a structured comparison data dictionary
        from the benchmark results of multiple models. The table is formatted using `tabulate`.

        Args:
            all_model_results (list[dict]): A list of dictionaries, where each dictionary
                                            contains the benchmark results for a single model.

        Returns:
            tuple[str, dict]: A tuple containing:
                              - str: The formatted comparison table.
                              - dict: A structured dictionary with detailed comparison data.
                              Returns (None, None) if no results are provided.
        """
        if not all_model_results:
            return None, None
        
        table_data = []
        comparison_data = {
            'comparison_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_models_tested': len(all_model_results),
                'benchmark_version': '1.0'
            },
            'model_comparisons': []
        }
        
        for result in all_model_results:
            individual = result.get('individual_results', [])
            if not individual:
                continue
                
            avg_tokens_per_second = sum(r['tokens_per_second'] for r in individual) / len(individual)
            avg_response_time = sum(r['total_time'] for r in individual) / len(individual)
            total_tokens = sum(r['completion_tokens'] for r in individual)
            
            system_stats = result.get('system_stats', [])
            avg_cpu = 0
            max_memory = 0
            avg_gpu_util = 0
            max_gpu_memory = 0
            
            if system_stats:
                avg_cpu = sum(s.get('cpu_percent', 0) for s in system_stats) / len(system_stats)
                max_memory = max(s.get('memory_used_gb', 0) for s in system_stats)
                
                gpu_stats = [s for s in system_stats if 'gpu_memory_used_gb' in s]
                if gpu_stats:
                    avg_gpu_util = sum(s.get('gpu_utilization', 0) for s in gpu_stats) / len(gpu_stats)
                    max_gpu_memory = max(s.get('gpu_memory_used_gb', 0) for s in gpu_stats)
            
            row = [
                result['model'],
                f"{avg_tokens_per_second:.2f}",
                f"{avg_response_time:.2f}s",
                str(total_tokens),
                f"{avg_cpu:.1f}%",
                f"{max_memory:.2f}GB",
                f"{avg_gpu_util:.1f}%" if avg_gpu_util > 0 else "N/A",
                f"{max_gpu_memory:.2f}GB" if max_gpu_memory > 0 else "N/A"
            ]
            table_data.append(row)
            
            model_comparison = {
                'model_name': result['model'],
                'performance_metrics': {
                    'avg_tokens_per_second': avg_tokens_per_second,
                    'avg_response_time_seconds': avg_response_time,
                    'total_completion_tokens': total_tokens,
                    'prompts_tested': len(individual)
                },
                'resource_usage': {
                    'avg_cpu_percent': avg_cpu,
                    'max_memory_used_gb': max_memory,
                    'avg_gpu_utilization_percent': avg_gpu_util if avg_gpu_util > 0 else None,
                    'max_gpu_memory_used_gb': max_gpu_memory if max_gpu_memory > 0 else None
                },
                'detailed_results': individual,
                'system_monitoring': system_stats
            }
            comparison_data['model_comparisons'].append(model_comparison)
        
        table_data.sort(key=lambda x: float(x[1]), reverse=True)
        comparison_data['model_comparisons'].sort(key=lambda x: x['performance_metrics']['avg_tokens_per_second'], reverse=True)
        
        headers = [
            "Model", "Avg Tokens/s", "Avg Time", "Total Tokens",
            "Avg CPU", "Max RAM", "Avg GPU", "Max VRAM"
        ]
        
        table = tabulate(table_data, headers=headers, tablefmt="github")
        
        comparison_data['performance_ranking'] = []
        for i, model_data in enumerate(comparison_data['model_comparisons']):
            comparison_data['performance_ranking'].append({
                'rank': i + 1,
                'model_name': model_data['model_name'],
                'tokens_per_second': model_data['performance_metrics']['avg_tokens_per_second']
            })
        
        if comparison_data['model_comparisons']:
            best_performance = comparison_data['model_comparisons'][0]['performance_metrics']['avg_tokens_per_second']
            for model_data in comparison_data['model_comparisons']:
                current_performance = model_data['performance_metrics']['avg_tokens_per_second']
                relative_performance = (current_performance / best_performance) * 100
                model_data['performance_metrics']['relative_performance_percent'] = relative_performance
        
        return table, comparison_data
    
    def save_comparison_results(self, comparison_data: dict, results_directory: str = None, filename_prefix: str = "") -> None:
        """
        Saves the structured model comparison results to a JSON file.

        Args:
            comparison_data (dict): The dictionary containing detailed comparison data for multiple models.
            results_directory (str, optional): The directory where the JSON file will be saved.
                                               Defaults to the current directory if None.
            filename_prefix (str): A prefix to add to the filename. Defaults to "".
        """
        filename = f"{filename_prefix}model_comparison.json"
        
        if results_directory:
            if not os.path.exists(results_directory):
                os.makedirs(results_directory)
            filepath = os.path.join(results_directory, filename)
        else:
            filepath = filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(comparison_data, f, indent=2, default=str)
            print(f"\nModel comparison results saved to: {filepath}")
            
            file_size = os.path.getsize(filepath)
            print(f"Comparison file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
        except Exception as e:
            print(f"Error saving comparison results: {e}")
    
    def benchmark_multiple_models(self, model_names: list[str], prompts: list[str], max_tokens: int = 100, temperature: float = 0.7,
                                 store_results: bool = False, results_directory: str = None, timeout: int = 240) -> list[dict]:
        """
        Orchestrates the benchmarking process for multiple LLM models.
        Iterates through a list of model names, runs individual benchmarks,
        and collects all results.

        Args:
            model_names (list[str]): A list of model names to benchmark.
            prompts (list[str]): A list of text prompts to use for benchmarking each model.
            max_tokens (int): The maximum number of tokens the model should generate per response. Defaults to 100.
            temperature (float): The sampling temperature for text generation. Defaults to 0.7.
            store_results (bool): If True, saves individual model benchmark results. Defaults to False.
            results_directory (str, optional): Directory to save individual and comparative results. Defaults to None.
            timeout (int): Timeout in seconds for each API request. Defaults to 240.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains the
                        comprehensive benchmark results for a single model.
        """
        all_results = []
        
        print(f"\n=== Starting Multi-Model Benchmark ===")
        print(f"Models to test: {', '.join(model_names)}")
        print(f"Total models: {len(model_names)}")
        
        for i, model_name in enumerate(model_names, 1):
            print(f"\n{'='*60}")
            print(f"Benchmarking Model {i}/{len(model_names)}: {model_name}")
            print(f"{'='*60}")
            
            try:
                test_response = requests.post(
                    f"{self.api_endpoint}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 1,
                        "temperature": 0.1
                    },
                    timeout=30
                )
                
                if test_response.status_code != 200:
                    print(f"❌ Model '{model_name}' is not available or not loaded. Skipping...")
                    print(f"   Error: {test_response.status_code} - {test_response.text}")
                    continue
                    
            except Exception as e:
                print(f"❌ Could not connect to model '{model_name}': {e}")
                continue
            
            try:
                result = self.benchmark_model(model_name, prompts, max_tokens, temperature, results_directory, timeout=timeout)
                all_results.append(result)
                
                self.analyze_results(result, store_results, results_directory)
                
                print(f"✅ Completed benchmark for {model_name}")
                
            except Exception as e:
                print(f"❌ Error benchmarking {model_name}: {e}")
                continue
            
            if i < len(model_names):
                print(f"\nPausing 2 seconds before next model...")
                time.sleep(2)
        
        return all_results
        return all_results
