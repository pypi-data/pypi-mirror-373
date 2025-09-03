#!/usr/bin/env python3
"""
Task Queue Daemon CLI Interface

This module provides command-line tools for managing the task queue daemon.
"""

import os
import sys
import signal
import time
import subprocess
import argparse
from sokrates.task_queue.daemon import TaskQueueDaemon
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config

DAEMON_PROCESS_NAMES=[
    "sokrates-daemon",
    "sokrates_daemon"
]

CONFIG = Config()

def start_daemon():
    """Start the task queue daemon."""
    
    # check for already running daemons
    OutputPrinter.print("Checking for running daemon processes...")
    pid = find_daemon_pid()
    if pid != None:
        OutputPrinter.print(f"Daemon is already started with PID: {pid} .")
        OutputPrinter.print(f"Exiting gracefully.")
        sys.exit(0)
    OutputPrinter.print("No running daemon process found.")
    
    OutputPrinter.print("Starting task queue daemon...")

    # Create a new daemon instance and run it in a separate process
    pid = os.fork()

    if pid == 0:
        # Child process - run the daemon with redirected output
        try:
            # Redirect stdout and stderr to log file
            sys.stdout = open(CONFIG.daemon_logfile_path, 'a')
            sys.stderr = open(CONFIG.daemon_logfile_path, 'a')

            # Also redirect logging to the same file (it's already set up in TaskQueueDaemon)
            daemon = TaskQueueDaemon(config=CONFIG)
            daemon.run()

            # Close log files on exit
            sys.stdout.close()
            sys.stderr.close()
        except Exception as e:
            # If we can't open log file, print to original stderr
            OutputPrinter.print(f"Error starting daemon: {e}")
            print(f"Error starting daemon: {e}", file=sys.__stderr__)
            sys.exit(1)
    else:
        # Parent process - return PID to user
        OutputPrinter.print(f"Task queue daemon started with PID: {pid}")
        return pid

def restart_daemon():
    stop_daemon()
    start_daemon()

def stop_daemon(pid=None):
    """Stop the task queue daemon."""
    if pid is None:
        print("No PID specified. Trying to find running daemon...")
        try:
            # Try to find the daemon process
            pid = find_daemon_pid()
            if not pid:
                OutputPrinter.print_error("No running daemon found.")
                return False

            OutputPrinter.print(f"Stopping task queue daemon (PID: {pid})...")
        except Exception as e:
            OutputPrinter.print_error(f"Error finding daemon PID: {e}")
            return False
    else:
        print(f"Stopping task queue daemon (PID: {pid})...")

    try:
        # Send termination signal
        os.kill(pid, signal.SIGTERM)

        # Wait for process to terminate
        start_time = time.time()
        while True:
            try:
                os.kill(pid, 0)  # Check if process exists
            except OSError:
                break  # Process terminated

            if time.time() - start_time > 10:  # 10 second timeout
                OutputPrinter.print("Timeout waiting for daemon to stop. Sending SIGKILL...")
                os.kill(pid, signal.SIGKILL)
                break

            time.sleep(0.1)

        OutputPrinter.print(f"Task queue daemon stopped (PID: {pid})")
        return True
    except Exception as e:
        OutputPrinter.print(f"Error stopping daemon: {e}")
        return False

def _search_for_pid_by_process_names(process_names:list) -> int:
    for process_name in process_names:
        result = subprocess.run(
            ['pgrep', '-f', process_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode == 0:
            pids = result.stdout.decode().strip().split('\n')
            # Filter out empty lines and return the first valid PID
            for pid in pids:
                if pid.isdigit():
                    return int(pid)
    return None

def find_daemon_pid():
    """Find the PID of a running task queue daemon."""
    try:
        # Look for python processes with our daemon module in the command line
        return _search_for_pid_by_process_names(DAEMON_PROCESS_NAMES)
    except Exception as e:
        print(f"Error finding daemon PID: {e}")
        return None

def check_status():
    """Check if the daemon is running."""
    pid = find_daemon_pid()
    if pid:
        OutputPrinter.print(f"Task queue daemon is running (PID: {pid})")
        return True
    else:
        OutputPrinter.print("Task queue daemon is not running")
        return False

def main():
    """Main CLI entry point for sokrates daemon CLI."""
    
    parser = argparse.ArgumentParser(description='Manage the task queue daemon')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start the task queue daemon')
    start_parser.set_defaults(func=lambda args: start_daemon())

    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the task queue daemon')
    stop_parser.add_argument('--pid', type=int, help='PID of the daemon to stop')

    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart the task queue daemon')
    restart_parser.set_defaults(func=lambda args: restart_daemon())
    
    def stop_func(args):
        return stop_daemon(args.pid)

    stop_parser.set_defaults(func=stop_func)

    # Status command
    status_parser = subparsers.add_parser('status', help='Check daemon status')
    status_parser.set_defaults(func=lambda args: check_status())

    args = parser.parse_args()

    try:
        if 'func' in args:
            success = args.func(args)
            sys.exit(0 if success else 1)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        OutputPrinter.print_error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()