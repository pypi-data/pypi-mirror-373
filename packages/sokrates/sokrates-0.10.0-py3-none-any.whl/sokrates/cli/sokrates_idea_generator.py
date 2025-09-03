#!/usr/bin/env python3
# TODO: Code review this script and refine
# TODO: add temperature settings per stage

import argparse
import sys

from sokrates.workflows.idea_generation_workflow import IdeaGenerationWorkflow
from sokrates.output_printer import OutputPrinter
from sokrates import Colors, Config, FileHelper

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Idea generator workflow: Generate topic or set topic -> Prompt Generator -> Execution Prompts (with optional refinement)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  idea-generator \\
    --prompt-generator-file prompts/prompt_generators/prompt-generator-v1.md \\
    --refinement-prompt-file prompts/refine-concept.md \\
    --topic-generation-model unsloth-phi-4 \\
    --generator-llm-model google/gemma-3-27b \\
    --execution-llm-model qwen2.5-coder-7b-instruct-mlx \\
    --refinement-llm-model unsloth-phi-4 \\
    --api-endpoint http://localhost:1234/v1 \\
    --api-key lmstudio \\
    --output-directory tmp/multi_stage_outputs \\
    --verbose
    
  idea-generator \\
    --topic "How will AI affect the course of human civilization in 100 years?" \\
    --output-directory tmp/multi_stage_outputs
        """
    )
    
    parser.add_argument(
        '--prompt-generator-file', '-pgf',
        required=False,
        help='Path to the "Prompt Generator Prompt" file (defines JSON output format)'
    )
    
    parser.add_argument(
        '--refinement-prompt-file', '-rpf',
        required=False,
        help='Path to the refinement prompt file (for workflow extension)'
    )
    
    parser.add_argument(
        '--topic-generation-model', '-tgm',
        required=False,
        help='Name of the model to use for the Topic generation from the list of categories'
    )
    
    parser.add_argument(
        '--generator-llm-model', '-gm',
        required=False,
        help='Name of the model to use for the Prompt Generator step'
    )
    
    parser.add_argument(
        '--execution-llm-model', '-em',
        required=False,
        help='Name of the model to use for executing the final prompts'
    )

    parser.add_argument(
        '--refinement-llm-model', '-rm',
        required=False,
        help='Name of the model to use for the prompt refinement step'
    )
    
    parser.add_argument(
        '--api-endpoint', '-ae',
        default=None,
        help='OpenAI-compatible API endpoint URL'
    )
    
    parser.add_argument(
        '--api-key', '-ak',
        default="lmstudio",
        help='API key for authentication'
    )
    
    parser.add_argument(
        '--max-tokens', '-mt',
        type=int,
        default=20000,
        help='Maximum tokens in response for all LLM calls (Default: 20000)'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        type=float,
        default=None,
        help=f"Temperature for response generation for all LLM calls)"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--output-directory', '-o',
        required=True,
        help='Directory to save the final execution prompt outputs'
    )

    parser.add_argument(
        '--topic', '-to',
        required=False,
        default=None,
        help='Optional: A topic to generate ideas from. If provided, skips topic generation.'
    )

    parser.add_argument(
        '--topic-input-file', '-tif',
        required=False,
        default=None,
        help='Optional: Path to a file containing the topic for prompt generation. If provided, skips topic generation.'
    )
    
    parser.add_argument(
        '--idea-count', '-ic',
        required=False,
        help='Optional: The number of prompts to generate and process. The default count is 2.',
        default=1
    )

    return parser.parse_args()

def main():
    """Main execution function"""
    OutputPrinter.print_header("🚀 Idea Generator 🚀", Colors.BRIGHT_CYAN, 60)

    args = parse_arguments()

    config = Config(verbose=args.verbose)
    api_endpoint = args.api_endpoint or config.api_endpoint
    api_key = args.api_key or config.api_key
    topic_generation_model = args.topic_generation_model or config.default_model
    generator_llm_model = args.generator_llm_model or config.default_model
    execution_llm_model = args.execution_llm_model or config.default_model
    refinement_llm_model = args.refinement_llm_model or config.default_model
    temperature = args.temperature or config.default_model_temperature

    OutputPrinter.print_info("idea-count", args.idea_count)
    OutputPrinter.print_info("topic", args.topic)
    OutputPrinter.print_info("topic-input-file", args.topic_input_file)
    
    OutputPrinter.print_info("prompt-generator-file", args.prompt_generator_file)
    OutputPrinter.print_info("refinement-prompt-file", args.refinement_prompt_file)
    
    OutputPrinter.print_info("topic-generation-model", topic_generation_model)
    OutputPrinter.print_info("generator-llm-model", generator_llm_model)
    OutputPrinter.print_info("execution-llm-model", execution_llm_model)
    OutputPrinter.print_info("refinement-llm-model", refinement_llm_model)
    OutputPrinter.print_info("temperature", temperature)
    OutputPrinter.print_info("max-tokens", args.max_tokens)
    OutputPrinter.print_info("verbose", args.verbose)
    output_directory = FileHelper.generate_postfixed_sub_directory_name(args.output_directory)
    OutputPrinter.print_info("output-directory", output_directory)

    workflow = IdeaGenerationWorkflow(
        api_endpoint=api_endpoint,
        api_key=api_key,
        verbose=args.verbose,
        topic=args.topic,
        topic_input_file=args.topic_input_file,
        refinement_prompt_file=args.refinement_prompt_file,
        prompt_generator_file=args.prompt_generator_file,
        output_directory=args.output_directory,
        generator_llm_model=generator_llm_model,
        refinement_llm_model=refinement_llm_model,
        topic_generation_llm_model=topic_generation_model,
        execution_llm_model=execution_llm_model,
        idea_count=args.idea_count,
        max_tokens=args.max_tokens,
        temperature=temperature
    )
    workflow.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        OutputPrinter.print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)