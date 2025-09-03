#!/usr/bin/env python3
"""
CLI Interface for Checking Task Status

This script provides a command-line interface for checking the status of tasks in the task queue system.
It uses the TaskQueueManager class to retrieve detailed task information.

Usage:
    python queue_status.py <task_id> [options]

Options:
    --verbose, -v: Show full execution details and logs

Example:
    python queue_status.py task-123 --verbose
"""

import argparse
import sys
from sokrates.task_queue.manager import TaskQueueManager
from sokrates.colors import Colors
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config

def main():
    """
    Main function to check task status.

    Sets up argument parsing, retrieves task information,
    and displays detailed status.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Provides comprehensive information about a single task.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'task_id',
        help='The ID of the task to check'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show full execution details and logs'
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)

    if args.verbose:
        print(f"{Colors.BRIGHT_BLUE}Retrieving status for task {args.task_id}...{Colors.RESET}")

    try:
        # Initialize TaskQueueManager
        manager = TaskQueueManager(config=config)

        # Get all tasks to find the specific one (we'll implement direct lookup later)
        all_tasks = manager.get_all_tasks()
        task = next((t for t in all_tasks if t['task_id'] == args.task_id), None)

        if not task:
            OutputPrinter.print_error(f"Task {args.task_id} not found")
            sys.exit(1)

        # Display task status
        OutputPrinter.print_section(f"TASK STATUS: {args.task_id}", Colors.BRIGHT_BLUE, "=")

        status_color = {
            'pending': Colors.YELLOW,
            'in_progress': Colors.BLUE,
            'completed': Colors.GREEN,
            'failed': Colors.RED
        }.get(task['status'], Colors.WHITE)

        print(f"{Colors.BRIGHT_WHITE}Status:{Colors.RESET} {status_color}{task['status'].upper()}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Priority:{Colors.RESET} {Colors.CYAN}{task['priority'].upper()}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Description:{Colors.RESET} {task['description']}")
        print(f"{Colors.BRIGHT_WHITE}File Path:{Colors.RESET} {task['file_path']}")
        print(f"{Colors.BRIGHT_WHITE}Created:{Colors.RESET} {task['created_at']}")
        print(f"{Colors.BRIGHT_WHITE}Updated:{Colors.RESET} {task['updated_at']}")

        if task['status'] == 'completed':
            print(f"{Colors.GREEN}Result:{Colors.RESET} {task.get('result', 'No result available')}")
        elif task['status'] == 'failed':
            print(f"{Colors.RED}Error:{Colors.RESET} {task.get('error_message', 'No error details available')}")

        if args.verbose:
            # In a real implementation, we would show more detailed logs here
            print(f"\n{Colors.BRIGHT_BLUE}Execution Details:{Colors.RESET}")
            print("This is where detailed execution logs would appear...")

    except Exception as e:
        OutputPrinter.print_error(f"Error checking task status: {str(e)}")
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