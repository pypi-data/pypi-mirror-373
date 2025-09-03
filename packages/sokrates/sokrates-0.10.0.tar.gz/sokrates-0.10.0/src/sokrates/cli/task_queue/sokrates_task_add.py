#!/usr/bin/env python3
"""
CLI Interface for Adding Tasks to Queue

This script provides a command-line interface for adding tasks to the task queue system.
It uses the TaskQueueManager class to add tasks from JSON files.

Usage:
    python queue_add.py --task-file <file_path> [options]

Options:
    --task-file, -tf: Path to the JSON file containing the task definition
    --priority, -p: Set task priority (values: high, normal, low)
    --verbose, -v: Enable verbose output with debug information

Example:
    python queue_add.py --task-file tasks/new_task.json --priority high --verbose
"""

import argparse
import sys
from sokrates.task_queue.manager import TaskQueueManager
from sokrates.colors import Colors
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config

def main():
    """
    Main function to add a task from JSON file to the queue.

    Sets up argument parsing, validates input, and coordinates task addition.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Adds a task from a JSON file to the processing queue.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--task-file', '-tf',
        required=True,
        help='Path to the JSON file containing tasks'
    )

    parser.add_argument(
        '--priority', '-p',
        choices=['high', 'normal', 'low'],
        default='normal',
        help='Priority level for the task (default: normal)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)

    if args.verbose:
        print(f"{Colors.BRIGHT_BLUE}Starting task addition process...{Colors.RESET}")

    try:
        # Initialize TaskQueueManager
        manager = TaskQueueManager(config=config)

        # Add task to queue
        task_id = manager.add_task_from_file(
            task_file_path=args.task_file,
            priority=args.priority
        )

        OutputPrinter.print_success(f"Task added successfully with ID: {task_id}")
        if args.verbose:
            print(f"{Colors.GREEN}Task details:{Colors.RESET}")
            print(f"- File: {args.task_file}")
            print(f"- Priority: {args.priority}")

    except Exception as e:
        OutputPrinter.print_error(f"Error adding task: {str(e)}")
        sys.exit(1)

    finally:
        manager.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)