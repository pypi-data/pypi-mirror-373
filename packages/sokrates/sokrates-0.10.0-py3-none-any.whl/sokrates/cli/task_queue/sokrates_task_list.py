#!/usr/bin/env python3
"""
CLI Interface for Listing Queued Tasks

This script provides a command-line interface for listing tasks in the task queue system.
It uses the TaskQueueManager class to retrieve and display task information.

Usage:
    python queue_list.py [options]

Options:
    --status, -s: Filter by status (values: pending, in_progress, completed, failed)
    --priority, -p: Filter by priority (values: high, normal, low)
    --verbose, -v: Show detailed task information

Example:
    python queue_list.py --status pending --priority high --verbose
"""

import argparse
import sys
from sokrates.task_queue.manager import TaskQueueManager
from sokrates.colors import Colors
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config

def main():
    """
    Main function to list queued tasks.

    Sets up argument parsing, retrieves tasks from the queue,
    and displays them in a user-friendly format.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Lists all tasks currently in the queue with their status.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--status', '-s',
        choices=['pending', 'in_progress', 'completed', 'failed'],
        help='Filter tasks by status'
    )

    parser.add_argument(
        '--priority', '-p',
        choices=['high', 'normal', 'low'],
        help='Filter tasks by priority'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed task information'
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)

    if args.verbose:
        print(f"{Colors.BRIGHT_BLUE}Retrieving tasks from queue...{Colors.RESET}")

    try:
        # Initialize TaskQueueManager
        manager = TaskQueueManager(config=config)

        # Build query parameters based on filters
        query_params = {}
        if args.status:
            query_params['status'] = args.status
        if args.priority:
            query_params['priority'] = args.priority

        # Get tasks from queue (for now, get all - we'll implement filtering in the manager later)
        tasks = manager.get_all_tasks()

        # Filter tasks based on arguments
        filtered_tasks = tasks
        if args.status and args.status != 'all':
            filtered_tasks = [t for t in tasks if t['status'] == args.status]
        if args.priority and args.priority != 'all':
            filtered_tasks = [t for t in tasks if t['priority'] == args.priority]

        # Display tasks
        OutputPrinter.print_section("QUEUED TASKS", Colors.BRIGHT_BLUE, "=")

        if not filtered_tasks:
            print(f"{Colors.YELLOW}No tasks found matching the criteria.{Colors.RESET}")
        else:
            for task in filtered_tasks:
                status_color = {
                    'pending': Colors.YELLOW,
                    'in_progress': Colors.BLUE,
                    'completed': Colors.GREEN,
                    'failed': Colors.RED
                }.get(task['status'], Colors.WHITE)

                print(f"{Colors.BRIGHT_WHITE}{task['task_id']}{Colors.RESET} | "
                      f"{status_color}{task['status'].upper()}{Colors.RESET} | "
                      f"{Colors.CYAN}{task['priority'].upper()}{Colors.RESET} | "
                      f"{Colors.GREEN}{task['description'][:50]}{'...' if len(task['description']) > 50 else ''}{Colors.RESET}")

                if args.verbose:
                    print(f"    {Colors.BRIGHT_BLUE}File:{Colors.RESET} {task['file_path']}")
                    print(f"    {Colors.BRIGHT_BLUE}Created:{Colors.RESET} {task['created_at']}")
                    print(f"    {Colors.BRIGHT_BLUE}Updated:{Colors.RESET} {task['updated_at']}")

        OutputPrinter.print(f"Total tasks: {len(filtered_tasks)}")

    except Exception as e:
        OutputPrinter.print_error(f"Error listing tasks: {str(e)}")
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