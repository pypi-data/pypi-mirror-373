"""
Test Generator Module

This module implements the core test generation functionality for the Smart Test Generator feature.
It orchestrates the process of analyzing Python code, preparing context-rich prompts,
and generating comprehensive pytest-compatible test files using LLM analysis.

Key features:
- Analyzes Python source code to extract function/class information
- Prepares structured prompts with multiple template strategies
- Generates tests using configurable LLM models and parameters
- Outputs pytest-compatible test files with proper structure
- Integrates with existing sokrates infrastructure

Usage examples:
1. Generate tests for a single file:
   generator = TestGenerator(model="gpt-4")
   results = generator.generate_tests(file_paths=["src/module.py"], output_dir="./tests")

2. Generate tests for a directory:
   results = generator.generate_tests(directory_path="./src", output_dir="./tests")

3. Custom prompt templates and strategies:
   generator.set_prompt_template("edge_cases", custom_template)
   results = generator.generate_tests(..., strategy="edge_cases")
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from .python_analyzer import PythonAnalyzer
from sokrates.llm_api import LLMApi
from sokrates.file_helper import FileHelper
from sokrates.output_printer import OutputPrinter
from sokrates.prompt_refiner import PromptRefiner
from sokrates.colors import Colors


class TestGenerator:
    """
    Core test generation class that orchestrates the process of analyzing code,
    preparing prompts, and generating comprehensive pytest-compatible tests.
    
    This class serves as the main interface for the Smart Test Generator feature,
    coordinating between code analysis, LLM processing, and file output.
    """
    
    # Default prompt template paths
    DEFAULT_PROMPT_TEMPLATES = {
        "base": str(Path(__file__).parent.parent / "prompts/coding/test_generation_base.md"),
        "edge_cases": str(Path(__file__).parent.parent / "prompts/coding/test_generation_edge_cases.md"), 
        "error_handling": str(Path(__file__).parent.parent / "prompts/coding/test_generation_error_handling.md"),
        "validation": str(Path(__file__).parent.parent / "prompts/coding/test_generation_validation.md"),
        "all": str(Path(__file__).parent.parent / "prompts/coding/test_generation_all.md")
    }
    
    def __init__(self, model: str = None, api_endpoint: str = None, 
                 api_key: str = 'notrequired', temperature: float = 0.7, 
                 max_tokens: int = 2000, verbose: bool = False):
        """
        Initialize the TestGenerator with LLM configuration.
        
        Args:
            model (str): LLM model name to use for test generation
            api_endpoint (str): Custom API endpoint for LLM calls
            api_key (str): API key for authentication with LLM service  
            temperature (float): Sampling temperature for responses (default: 0.7)
            max_tokens (int): Maximum tokens for test generation (default: 2000)
            verbose (bool): Enable verbose output during processing
        """
        self.verbose = verbose
        self.llm_api = LLMApi(
            api_endpoint=api_endpoint, 
            api_key=api_key
        )
        self.refiner = PromptRefiner(verbose=verbose)
        
        # Use provided model or fall back to default from config
        self.model = model
        
        # LLM generation parameters
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Prompt templates - can be customized per strategy
        self.prompt_templates = self.DEFAULT_PROMPT_TEMPLATES.copy()
        
        if self.verbose:
            print(f"{Colors.BLUE}{Colors.BOLD}TestGenerator initialized:{Colors.RESET}")
            print(f"   Model: {self.model or 'default'}")
            print(f"   Temperature: {temperature}")
            print(f"   Max tokens: {max_tokens}")

    def set_prompt_template(self, strategy: str, template_path: str) -> None:
        """
        Set a custom prompt template for a specific test generation strategy.
        
        Args:
            strategy (str): The strategy name ("base", "edge_cases", etc.)
            template_path (str): Path to the custom prompt template file
        """
        self.prompt_templates[strategy] = template_path
        if self.verbose:
            print(f"Custom prompt template set for '{strategy}': {template_path}")

    def generate_tests(self, directory_path: str = None, file_paths: List[str] = None,
                      output_dir: str = "tests", strategy: str = "all") -> Dict[str, Any]:
        """
        Generate tests for Python files using the specified strategy.
        
        Args:
            directory_path (str): Directory containing Python files to test
            file_paths (List[str]): Specific Python files to generate tests for
            output_dir (str): Directory for output test files (default: "tests")
            strategy (str): Test generation strategy ("base", "edge_cases", "error_handling", "validation")
            
        Returns:
            Dict[str, Any]: Results containing test generation statistics and file paths
            
        Raises:
            ValueError: If neither directory_path nor file_paths is specified
            FileNotFoundError: If specified files or directories don't exist
        """
        if self.verbose:
            OutputPrinter.print_header("🚀 Smart Test Generation 🚀", Colors.BRIGHT_CYAN, 50)
        
        # Validate input parameters
        if not directory_path and not file_paths:
            raise ValueError("Either directory_path or file_paths must be specified")
            
        # Prepare source files for processing
        source_files = self._prepare_source_files(directory_path, file_paths)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        if self.verbose:
            print(f"Processing {len(source_files)} source files...")
            print(f"Output directory: {output_dir}")
            print(f"Strategy: {strategy}")

        results = {
            'total_files_processed': len(source_files),
            'tests_generated': 0,
            'files_created': [],
            'errors': []
        }

        # Process each source file
        for source_file in source_files:
            try:
                result = self._generate_tests_for_file(
                    source_file, output_dir, strategy
                )
                
                results['tests_generated'] += result.get('tests_generated', 0)
                results['files_created'].extend(result.get('files_created', []))
                
                if result['error']:
                    results['errors'].append({
                        'file': source_file,
                        'error': result['error']
                    })
                    
            except Exception as e:
                error_msg = f"Error processing {source_file}: {str(e)}"
                results['errors'].append({'file': source_file, 'error': error_msg})
                
                if self.verbose:
                    print(f"{Colors.RED}Error: {error_msg}{Colors.RESET}")

        # Print summary
        if self.verbose:
            OutputPrinter.print_success("Test generation completed!")
            print(f"   Files processed: {results['total_files_processed']}")
            print(f"   Tests generated: {results['tests_generated']}")
            print(f"   Test files created: {results['files_created']}")
            
            if results['errors']:
                print(f"{Colors.YELLOW}⚠️  Errors encountered: {len(results['errors'])}{Colors.RESET}")

        return results

    def _prepare_source_files(self, directory_path: str = None, 
                             file_paths: List[str] = None) -> List[str]:
        """
        Prepare list of source files for test generation.
        
        Args:
            directory_path (str): Directory to scan for Python files
            file_paths (List[str]): Specific file paths
            
        Returns:
            List[str]: List of absolute file paths to process
        """
        if directory_path:
            # Scan directory for Python files
            python_files = FileHelper.directory_tree(
                directory_path, 
                file_extensions=['.py'],
                sort=True
            )
            
            # Filter out test files and __init__.py files
            filtered_files = [
                f for f in python_files 
                if not (f.endswith('_test.py') or f.endswith('test_*.py') or '__init__.py' in f)
            ]
            
            if self.verbose:
                print(f"Found {len(filtered_files)} Python files in directory: {directory_path}")
                
            return filtered_files
            
        elif file_paths:
            # Validate specific files exist
            validated_files = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                if not file_path.endswith('.py'):
                    continue  # Skip non-Python files
                validated_files.append(os.path.abspath(file_path))
            
            if self.verbose:
                print(f"Processing {len(validated_files)} specified Python files")
                
            return validated_files

    def _generate_tests_for_file(self, source_file: str, output_dir: str, 
                                 strategy: str) -> Dict[str, Any]:
        """
        Generate tests for a single source file.
        
        Args:
            source_file (str): Path to the source Python file
            output_dir (str): Output directory for test files
            strategy (str): Test generation strategy
            
        Returns:
            Dict[str, Any]: Results for this specific file
        """
        result = {
            'source_file': source_file,
            'tests_generated': 0,
            'files_created': [],
            'error': None
        }
        
        try:
            # Check if test file already exists
            test_filename = f"test_{os.path.basename(source_file)}"
            test_filepath = os.path.join(output_dir, test_filename)
            
            existing_test_context = None
            if os.path.exists(test_filepath):
                existing_test_context = PythonAnalyzer.get_test_file_context(test_filepath)
                
                if self.verbose:
                    print(f"   Existing test file found: {test_filepath}")
            
            source_file_content = FileHelper.read_file(source_file, verbose=self.verbose)
            
            # Prepare prompt based on strategy
            prompt_template_path = self.prompt_templates.get(strategy, self.prompt_templates["base"])
            prompt_template = FileHelper.read_file(prompt_template_path, verbose=self.verbose)
            
            # Build context-rich prompt
            prompt = self._build_test_generation_prompt(
                prompt_template, source_file, source_file_content, existing_test_context
            )
            
            if self.verbose:
                print(f"   Generating tests using strategy: {strategy}")
            
            # Send to LLM for test generation
            generated_tests = self.llm_api.send(
                prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            generated_tests = self.refiner.clean_response(generated_tests)
            
            # Clean and format the generated code
            cleaned_tests = self._clean_generated_code(generated_tests)
            
            # Write test file
            FileHelper.write_to_file(test_filepath, cleaned_tests, verbose=self.verbose)
            
            result.update({
                'tests_generated': self._count_test_functions(cleaned_tests),
                'files_created': [test_filepath],
                'generated_strategy': strategy
            })
            
            if self.verbose:
                OutputPrinter.print_file_created(test_filepath)
                
        except Exception as e:
            result['error'] = str(e)
            if self.verbose:
                print(f"{Colors.RED}Error generating tests for {source_file}: {e}{Colors.RESET}")

        return result

    def _build_test_generation_prompt(self, template: str, source_file_path: str, source_file_content: str,
                                    existing_context: Dict[str, Any] = None) -> str:
        """
        Build a context-rich prompt for test generation.
        
        Args:
            template (str): Base prompt template
            analysis_result (Dict[str, Any]): Code analysis results
            existing_context (Dict[str, Any]): Existing test file context if any
            
        Returns:
            str: Complete prompt ready for LLM processing
        """
        
        # Simple template substitution - replace all placeholders with their values
        prompt = template
        
        prompt = prompt.replace('{{source_file_path}}', source_file_path)
        prompt = prompt.replace('{{source_file_content}}', source_file_content)

        return prompt

    def _clean_generated_code(self, generated_code: str) -> str:
        """
        Clean and format the LLM-generated test code.
        
        Args:
            generated_code (str): Raw code from LLM
            
        Returns:
            str: Cleaned and formatted Python code
        """
        # Remove any markdown formatting if present
        if generated_code.startswith('```python'):
            lines = generated_code.split('\n')
            generated_code = '\n'.join(lines[1:-1])  # Remove ```python and ```
        
        # Ensure proper line endings
        generated_code = generated_code.strip()
        
        # Add file header if not present
        if 'import' not in generated_code[:100]:
            header = f'''"""
Automatically generated tests for {self.model or "LLM"} model.
Do not edit this file manually - regenerate using sokrates-generate-tests
"""

'''
            generated_code = header + generated_code
        
        return generated_code

    def _count_test_functions(self, code: str) -> int:
        """
        Count the number of test functions in generated code.
        
        Args:
            code (str): Generated Python code
            
        Returns:
            int: Number of test functions found
        """
        import re
        
        # Look for function definitions starting with 'test_'
        test_pattern = r'^def test_\w+\s*\('
        matches = re.findall(test_pattern, code, re.MULTILINE)
        return len(matches)

    def get_available_strategies(self) -> List[str]:
        """
        Get list of available test generation strategies.
        
        Returns:
            List[str]: Available strategy names
        """
        return list(self.prompt_templates.keys())

    def set_custom_strategy(self, name: str, template_path: str) -> None:
        """
        Define a custom test generation strategy with its own prompt template.
        
        Args:
            name (str): Name for the custom strategy
            template_path (str): Path to the custom prompt template file
        """
        self.prompt_templates[name] = template_path
        if self.verbose:
            print(f"Custom strategy '{name}' added using template: {template_path}")