#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from sokrates.workflows.refinement_workflow import RefinementWorkflow
from sokrates.colors import Colors
from sokrates.file_helper import FileHelper
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config
from .helper import Helper

DEFAULT_MAX_TOKENS = 5000

def main():
    """Main function for the task breakdown CLI tool.
    
    This function handles command-line arguments, processes the input task,
    and executes the breakdown workflow using the RefinementWorkflow.
    
    Returns:
        None
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
            description='Breaks down a given task into sub-tasks with complexity rating. Returns a json representation of the calculated tasks.',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

    parser.add_argument(
        '--api-endpoint',
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
        '--task', '-t',
        required=False,
        default=None,
        help='The full task description at hand as string'
    )

    parser.add_argument(
        '--task-file', '-tf',
        required=False,
        default=None,
        help='A filepath to a file with the task to break down'
    )
    
    parser.add_argument(
        '--model', '-m',
        default=None,
        help=f"The model to use for the task breakdown"
    )
    
    parser.add_argument(
        '--temperature',
        default=None,
        help=f"The temperature to use for the task breakdown"
    )

    parser.add_argument(
        '--output', '-o',
        help='Output filename to save the response (e.g., tasks.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )
    
    # context
    parser.add_argument(
        '--context-text', '-ct',
        default=None,
        help='Optional additional context text to prepend before the prompt'
    )
    parser.add_argument(
        '--context-files', '-cf',
        help='Optional comma separated additional context text file paths with content that should be prepended before the prompt'
    )
    parser.add_argument(
        '--context-directories', '-cd',
        default=None,
        help='Optional comma separated additional directory paths with files with content that should be prepended before the prompt'
    )
    
    parser.add_argument(
        '--max-tokens', '-mt',
        default=DEFAULT_MAX_TOKENS,
        help="Max number of output tokens to generate"
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)
    
    api_key = args.api_key or config.api_key
        
    api_endpoint = args.api_endpoint or config.api_endpoint
    
    model = args.model or config.default_model
        
    temperature = args.temperature or config.default_model_temperature

    if args.task and args.task_file:
        OutputPrinter.print_error("You cannot provide both a task-file and a task. Exiting.")
        sys.exit(1)
        
    if not args.task and not args.task_file:
        OutputPrinter.print_error("You did not provide a task via --task or --task-file. Exiting.")
        sys.exit(1)
    
    task = ""
    if args.task:
        task = args.task
        
    if args.task_file:
        task = FileHelper.read_file(args.task_file, verbose=args.verbose)
        
    # context
    context = Helper.construct_context_from_arguments(
        context_text=args.context_text,
        context_directories=args.context_directories,
        context_files=args.context_files)
    
    OutputPrinter.print_info("api-endpoint", api_endpoint)
    OutputPrinter.print_info("model", model)
    OutputPrinter.print_info("temperature", temperature)
    OutputPrinter.print_info("max-tokens", args.max_tokens)
        
    workflow = RefinementWorkflow(api_endpoint=api_endpoint, 
        api_key=api_key, model=model, 
        max_tokens=args.max_tokens, 
        temperature=temperature,
        verbose=args.verbose
    )
    result = workflow.breakdown_task(task=task, context=context)

    OutputPrinter.print_section("RESULT", Colors.BRIGHT_BLUE, "═")
    print(result)
    
    if args.output:
        OutputPrinter.print_info("Writing task list to file:", args.output, Colors.BRIGHT_MAGENTA)
        FileHelper.write_to_file(args.output, result, verbose=args.verbose)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
