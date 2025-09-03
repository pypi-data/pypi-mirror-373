#!/usr/bin/env python3
"""
Task Queue Manager Module

This module provides the main interface for managing the task queue system.
It handles adding tasks, retrieving pending tasks, and updating task status.

Classes:
    TaskQueueManager: Manages task queue operations with database integration
"""

import uuid
from typing import List, Dict, Optional
from .database import TaskQueueDatabase
from sokrates.file_helper import FileHelper
from sokrates.config import Config

class TaskQueueManager:
    """
    Manages the task queue system by coordinating database operations and task management.

    This class provides a high-level interface for adding tasks to the queue,
    retrieving pending tasks for processing, and updating task status. It serves as
    the main entry point for task queue operations in the application.

    Attributes:
        db: TaskQueueDatabase instance for database operations

    Methods:
        add_task_from_file(): Add a new task from JSON file to the queue
        get_all_tasks(): Get all tasks
        get_pending_tasks(): Get pending tasks for processing
        update_task_status(): Update task status with optional result/error
        remove_task(): Remove a task from the queue
    """

    def __init__(self, config: Config):
        """
        Initializes the TaskQueueManager with database configuration.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                If None, uses the default from TaskQueueDatabase.
        """
        self.config = config
        self.db = TaskQueueDatabase(self.config.database_path)

    def add_task_from_file(self, task_file_path: str,
                          priority: str = "normal") -> str:
        """
        Add a new task from JSON file to the queue.

        Args:
            task_file_path (str): Path to the JSON file containing task definition
            priority (str, optional): Task priority level. Defaults to "normal".

        Returns:
            str: The generated task ID

        Raises:
            ValueError: If task file cannot be loaded or parsed
            Exception: If database operation fails
        """
        try:
            # Read and parse the task file
            task_data = FileHelper.read_json_file(task_file_path)

            # Generate a unique task ID
            task_id = str(uuid.uuid4())

            # Extract description from task data
            description = task_data.get("description", "Task from JSON file")

            # Add task to database
            self.db.add_task(
                task_id=task_id,
                description=description,
                file_path=task_file_path,
                priority=priority
            )

            return task_id

        except Exception as e:
            raise ValueError(f"Failed to add task from {task_file_path}: {e}")

    def get_all_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all tasks for processing.

        Args:
            limit (int, optional): Maximum number of tasks to return. If None, returns all.

        Returns:
            List[Dict]: List of task dictionaries
        """
        try:
            return self.db.get_all_tasks(limit)
        except Exception as e:
            raise Exception(f"Failed to retrieve all tasks: {e}")

    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get pending tasks for processing.

        Args:
            limit (int, optional): Maximum number of tasks to return. If None, returns all.

        Returns:
            List[Dict]: List of task dictionaries with pending status
        """
        print("############## GET PENDING TASKS")
        try:
            return self.db.get_pending_tasks(limit)
        except Exception as e:
            print(f"Error retrieving pending tasks: {e}")
            raise Exception(f"Failed to retrieve pending tasks: {e}")

    def update_task_status(self, task_id: str, status: str,
                          result: Optional[str] = None, error: Optional[str] = None) -> None:
        """
        Update task status with optional result/error.

        Args:
            task_id (str): Unique identifier for the task
            status (str): New status for the task
            result (str, optional): Execution result if completed
            error (str, optional): Error message if failed

        Raises:
            Exception: If database operation fails
        """
        try:
            self.db.update_task_status(task_id, status, result, error)
        except Exception as e:
            raise Exception(f"Failed to update task status for {task_id}: {e}")

    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the queue.

        Args:
            task_id (str): Unique identifier for the task to remove

        Raises:
            Exception: If database operation fails
        """
        try:
            with self.db.conn:
                self.db.conn.execute(
                    "DELETE FROM tasks WHERE task_id = ?",
                    (task_id,)
                )
        except Exception as e:
            raise Exception(f"Failed to remove task {task_id}: {e}")

    def close(self):
        """
        Closes the underlying database connection.

        This method ensures that all database resources are properly closed
        and released. It should be called when the TaskQueueManager is no longer needed.
        
        Returns:
            None
        """
        self.db.close()

    def __enter__(self):
        """Support context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol"""
        self.close()
