#!/usr/bin/env python3
"""
Task Queue Error Handler Module

This module provides functionality for handling errors in the task queue system.
It implements retry mechanisms and dead letter queue management.

Classes:
    ErrorHandler: Manages error handling and recovery strategies
"""

import time
from sokrates.constants import Constants

class ErrorHandler:
    """
    Handles errors that occur during task processing.

    This class provides methods for implementing retry logic,
    managing the dead letter queue, and logging errors.

    Attributes:
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Base delay for exponential backoff
        dead_letter_enabled (bool): Whether dead letter queue is enabled

    Methods:
        should_retry(): Determine if a task should be retried
        get_retry_delay(): Calculate retry delay with exponential backoff
        log_error(): Log error details to history
    """

    def __init__(self):
        """
        Initializes the ErrorHandler with static config from Constants.
        """
        self.max_retries = Constants.DEFAULT_TASK_DAEMON_MAX_RETRIES
        self.base_delay = Constants.DEFAULT_TASK_DAEMON_BASE_RETRY_DELAY
        self.dead_letter_enabled = Constants.DEFAULT_TASK_DAEMON_DEAD_LETTER_QUEUE_ENABLED

    def should_retry(self, task, current_attempt):
        """
        Determine if a task should be retried based on retry count.

        Args:
            task (dict): Task information
            current_attempt (int): Current retry attempt number

        Returns:
            bool: True if task should be retried, False otherwise
        """
        return current_attempt <= self.max_retries

    def get_retry_delay(self, attempt):
        """
        Calculate retry delay using exponential backoff.

        Args:
            attempt (int): Current retry attempt number

        Returns:
            float: Delay in seconds
        """
        # Cap the delay to avoid excessive waiting
        return min(60.0, self.base_delay * (2 ** attempt))

    def log_error(self, task_id, error_message, attempt=1):
        """
        Log error details for a task.

        Args:
            task_id (str): Unique identifier for the task
            error_message (str): Error message to log
            attempt (int): Current retry attempt number

        Returns:
            dict: Error information for logging
        """
        return {
            "task_id": task_id,
            "attempt": attempt,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "error_message": error_message,
            "retryable": self.should_retry(None, attempt)
        }

    def handle_failure(self, manager, task_id, error_message, current_attempt=1):
        """
        Handle task failure by updating status and determining next steps.

        Args:
            manager: TaskQueueManager instance for database operations
            task_id (str): Unique identifier for the task
            error_message (str): Error message to log
            current_attempt (int): Current retry attempt number

        Returns:
            str: Next action ("retry", "dead_letter", or "fail")
        """
        if self.should_retry(None, current_attempt):
            # Update status to retrying and calculate delay
            manager.update_task_status(
                task_id,
                "retrying",
                error=error_message
            )
            return "retry"
        else:
            if self.dead_letter_enabled:
                # In a real implementation, we would move to dead letter queue
                manager.update_task_status(
                    task_id,
                    "failed",
                    error=f"Max retries reached: {error_message}"
                )
                return "dead_letter"
            else:
                manager.update_task_status(
                    task_id,
                    "failed",
                    error=error_message
                )
                return "fail"