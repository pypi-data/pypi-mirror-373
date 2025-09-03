"""
Python Analyzer Script

This script provides functionality to analyze Python code files and generate markdown documentation 
for classes and functions found in those files. It parses Python AST (Abstract Syntax Tree) to 
extract class definitions, method signatures, decorators, and docstrings.

Key features:
- Generates markdown documentation for Python files
- Extracts class definitions with their methods and decorators  
- Parses function definitions including arguments and docstrings
- Supports both standalone functions and class-based methods
- Handles nested function structures in classes

Usage examples:
1. Generate documentation for a single file: 
   PythonAnalyzer.get_definitions_markdown_for_file('example.py')

2. Generate documentation for all Python files in a directory:
   PythonAnalyzer.create_markdown_documentation_for_directory('/path/to/project', 'output.md')

3. Parse AST from a file:
   PythonAnalyzer._parse_ast('example.py')
   
Parameters:
- directory_path: Path to the directory containing Python files
- target_file: Output file path for documentation  
- filepath: Path to the specific Python file to analyze
- verbose: Boolean flag for detailed output

Functions:
1. create_markdown_documentation_for_directory - Creates documentation for all Python files in a directory
2. get_definitions_markdown_for_file - Generates markdown from a single file  
3. _parse_ast - Parses Python file into AST
4. _extract_decorators - Extracts decorator information from nodes
5. _extract_args - Parses function arguments and type hints  
6. _extract_class_info - Extracts class information including methods
7. _extract_function_info - Extracts function information 
8. _get_class_and_function_definitions - Main parsing function that walks AST
9. _format_md_class - Formats class information as markdown
10. _format_md_function - Formats function information as markdown

This script is designed to be used in code documentation workflows and can 
generate comprehensive technical documentation for Python projects.
"""
from sokrates import FileHelper
from sokrates import OutputPrinter
import ast
import os
from typing import Tuple, List, Dict, Any

