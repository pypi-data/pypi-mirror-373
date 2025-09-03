"""
LLM Chat CLI - Command-line interface for interacting with large language models.

Main Purpose:
Provides a CLI for interacting with LLMs supporting model selection, 
temperature adjustment, context management, and conversation logging.

Parameters:
  --api-endpoint (-ae): LLM API endpoint (required if not in config)
  --api-key (-ak): API key for authentication (required if not in config)
  --model (-m): LLM model identifier (default: qwen3-4b-instruct-2507-mlx)
  --temperature (-t): Sampling temperature (0.0-1.0, default: 0.7)
  --max-tokens (-mt): Maximum response tokens (default: 6000)
  --verbose (-v): Enable verbose output
  --context-text (-ct): Additional context for LLM processing
  --context-files (-cf): Paths to files containing context
  --context-directories (-cd): Paths to directories with context files
  --output-file (-o): Path to log conversation history
  --hide-reasoning (-hr): Hide reasoning in responses

Usage Example:
  python llm_chat.py \\
    --model qwen3-4b-instruct-2507-mlx \\
    --temperature 0.8 \\
    --max-tokens 1024 \\
    --context-files ./context/prompt.md \\
    --output-file chat_log.txt
"""

import sys
import argparse

from sokrates.llm_api import LLMApi
from sokrates.config import Config
from sokrates.colors import Colors
from sokrates.file_helper import FileHelper
from sokrates.output_printer import OutputPrinter
from sokrates.prompt_refiner import PromptRefiner
import re
from datetime import datetime
from pathlib import Path
import asyncio # Import asyncio for running async functions

