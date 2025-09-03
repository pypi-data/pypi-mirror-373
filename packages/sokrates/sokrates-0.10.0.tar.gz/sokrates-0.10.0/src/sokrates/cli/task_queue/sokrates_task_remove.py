#!/usr/bin/env python3
"""
CLI Interface for Removing Tasks from Queue

This script provides a command-line interface for removing tasks from the task queue system.
It uses the TaskQueueManager class to delete tasks from the queue.

Usage:
    python queue_remove.py <task_id> [options]

Options:
    --force, -f: Bypass confirmation prompt
    --verbose, -v: Show removal details

Example:
    python queue_remove.py task-123 --force --verbose
"""

import argparse
import sys
from sokrates.task_queue.manager import TaskQueueManager
from sokrates.colors import Colors
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config

def main():
    """
    Main function to remove a task from the queue.

    Sets up argument parsing, handles confirmation,
    and coordinates task removal.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Deletes a task from the queue before it\'s processed.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'task_id',
        help='The ID of the task to remove'
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Bypass confirmation prompt'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show removal details'
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)

    if args.verbose:
        print(f"{Colors.BRIGHT_BLUE}Preparing to remove task {args.task_id}...{Colors.RESET}")

    try:
        # Initialize TaskQueueManager
        manager = TaskQueueManager(config=config)

        # Check if task exists first
        all_tasks = manager.get_all_tasks()
        task = next((t for t in all_tasks if t['task_id'] == args.task_id), None)

        if not task:
            OutputPrinter.print_error(f"Task {args.task_id} not found")
            sys.exit(1)

        # Confirm removal
        if not args.force:
            confirmation = input(f"{Colors.YELLOW}Are you sure you want to remove task {args.task_id}? [y/N]: {Colors.RESET}")
            if confirmation.lower() != 'y':
                OutputPrinter.print_info("Task removal cancelled")
                sys.exit(0)

        # Remove task
        manager.remove_task(args.task_id)
        OutputPrinter.print_success(f"Task {args.task_id} removed successfully")

        if args.verbose:
            print(f"{Colors.GREEN}Details:{Colors.RESET}")
            print(f"- Task ID: {task['task_id']}")
            print(f"- Description: {task['description']}")
            print(f"- Status was: {task['status']}")

    except Exception as e:
        OutputPrinter.print_error(f"Error removing task: {str(e)}")
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