class PythonAnalyzer:
    @staticmethod
    def create_markdown_documentation_for_directory(directory_path: str, target_file: str, verbose: bool = False) -> str:
        """
        Creates markdown documentation for all Python files in a directory.

        This method walks through the specified directory and generates markdown documentation 
        for each Python file (excluding __init__.py files). It collects all
        class and function definitions from each Python file and combines them into 
        a single markdown document.

        Args:
            directory_path (str): Path to the directory containing Python files
            target_file (str): Output file path where documentation will be written  
            verbose (bool, optional): If True, prints detailed output. Defaults to False
            
        Returns:
            str: The complete markdown analysis as a string
            
        Side Effects:
            - Writes documentation to the target file specified
            - Prints directory contents if verbose is True
        """
        file_paths = FileHelper.directory_tree(directory_path, sort=True, file_extensions=['.py'])
        file_paths = list(filter(lambda s: not "__init__.py" in s, file_paths))
        
        if verbose:
            print(f"Python files to summarize:")
            for file_path in file_paths:
                print(file_path)
        
        full_analysis = ""
        for file_path in file_paths:
            full_analysis = f"{full_analysis}\n{PythonAnalyzer.get_definitions_markdown_for_file(file_path)}"
            
        FileHelper.write_to_file(target_file,full_analysis, verbose=verbose)
        OutputPrinter.print_file_created(target_file)
        return full_analysis
    
    @staticmethod
    def get_definitions_markdown_for_file(filepath: str) -> str:
        """Print all class and function definitions in markdown format."""
        full_md_string = ""
        try:
            classes, functions = PythonAnalyzer._get_class_and_function_definitions(filepath)
            
            full_md_string = f"{full_md_string}# Filepath: `{filepath}`"
            
            # Print classes and their methods together
            if classes:
                full_md_string = f"{full_md_string}\n## Classes"
                for cls_info in classes:
                    full_md_string = f"{full_md_string}\n{PythonAnalyzer._format_md_class(cls_info)}"
                full_md_string = f"{full_md_string}\n---"
            
            # Print top-level functions if classes exist (to show all)
            if not classes and functions:
                full_md_string = f"{full_md_string}\n## Functions"
                for func_info in functions:
                    full_md_string = f"{full_md_string}\n{PythonAnalyzer._format_md_function(func_info)}"
                full_md_string = f"{full_md_string}\n---"
            elif classes and functions:
                # Show standalone functions if any
                standalone_functions = [f for f in functions 
                                if not any(f['name'] in [m['name'] for m in c.get('methods', [])] 
                                          for c in classes)]
                if standalone_functions:
                    full_md_string = f"{full_md_string}\n## Standalone Functions"
                    for func_info in standalone_functions:
                        full_md_string = f"{full_md_string}\n{PythonAnalyzer._format_md_function(func_info)}"
                    full_md_string = f"{full_md_string}\n---"
            return full_md_string
        except Exception as e:
            print(f"Error: {e}")
            raise e

    # ----------------------------------------------------------
    # private helpers 
    # ----------------------------------------------------------
    @staticmethod
    def _parse_ast(filepath: str) -> ast.AST:
        """
        Parses a Python file into an Abstract Syntax Tree (AST).
        
        This method reads the content of a Python file and parses it into an 
        Abstract Syntax Tree (AST) which can be used for code analysis.
        
        Args:
            filepath (str): Path to the Python file to parse
            
        Returns:
            ast.AST: The parsed Abstract Syntax Tree object
            
        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the file is not a Python file (.py extension)
            SyntaxError: If there are syntax errors in the Python file
            
        Side Effects:
            - Reads and parses a Python file from disk
            - Raises exceptions for invalid files or syntax errors
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not filepath.endswith('.py'):
            raise ValueError("File must be a Python file (.py)")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        try:
            return ast.parse(file_content)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {filepath}: {e}")

    @staticmethod
    def _extract_decorators(node) -> List[str]:
        """Extract decorator information from a node."""
        if hasattr(node, 'decorator_list'):
            return [ast.dump(decorator) for decorator in node.decorator_list]
        return []

    @staticmethod
    def _extract_args(args_node: ast.arguments) -> List[Dict[str, Any]]:
        """Extract argument information from function arguments."""
        result = []
        
        # Handle regular arguments
        if hasattr(args_node, 'args') and args_node.args:
            for arg in args_node.args:
                if isinstance(arg, ast.arg):
                    annotation = None
                    
                    # Extract type hint information
                    if hasattr(arg, 'annotation') and arg.annotation:
                        if isinstance(arg.annotation, ast.Name):
                            annotation = arg.annotation.id
                        elif isinstance(arg.annotation, ast.Subscript):
                            annotation = f"{arg.annotation.value.id}[{str(arg.annotation.slice)}]"
                    
                    result.append({
                        'name': arg.arg,
                        'annotation': annotation,
                        'has_default': False,
                        'default_value': None
                    })
        
        # Handle varargs and kwargs
        if hasattr(args_node, 'vararg') and args_node.vararg:
            result.append({
                'name': args_node.vararg.arg,
                'annotation': getattr(args_node.vararg, 'annotation', None),
                'is_vararg': True,
                'has_default': False,
                'default_value': None
            })
        
        if hasattr(args_node, 'kwarg') and args_node.kwarg:
            result.append({
                'name': args_node.kwarg.arg,
                'annotation': getattr(args_node.kwarg, 'annotation', None),
                'is_kwarg': True,
                'has_default': False,
                'default_value': None
            })
        
        return result

    @staticmethod
    def _extract_class_info(cls_node: ast.ClassDef) -> Dict[str, Any]:
        """Extract class information including methods."""
        # Extract decorators for the class
        decorators = PythonAnalyzer._extract_decorators(cls_node)
        
        methods = []
        for node in cls_node.body:
            if isinstance(node, ast.FunctionDef):
                # Extract decorators and method information
                method_decorators = PythonAnalyzer._extract_decorators(node)
                
                method_info = {
                    'name': node.name,
                    'line_number': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'decorators': method_decorators,
                    'args': PythonAnalyzer._extract_args(node.args)
                }
                methods.append(method_info)
        
        return {
            'name': cls_node.name,
            'line_number': cls_node.lineno,
            'docstring': ast.get_docstring(cls_node),
            'decorators': decorators,
            'methods': methods
        }

    @staticmethod
    def _extract_function_info(func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract enhanced function information including return type and complexity metrics."""
        decorators = PythonAnalyzer._extract_decorators(func_node)
        
        # Extract return type annotation
        return_annotation = None
        if func_node.returns:
            if isinstance(func_node.returns, ast.Name):
                return_annotation = func_node.returns.id
            elif isinstance(func_node.returns, ast.Subscript):
                return_annotation = f"{func_node.returns.value.id}[{str(func_node.returns.slice)}]"
        
        # Analyze function complexity
        complexity_metrics = PythonAnalyzer._analyze_function_complexity(func_node)
        
        # Check for error handling patterns
        exception_handling = PythonAnalyzer._extract_exception_patterns(func_node)
        
        return {
            'name': func_node.name,
            'line_number': func_node.lineno,
            'docstring': ast.get_docstring(func_node),
            'decorators': decorators,
            'args': PythonAnalyzer._extract_args(func_node.args),
            'return_type': return_annotation,
            'complexity_metrics': complexity_metrics,
            'exception_handling': exception_handling
        }

    @staticmethod
    def _analyze_function_complexity(func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze function complexity metrics."""
        cyclomatic_complexity = 1  # Base complexity
        
        # Count decision points (if statements, for loops, while loops, etc.)
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.AsyncFor)):
                cyclomatic_complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                cyclomatic_complexity += 1
        
        # Count function calls to estimate complexity
        call_count = 0
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                call_count += 1
        
        return {
            'cyclomatic_complexity': cyclomatic_complexity,
            'call_count': call_count,
            'has_loops': any(isinstance(n, (ast.For, ast.While, ast.AsyncFor)) for n in ast.walk(func_node)),
            'has_conditionals': any(isinstance(n, ast.If) for n in ast.walk(func_node))
        }

    @staticmethod
    def _extract_exception_patterns(func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract exception handling patterns from function."""
        exceptions_caught = []
        exceptions_raised = []
        
        # Look for try-except blocks and raise statements
        for node in ast.walk(func_node):
            if isinstance(node, ast.ExceptHandler):
                if isinstance(node.type, (ast.Name, ast.Tuple)):
                    if isinstance(node.type, ast.Name):
                        exceptions_caught.append(node.type.id)
                    else:
                        # Handle tuple of exception types
                        for exc_type in node.type.elts:
                            if isinstance(exc_type, ast.Name):
                                exceptions_caught.append(exc_type.id)
            
            elif isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    exceptions_raised.append(node.exc.func.id)
        
        return {
            'exceptions_caught': list(set(exceptions_caught)),
            'exceptions_raised': list(set(exceptions_raised)),
            'has_exception_handling': len(exceptions_caught) > 0,
            'has_raise_statements': len(exceptions_raised) > 0
        }

    @staticmethod
    def _get_class_and_function_definitions(filepath: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse a Python file and return lists of class and function definitions.
        
        Args:
            filepath (str): Path to the Python file
            
        Returns:
            tuple: (classes, functions) where each is a list of dictionaries
        """
        tree = PythonAnalyzer._parse_ast(filepath)
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(PythonAnalyzer._extract_class_info(node))
            elif isinstance(node, ast.FunctionDef):
                functions.append(PythonAnalyzer._extract_function_info(node))
        return classes, functions

    @staticmethod
    def get_test_file_context(test_filepath: str) -> Dict[str, Any]:
        """
        Extract test-related information from existing test files.
        
        Args:
            test_filepath (str): Path to the test file
            
        Returns:
            Dict[str, Any]: Test context including test functions and patterns
        """
        try:
            tree = PythonAnalyzer._parse_ast(test_filepath)
            
            test_functions = []
            test_patterns = {
                'uses_pytest': False,
                'uses_unittest': False,
                'has_fixtures': [],
                'has_parametrize': False,
                'mock_usage': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_functions.append(PythonAnalyzer._extract_function_info(node))
                    
                    # Check for pytest fixtures
                    for decorator in getattr(node, 'decorator_list', []):
                        if hasattr(decorator, 'id') and decorator.id == 'pytest.fixture':
                            test_patterns['has_fixtures'].append(node.name)
                        
                        # Check for parametrize decorators
                        if (hasattr(decorator, 'func') and
                            hasattr(decorator.func, 'id') and
                            decorator.func.id == 'parametrize'):
                            test_patterns['has_parametrize'] = True
                
                # Check for pytest imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if 'pytest' in alias.name:
                            test_patterns['uses_pytest'] = True
                elif isinstance(node, ast.ImportFrom):
                    if (node.module and
                        ('pytest' in node.module or 'unittest' in node.module)):
                        if 'pytest' in node.module:
                            test_patterns['uses_pytest'] = True
                        else:
                            test_patterns['uses_unittest'] = True
            
            return {
                'filepath': test_filepath,
                'test_functions': test_functions,
                'patterns': test_patterns,
                'existing_tests_count': len(test_functions)
            }
            
        except Exception as e:
            return {
                'filepath': test_filepath,
                'error': str(e),
                'test_functions': [],
                'patterns': {
                    'uses_pytest': False,
                    'uses_unittest': False,
                    'has_fixtures': [],
                    'has_parametrize': False,
                    'mock_usage': []
                },
                'existing_tests_count': 0
            }

    @staticmethod
    def analyze_source_file(source_filepath: str, test_filepath: str = None) -> Dict[str, Any]:
        """
        Analyze source code for a given source file, optionally considering existing tests for the code.
        
        Args:
            source_filepath (str): Path to the source Python file
            test_filepath (str, optional): Path to existing test file if any
            
        Returns:
            Dict[str, Any]: Complete analysis of the code in the source filepath
        """
        # Analyze source code
        classes, functions = PythonAnalyzer._get_class_and_function_definitions(source_filepath)
        
        result = {
            'source_file': {
                'filepath': source_filepath,
                'classes': classes,
                'functions': functions,
                'total_functions': len(functions),
                'total_classes': len(classes)
            }
        }
        
        # Add existing test context if provided
        if test_filepath and os.path.exists(test_filepath):
            result['existing_tests'] = PythonAnalyzer.get_test_file_context(test_filepath)
        else:
            result['existing_tests'] = None
        
        return result

    @staticmethod
    def _format_md_class(cls_info: Dict[str, Any]) -> str:
        """Format class information as markdown."""
        md_lines = []
        
        # Class header
        decorators_str = ""
        if cls_info.get('decorators'):
            decorators_str = " ".join(cls_info['decorators']) + " "
        
        md_lines.append(f"\n### {decorators_str} `{cls_info['name']}` (Line Number: {cls_info['line_number']})")
        
        # Docstring
        if cls_info.get('docstring'):
            md_lines.append(f"#### Docstring:\n```\n{cls_info['docstring']}\n```")
        
        # Methods
        if cls_info.get('methods'):
            md_lines.append("\n#### Methods")
            for method in cls_info['methods']:
                # Method header
                method_decorators_str = ""
                if method.get('decorators'):
                    method_decorators_str = " ".join(method['decorators']) + " "
                
                arg_signature = "()"
                if method.get('args'):
                    args_list = [arg['name'] for arg in method['args']]
                    arg_signature = f"({', '.join(args_list)})"
                
                md_lines.append(f"##### {method_decorators_str} `{method['name']}{arg_signature}` (Line Number: {method['line_number']})")
                
                # Method docstring
                if method.get('docstring'):
                    md_lines.append(f"##### Docstring:\n```\n{method['docstring']}\n```")
        return "\n".join(md_lines)

    @staticmethod
    def _format_md_function(func_info: Dict[str, Any]) -> str:
        """Format function information as markdown."""
        
        md_lines = []
        # Function header
        decorators_str = ""
        if func_info.get('decorators'):
            decorators_str = " ".join(func_info['decorators']) + " "
            
        arg_signature = "()"
        if func_info.get('args'):
            args_list = [arg['name'] for arg in func_info['args']]
            arg_signature = f"({', '.join(args_list)})"
        
        md_lines.append(f"##### {decorators_str} `{func_info['name']}{arg_signature}` (Line Number: {func_info['line_number']})")
        
        # Docstring
        if func_info.get('docstring'):
            md_lines.append(f"#### Docstring:\n```\n{func_info['docstring']}\n```")
        
        return "\n".join(md_lines)