def main():
    """Main function to handle command line arguments and initiate LLM chat session."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='LLM Chat CLI - Interact with large language models through a command-line interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--api-endpoint", "-ae", 
                        default=None,
                        type=str, 
                        help="The API endpoint for the LLM.")
    parser.add_argument("--api-key", "-ak", 
                        default=None,
                        type=str, 
                        help="The API key for the LLM.")
    parser.add_argument("--model", "-m", 
                        default=None,
                        type=str, 
                        help="The model to use for the LLM.")
    parser.add_argument("--temperature", "-t", 
                        default=None, 
                        type=float, 
                        help="The temperature for the LLM.")
    parser.add_argument("--max-tokens", "-mt", 
                        default=6000, 
                        type=float, 
                        help="The maximum amount of tokens to generate for one answer.")
    parser.add_argument("--verbose", "-v", 
                        action='store_true', 
                        help="Enable verbose output.")
    parser.add_argument("--context-text", "-ct", 
                        default=None, 
                        type=str,
                        help="Additional context text for the LLM.")
    parser.add_argument("--context-files", "-cf", 
                        nargs='*', 
                        help="Paths to files containing additional context.")
    parser.add_argument("--context-directories", "-cd", 
                        nargs='*', 
                        help="Paths to directories containing additional context files.")
    parser.add_argument("--output-file", "-o", 
                        type=str, 
                        help="Path to a file to log the conversation.")
    parser.add_argument("--hide-reasoning", "-hr", 
                        action='store_true', 
                        help="Hide <tool_call> blocks from console output.")
    parser.add_argument("--voice", "-V", 
                        action='store_true', 
                        help="Enable voice chat mode.") # Add voice flag
    parser.add_argument("--whisper-model-language", "-wl", 
                        default="en",
                        type=str,
                        help="The language to use for whisper transcriptions (e.g. en, de) (Default: en).")
    
    # Parse arguments
    args = parser.parse_args()
    
    config = Config(verbose=args.verbose)
    
    api_endpoint = config.api_endpoint
    if args.api_endpoint:
        api_endpoint = args.api_endpoint
        
    api_key = config.api_key
    if args.api_key:
        api_key = args.api_key
        
    model = config.default_model
    if args.model:
        model = args.model
        
    OutputPrinter.print_info("You are chatting with the model:", model, Colors.BRIGHT_MAGENTA)
    
    temperature = config.default_model_temperature
    if args.temperature:
        temperature = args.temperature
    
    refiner = PromptRefiner(verbose=args.verbose)

    if not api_endpoint or not api_key or not model:
        OutputPrinter.print_error("API endpoint, API key, and model must be configured or provided.")
        sys.exit(1)
    
    llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
    conversation_history = []
    log_files = [] # Initialize as a list to hold all log file handles

    # Setup default log file
    home_dir = Path.home()
    default_chat_dir = home_dir / ".sokrates" / "chats"
    default_chat_dir.mkdir(parents=True, exist_ok=True) # Create directory if it doesn't exist

    timestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    default_log_file_path = default_chat_dir / FileHelper.clean_name(f"{timestamp}_{model}.md")

    try:
        default_log_file = open(default_log_file_path, "a")
        log_files.append(default_log_file)
        OutputPrinter.print_info("Conversation will be logged to default file:", str(default_log_file_path))
    except IOError as e:
        OutputPrinter.print_error(f"Could not open default log file {default_log_file_path}: {e}")
        sys.exit(1)

    # If --output-file is specified, open it as well
    if args.output_file:
        try:
            extra_log_file = open(args.output_file, "a")
            log_files.append(extra_log_file)
            OutputPrinter.print_info("Conversation will also be logged to:", args.output_file)
        except IOError as e:
            OutputPrinter.print_error(f"Could not open output file {args.output_file}: {e}")
            sys.exit(1)

    # Load context
    context_content = []
    if args.context_text:
        context_content.append(args.context_text)
    if args.context_files:
        try:
            context_content.extend(FileHelper.read_multiple_files(list(args.context_files), verbose=args.verbose))
        except Exception as e:
            OutputPrinter.print_error(f"Error reading context files: {e}")
            sys.exit(1)
    if args.context_directories:
        try:
            context_content.extend(FileHelper.read_multiple_files_from_directories(list(args.context_directories), verbose=args.verbose))
        except Exception as e:
            OutputPrinter.print_error(f"Error reading context directories: {e}")
            sys.exit(1)

    if context_content:
        full_context = "\n\n".join(context_content)
        conversation_history.append({"role": "system", "content": f"# This is the context for our conversation \n {full_context}"})
        if args.verbose:
            OutputPrinter.print_info("Loaded context", f"{full_context[:200]}...") # Show first 200 chars of context

    # Define a function for the chat loop to allow switching between modes
    async def chat_loop(voice_mode, whisper_model_language):
        """
        Main chat loop function that handles both text and voice interactions.
    
        Args:
            voice_mode (bool): Flag indicating whether to use voice chat mode
    
        Returns:
            None: This function runs an interactive loop and doesn't return a value
    
        Side Effects:
            - Modifies conversation_history with user and LLM messages
            - Writes conversation logs to all open log files
            - Handles mode switching between text and voice chat
            - Manages context addition during chat sessions
        """
        nonlocal conversation_history # Allow modification of conversation_history from outer scope
    
        while True:
            try:
                if voice_mode:
                    # import only when activated
                    from sokrates.voice_helper import run_voice_chat # Import the voice chat function
                    OutputPrinter.print_info("Starting voice chat. Press CTRL+C to exit.", "")
                    action = await run_voice_chat(llm_api, model, temperature, args.max_tokens, conversation_history, log_files, args.hide_reasoning, args.verbose, refiner, whisper_model_language=whisper_model_language)
                    if action == "toggle_voice":
                        voice_mode = not voice_mode
                        OutputPrinter.print_info(f"Switched to {'voice' if voice_mode else 'text'} mode.", "")
                        continue
                    elif isinstance(action, tuple) and action[0] == "add_context":
                        filepath = action[1]
                        try:
                            context_content = FileHelper.read_file(filepath)
                            conversation_history.append({"role": "system", "content": context_content})
                            OutputPrinter.print_info(f"Added context from {filepath}", "")
                        except Exception as e:
                            OutputPrinter.print_error(f"Error reading context file {filepath}: {e}")
                        continue
                    elif action == "exit":
                        break
                    elif action == "voice_disabled":
                        voice_mode = False
                        OutputPrinter.print_info(f"Switched to 'text' mode.", "")
                        continue
                else:
                    OutputPrinter.print_info("Starting text chat. Press CTRL+D or type 'exit' to quit.", "")
                    OutputPrinter.print_info("Commands: /add <Filepath>, /voice, or /talk", "")
                    user_input = input(f"{Colors.BLUE}You:{Colors.RESET} ")
                    if user_input.lower() == "exit":
                        break
                    elif user_input.lower() == "/voice":
                        voice_mode = not voice_mode
                        OutputPrinter.print_info(f"Switched to {'voice' if voice_mode else 'text'} mode.", "")
                        continue
                    elif user_input.lower() == "/talk":
                        # Import the handle_talk_command function
                        from sokrates.voice_helper import handle_talk_command
                        handle_talk_command(conversation_history, refiner)
                        continue
                    elif user_input.lower().startswith("/add "):
                        filepath = user_input[5:].strip()
                        try:
                            context_content = FileHelper.read_file(filepath)
                            conversation_history.append({"role": "system", "content": context_content})
                            OutputPrinter.print_info(f"Added context from {filepath}", "")
                        except Exception as e:
                            OutputPrinter.print_error(f"Error reading context file {filepath}: {e}")
                        continue
                    if not user_input:
                        continue

                    conversation_history.append({"role": "user", "content": user_input})

                    if args.verbose:
                        OutputPrinter.print_info("Sending request to LLM...", "")

                    response_content_full = llm_api.chat_completion(
                        messages=conversation_history,
                        model=model,
                        temperature=temperature,
                        max_tokens=args.max_tokens
                    )
                    
                    if response_content_full:
                        # Always log the full response to all open log files
                        for lf in log_files:
                            lf.write(f"User: {user_input}\n---\n")
                            lf.write(f"LLM: {response_content_full}\n---\n")
                            lf.flush()

                        display_content = response_content_full
                        
                        # Extract and colorize <tool_call> block for display if not hidden
                        think_match = re.search(r'<tool_call>(.*?)<tool_call>', display_content, re.DOTALL)
                        if think_match:
                            think_content = think_match.group(1)
                            colored_think_content = f"{Colors.DIM}<tool_call>{think_content}</tool_call>{Colors.RESET}"
                            display_content = display_content.replace(think_match.group(0), colored_think_content)

                        if args.hide_reasoning:
                            display_content = refiner.clean_response(display_content)
                            
                        OutputPrinter.print_info(f"{Colors.GREEN}LLM", f"{display_content}{Colors.RESET}")
                        conversation_history.append({"role": "assistant", "content": response_content_full})
                    else:
                        OutputPrinter.print_error("No response from LLM.")
                        for lf in log_files:
                            lf.write(f"User: {user_input}\n---\n")
                            lf.write("LLM: No response\n---\n")
                            lf.flush()

            except EOFError:
                OutputPrinter.print_info("\nExiting chat.", "")
                break
            except KeyboardInterrupt:
                OutputPrinter.print_info("\nExiting chat.", "")
                break
            except Exception as e:
                    OutputPrinter.print_error(f"An error occurred: {e}")
                    for lf in log_files:
                        lf.write(f"Error: {e}\n")
                        lf.flush()
        
        # Close all open log files
        for lf in log_files:
            lf.close()

    asyncio.run(chat_loop(args.voice, whisper_model_language=args.whisper_model_language))

if __name__ == "__main__":
    main()