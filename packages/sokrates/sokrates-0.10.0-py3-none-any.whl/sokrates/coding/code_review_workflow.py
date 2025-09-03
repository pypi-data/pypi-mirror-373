"""
Code Review Workflow Module

This module implements the core workflow for analyzing Python code and generating 
automated code reviews using LLMs. It leverages the existing PythonAnalyzer infrastructure
to extract structured code information, then applies appropriate prompt templates based on
the review type to generate comprehensive feedback.
"""

from sokrates.coding.python_analyzer import PythonAnalyzer
from sokrates.llm_api import LLMApi
from sokrates.file_helper import FileHelper
from sokrates.prompt_refiner import PromptRefiner
import os
from pathlib import Path
from typing import List, Dict, Any

# Maximum tokens for LLM responses - balances detail with performance
DEFAULT_MAX_TOKENS = 30000
DEFAULT_TEMPERATURE = 0.7

CODE_REVIEW_TYPE_ALL = "all"

class CodeReviewWorkflow:
    """
    A workflow class for performing code reviews on Python files using LLMs.
    
    This class orchestrates the process of analyzing Python code with PythonAnalyzer,
    preparing structured input data, and sending prompts to LLM APIs for review generation.
    """
    
    REVIEW_TYPES = [
        'style',
        'security',
        'performance',
        'quality'
    ]
    
    DEFAULT_CODING_PROMPT_PATH = Path(f"{Path(__file__).parent.parent.resolve()}/prompts/coding").resolve()
    
    PROMPT_TEMPLATES = {
        "style": str(DEFAULT_CODING_PROMPT_PATH / "style_review.md"),
        "security": str(DEFAULT_CODING_PROMPT_PATH / "security_review.md"),
        "performance": str(DEFAULT_CODING_PROMPT_PATH / "performance_review.md"),
        "quality": str(DEFAULT_CODING_PROMPT_PATH / "code_quality_review.md")
    }

    def __init__(self, verbose: bool = False, api_endpoint: str = None, api_key: str = None,
                 prompt_templates: Dict[str, str] = None):
        """
        Initialize the CodeReviewWorkflow.
        
        Args:
            verbose (bool): Enable verbose output
            api_endpoint (str): Custom API endpoint for LLM calls
            api_key (str): API key for authentication with LLM service
            prompt_templates (Dict[str, str]): Dictionary mapping review types to prompt template file paths.
                                            If None, uses default templates.
        """
        self.verbose = verbose
        self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
        self.prompt_refiner = PromptRefiner(verbose=verbose)
        
        # Use provided templates or fall back to defaults
        if prompt_templates:
            self.PROMPT_TEMPLATES = prompt_templates
            
        if self.verbose:
            print(f"Prompt template paths: {self.PROMPT_TEMPLATES}")
        
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze all Python files in a directory and return file contents.
        
        Args:
            directory_path (str): Path to the directory containing Python files
            
        Returns:
            Dict[str, Any]: Dictionary containing analysis results for each file
        """
        if self.verbose:
            print(f"Analyzing directory: {directory_path}")
            
        # Get all Python files in directory using file system handler
        python_files = FileHelper.directory_tree(directory_path, file_extensions=['.py'])
        python_files = [f for f in python_files if not '__init__.py' in f]
        python_files = [f for f in python_files if not '__init__.py' in f]
        
        return self.analyze_files(python_files)
    
    def analyze_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze specific Python files and return file contents.
        
        Args:
            file_paths (List[str]): List of paths to Python files to be analyzed.
                                   Each file should be a valid Python source code file path.
            
        Returns:
            Dict[str, Any]: Dictionary containing analysis results for each file.
                            Each entry includes 'filepath', 'file_content', 'classes', and 'functions' keys.
                            If an error occurs during analysis, the entry will contain an 'error' key instead.
        """
        if self.verbose:
            print(f"Analyzing {len(file_paths)} files")
            
        analysis_results = {}
        
        for file_path in file_paths:
            try:
                # Read full file content using FileHelper
                file_content = FileHelper.read_file(file_path, verbose=self.verbose)
                
                # Extract the raw AST data for more detailed analysis if needed
                classes, functions = PythonAnalyzer._get_class_and_function_definitions(file_path)
                
                analysis_results[file_path] = {
                    'filepath': file_path,
                    'file_content': file_content,
                    'classes': classes,
                    'functions': functions
                }
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                analysis_results[file_path] = {
                    'filepath': file_path,
                    'error': str(e),
                    'file_content': '',
                    'classes': [],
                    'functions': []
                }
                raise e
        
        return analysis_results

    def generate_review(self, model: str, code_analysis: Dict[str, Any], review_type: str = CODE_REVIEW_TYPE_ALL,
                        temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                        output_dir: str = None) -> Dict[str, Any]:
        """
        Generate a code review using LLM based on the analyzed code and specified review type.
        
        Args:
            code_analysis (Dict[str, Any]): Analysis results from analyze_directory or analyze_files
            review_type (str): Type of review to generate ("style", "security", "performance", "quality", "all")
            model (str): LLM model name to use for generation
            temperature (float): Sampling temperature for responses
            max_tokens (int): Maximum number of tokens for the review
            output_dir (str): Directory where markdown files will be saved immediately (optional)
            
        Returns:
            Dict[str, Any]: Dictionary containing the generated reviews
        """
        if self.verbose:
            print(f"Generating {review_type} review")
        
        # Prepare contextual file listing for multi-file reviews
        all_file_paths = code_analysis.keys()
        contextual_file_listing = ""
        if len(all_file_paths) > 1:
            contextual_file_listing = "## Directory listing (as context for the code to review)"
            for file_path in all_file_paths:
                contextual_file_listing = f"{contextual_file_listing}\n- {file_path}"
        
        # Determine which review types to generate
        if review_type == CODE_REVIEW_TYPE_ALL:
            review_types = self.REVIEW_TYPES
        else:
            review_types = [review_type]
            
        reviews = {}
        
        for file_path, analysis in code_analysis.items():
            if self.verbose:
                print(f"Processing {file_path}")
                
            # Generate individual reviews for this file
            file_reviews = self._generate_file_reviews(
                file_path=file_path, analysis=analysis, 
                review_types=review_types, contextual_file_listing=contextual_file_listing,
                model=model, temperature=temperature, max_tokens=max_tokens
            )
            
            reviews[file_path] = file_reviews
            
            # Save immediately if output directory is specified
            if output_dir:
                try:
                    self.generate_and_save_markdown_review(file_path=file_path, file_reviews=file_reviews, output_dir=output_dir, model=model)
                except Exception as e:
                    print(f"Warning: Failed to save review for {file_path} immediately: {e}")
            
        return reviews

    def _generate_file_reviews(self, model: str, file_path: str, analysis: Dict[str, Any],
                             review_types: List[str], contextual_file_listing: str,
                             temperature: float = DEFAULT_TEMPERATURE,
                             max_tokens: int = DEFAULT_MAX_TOKENS) -> Dict[str, Any]:
        """
        Generate reviews for a single file across multiple review types.
        
        Args:
            file_path (str): Path to the Python file being reviewed
            analysis (Dict[str, Any]): Analysis results for this file
            review_types (List[str]): List of review types to generate
            contextual_file_listing (str): Contextual information about all files being reviewed
            model (str): LLM model name to use for generation
            temperature (float): Sampling temperature for responses
            max_tokens (int): Maximum number of tokens for the review
            
        Returns:
            Dict[str, Any]: Dictionary containing reviews for this file
        """
        file_reviews = {}
        
        for review_type in review_types:
            try:
                # Prepare prompt template and content
                prompt_template = self._read_prompt_template(review_type)
                prompt = self._prepare_review_prompt(
                    prompt_template=prompt_template, 
                    contextual_file_listing=contextual_file_listing, 
                    file_path=file_path, 
                    file_content=analysis['file_content']
                )
                
                # Send to LLM for review generation
                response = self._call_llm_for_review(prompt=prompt, model=model,
                                    temperature=temperature, max_tokens=max_tokens)
                response = self.prompt_refiner.clean_response(response)
                
                file_reviews[review_type] = {
                    'review_type': review_type,
                    'file_path': file_path,
                    'prompt_template_used': self.PROMPT_TEMPLATES[review_type],
                    'generated_review': response
                }
                
            except Exception as e:
                print(f"Error generating {review_type} review for {file_path}: {e}")
                file_reviews[review_type] = {
                    'review_type': review_type,
                    'file_path': file_path,
                    'error': str(e),
                    'generated_review': None
                }
        
        return file_reviews

    def _read_prompt_template(self, review_type: str) -> str:
        """
        Read the prompt template for a specific review type.
        
        Args:
            review_type (str): Type of review to get template for
            
        Returns:
            str: Content of the prompt template
        """
        return FileHelper.read_file(self.PROMPT_TEMPLATES[review_type], verbose=self.verbose)

    def _prepare_review_prompt(self, prompt_template: str, contextual_file_listing: str,
                               file_path: str, file_content: str) -> str:
        """
        Prepare the complete review prompt by combining template and code content.
        
        Args:
            prompt_template (str): The base prompt template
            contextual_file_listing (str): Contextual information about all files
            file_path (str): Path to the current file being reviewed
            file_content (str): Content of the Python file
            
        Returns:
            str: Complete prompt ready for LLM processing
        """
        return (
            f"{prompt_template}\n\n"
            f"{contextual_file_listing}\n\n"
            f"## Code to Review\n"
            f"Filepath: {file_path}\n"
            "```\n"
            f"{file_content}\n"
            "```\n\n"
            "Please analyze this code and provide specific feedback based on the review criteria above."
        )

    def _call_llm_for_review(self, prompt: str, model: str,
                           temperature: float = DEFAULT_TEMPERATURE, 
                           max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """
        Send prompt to LLM API and return response.
        
        Args:
            prompt (str): Complete review prompt
            model (str): LLM model name to use for generation
            temperature (float): Sampling temperature for responses
            max_tokens (int): Maximum number of tokens for the review
            
        Returns:
            str: Response from LLM API
        """
        return self.llm_api.send(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
        
    def generate_and_save_markdown_review(self, file_path: str, file_reviews: Dict[str, Any], output_dir: str, model: str) -> str:
        """
        Generate and save a single code review to markdown file immediately.
        
        Args:
            file_path (str): Path to the original Python file
            file_reviews (Dict[str, Any]): Review results for this file
            output_dir (str): Directory where markdown files will be saved
            
        Returns:
            str: Path to created markdown file
            
        Raises:
            OSError: If there are issues with directory creation or file writing
            PermissionError: If lacking write permissions for the target location
        """
        if self.verbose:
            print(f"Generating and saving review for {file_path} to directory: {output_dir}")
            
        try:
            # Create output directory - this will be handled by write_to_file
            
            # Generate filename based on original file path
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            model_name = FileHelper.clean_name(model)
            output_file = os.path.join(output_dir, f"{name_without_ext}_{model_name}_review.md")
            
            # Create markdown content
            md_content = self._generate_markdown_content(base_name, file_reviews)
            
            # Write to file using FileHelper with enhanced error handling
            FileHelper.write_to_file(output_file, md_content, verbose=self.verbose)
            
            return output_file
            
        except PermissionError as e:
            raise OSError(f"Permission denied when writing review for {file_path}: {e}")
        except OSError as e:
            if "No space left on device" in str(e):
                raise OSError(f"Disk full - cannot save review for {file_path}")
            raise OSError(f"File system error while saving review for {file_path}: {e}")

    def _generate_markdown_content(self, base_name: str, file_reviews: Dict[str, Any]) -> str:
        """
        Generate markdown content from file reviews.
        
        Args:
            base_name (str): Base name of the original Python file
            file_reviews (Dict[str, Any]): Review results for this file
            
        Returns:
            str: Complete markdown content ready for writing to file
        """
        md_content = f"# Code Review for {base_name}\n\n"
        
        # Add individual reviews
        for review_type, review_data in file_reviews.items():
            md_content += f"\n## {review_type.capitalize()} Review\n\n"
            if 'generated_review' in review_data and review_data['generated_review']:
                md_content += review_data['generated_review']
            elif 'error' in review_data:
                md_content += f"Error during review generation: {review_data['error']}\n"
        
        return md_content


# For backward compatibility and direct usage
def run_code_review(api_endpoint: str, api_key: str, model: str, 
                directory_path: str, file_paths: List[str] = None,
                output_dir: str = "reviews", review_type: str = CODE_REVIEW_TYPE_ALL,
                max_tokens: int = DEFAULT_MAX_TOKENS, verbose: bool = False) -> Dict[str, Any]:
    """
    Convenience function to run a code review workflow.
    
    Args:
        directory_path (str): Path to directory containing Python files
        file_paths (List[str]): List of specific Python file paths
        output_dir (str): Directory for output markdown files
        review_type (str): Type of review ("style", "security", "performance", "quality", "all")
        model (str): LLM model name to use
        api_endpoint (str): Custom API endpoint
        api_key (str): API key for authentication
        max_tokens (int): Maximum number of tokens for the review
        verbose (bool): Enable verbose output
        
    Returns:
        Dict[str, Any]: Review results
    """
    workflow = CodeReviewWorkflow(verbose=verbose, 
                        api_endpoint=api_endpoint, 
                        api_key=api_key)
    
    # Analyze code based on input parameters
    analysis_results = _analyze_code_for_review(workflow, directory_path, file_paths)
        
    # Generate reviews - with immediate writing capability
    reviews = workflow.generate_review(code_analysis=analysis_results, 
                        model=model, 
                        review_type=review_type, 
                        max_tokens=max_tokens, 
                        output_dir=output_dir)
    
    return reviews

def _analyze_code_for_review(workflow: CodeReviewWorkflow, 
                directory_path: str = None,
                file_paths: List[str] = None) -> Dict[str, Any]:
    """
    Analyze code for review based on input parameters.
    
    Args:
        workflow (CodeReviewWorkflow): Initialized workflow instance
        directory_path (str): Path to directory containing Python files
        file_paths (List[str]): List of specific Python file paths
        
    Returns:
        Dict[str, Any]: Analysis results from analyze_directory or analyze_files
        
    Raises:
        ValueError: If neither directory_path nor file_paths is specified
    """
    if directory_path:
        return workflow.analyze_directory(directory_path)
    elif file_paths:
        return workflow.analyze_files(file_paths)
    else:
        raise ValueError("Either directory_path or file_paths must be specified")