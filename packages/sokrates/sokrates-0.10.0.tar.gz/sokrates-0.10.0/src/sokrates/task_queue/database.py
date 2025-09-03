#!/usr/bin/env python3
"""
Task Queue Database Module

This module provides database access functionality for the task queue system.
It handles SQLite database operations including task management, status tracking,
and history logging.

Classes:
    TaskQueueDatabase: Manages database connections and CRUD operations for tasks
"""

import sqlite3
import time
from typing import List, Dict, Optional

class TaskQueueDatabase:
    """
    Manages the SQLite database for task queue storage and retrieval.

    This class provides methods for adding tasks to the queue, retrieving 
    tasks, updating task status, and logging history changes. It ensures data
    integrity through transaction management and proper error handling.

    Attributes:
        db_path (str): Path to the SQLite database file
        conn: Database connection object

    Methods:
        _connect(): Establish database connection with retry logic
        add_task(): Add a new task to the queue
        get_all_tasks(): Get all tasks from the db
        get_pending_tasks(): Get pending tasks for processing
        
        update_task_status(): Update task status with optional result/error
        close(): Close the database connection
    """

    def __init__(self, db_path: str):
        """
        Initializes the TaskQueueDatabase with configuration and database setup.

        Args:
            db_path (str): Path to the SQLite database file.

        Side Effects:
            - Creates database tables if they don't exist
            - Establishes initial database connection
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._initialize_tables()

    def connection(self):
        """
        Get a database connection, establishing one if needed.

        Returns:
            sqlite3.Connection: A database connection object.
        """
        if not self.conn:
            self._connect()
        return self.conn
    
    def _connect(self):
        """
        Establishes a connection to the SQLite database with retry logic.

        This method attempts to connect to the SQLite database up to 3 times,
        with increasing delays between retries in case of connection failures.

        Returns:
            None

        Raises:
            Exception: If all retry attempts fail to establish a database connection.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                self.conn.execute("PRAGMA journal_mode=WAL")
                return
            except sqlite3.Error as e:
                if attempt == max_retries - 1:
                    print(f"Failed to connect to database: {e}")
                    raise Exception(f"Failed to connect to database: {e}")
                time.sleep(0.1 * (attempt + 1))

    def _initialize_tables(self):
        """
        Initializes the database tables if they don't already exist.

        This method creates two tables in the SQLite database:
        1. 'tasks' table for storing task information
        2. 'task_history' table for logging status changes

        Returns:
            None
        """
        with self.connection():
            # Create tasks table
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                file_path TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result TEXT, -- for completed tasks
                error_message TEXT -- for failed tasks
            )
            """)

            # Create task history table
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result TEXT,
                error_message TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
            """)

    def add_task(self, task_id: str, description: str, file_path: str,
                 priority: str = "normal") -> None:
        """Add a new task to the queue"""
        try:
            with self.connection():
                self.conn.execute(
                    """
                    INSERT INTO tasks (task_id, description, file_path, priority)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, description, file_path, priority)
                )
        except sqlite3.IntegrityError as e:
            print(f"Error: Task already exists: {e}")
            raise ValueError(f"Task already exists: {e}")

    def _execute_select_query(self, query, params: list=None, limit: Optional[int] = None):
        """
        Executes a SELECT query and returns the results as a list of dictionaries.

        Args:
            query (str): The SQL SELECT query to execute.
            params (list, optional): Parameters for the SQL query. Defaults to None.
            limit (int, optional): Maximum number of results to return. Defaults to None.

        Returns:
            list[Dict]: A list of dictionaries representing the query results.
        """
        if params is None:
            params = []

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self.connection():
            cursor = self.conn.execute(query, params)
            tasks = [self._row_to_dict(row) for row in cursor.fetchall()]
            return tasks

    def get_all_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all tasks"""
        # query = "SELECT * FROM tasks WHERE status = 'pending'"
        query = "SELECT * FROM tasks"
        return self._execute_select_query(query, limit=limit)

    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """Get pending tasks for processing"""
        query = "SELECT * FROM tasks WHERE status = 'pending'"
        return self._execute_select_query(query, limit=limit)

    def update_task_status(self, task_id: str, status: str,
                          result: Optional[str] = None, error: Optional[str] = None) -> None:
        """Update task status with optional result/error"""
        try:
            with self.connection():
                query = """
                UPDATE tasks
                SET status = ?,
                    result = ?,
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
                """

                self.conn.execute(query, (status, result or None, error or None, task_id))

                # Also log to history table
                self._log_task_history(task_id, status, result, error)
        except sqlite3.Error as e:
            print(f"An Error occured during updating the task status: {e}")
            raise Exception(f"Failed to update task status: {e}")

    def _log_task_history(self, task_id: str, status: str,
                          result: Optional[str] = None, error: Optional[str] = None) -> None:
        """Log status change to history table"""
        try:
            with self.connection():
                self.conn.execute(
                    """
                    INSERT INTO task_history (task_id, status, result, error_message)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, status, result, error)
                )
        except sqlite3.Error as e:
            # Don't fail the main operation if history logging fails
            print(f"Warning: Failed to log history for {task_id}: {e}")

    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        return dict(row)

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Support context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol"""
        self.close()
