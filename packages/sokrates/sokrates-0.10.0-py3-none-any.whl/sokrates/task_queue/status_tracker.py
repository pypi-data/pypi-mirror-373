#!/usr/bin/env python3
"""
Task Status Tracker Module

This module provides functionality for tracking task execution status.
It handles status updates and maintains the current state of tasks.

Classes:
    StatusTracker: Manages task status tracking and reporting
"""

class StatusTracker:
    """
    Tracks the status of tasks in the queue system.

    This class provides methods for updating task status,
    retrieving current status, and managing status transitions.

    Attributes:
        None (state is managed through TaskQueueManager)

    Methods:
        update_status(): Update task status with optional result/error
        get_status(): Get current status of a task
    """

    def __init__(self, manager):
        """
        Initializes the StatusTracker with reference to TaskQueueManager.

        Args:
            manager: TaskQueueManager instance for database operations
        """
        self.manager = manager

    def update_status(self, task_id, status, result=None, error=None):
        """
        Update the status of a task.

        Args:
            task_id (str): Unique identifier for the task
            status (str): New status for the task
            result (str, optional): Execution result if completed
            error (str, optional): Error message if failed

        Raises:
            Exception: If database operation fails
        """
        try:
            self.manager.update_task_status(task_id, status, result, error)
        except Exception as e:
            raise Exception(f"Failed to update task status: {e}")

    def get_status(self, task_id):
        """
        Get the current status of a task.

        Args:
            task_id (str): Unique identifier for the task

        Returns:
            dict: Task information including status
        """
        try:
            # In a real implementation, we would query the database directly
            tasks = self.manager.get_all_tasks()
            return next((t for t in tasks if t['task_id'] == task_id), None)
        except Exception as e:
            raise Exception(f"Failed to retrieve task status: {e}")
