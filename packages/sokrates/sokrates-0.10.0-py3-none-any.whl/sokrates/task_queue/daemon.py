#!/usr/bin/env python3
"""
Task Queue Daemon Module with Status Tracking

This module provides a background daemon process for processing tasks
from the task queue using TaskProcessor, with comprehensive status tracking.
"""

import signal
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from sokrates.task_queue.processor import TaskProcessor
from sokrates.config import Config
class TaskQueueDaemon:
    """
    Background daemon for processing tasks from the task queue.

    Attributes:
        processor: TaskProcessor instance for task execution
        processing_interval: Time between processing cycles in seconds
        running: Flag indicating if daemon is running
    """

    def __init__(self, config: Config):
        """
        Initialize the TaskQueueDaemon with configuration and set up components.

        This constructor configures the daemon's processing interval, initializes
        logging, and sets up the TaskProcessor for task execution.

        Args:
            config (Config): Config object for configuration loading attributes from
        """
        self.config = config
        self.processing_interval = self.config.daemon_processing_interval
        self.daemon_logfile_path = self.config.daemon_logfile_path
        self.running = False

        # Set up logging
        self.setup_logger()
        self.processor = TaskProcessor(config=self.config)

    def setup_logger(self):
        """Configure logging for the daemon."""
        log_file = self.daemon_logfile_path
        logger = logging.getLogger('TaskQueueDaemon')
        logger.setLevel(logging.INFO)

        # Create rotating file handler
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.logger = logger

    def process_cycle(self):
        """Process a single cycle of tasks using TaskProcessor."""
        try:
            self.logger.info(f"Starting processing cycle (processing_interval: {self.processing_interval}s)")
            
            self.processor.process_tasks()
            self.logger.info("Processing cycle completed")
        except Exception as e:
            self.logger.error(f"Error during processing cycle: {e}")

    def run(self):
        """Run the daemon main loop."""
        self.running = True
        self.logger.info("Task Queue Daemon started")

        try:
            while self.running:
                self.process_cycle()
                time.sleep(self.processing_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        """Clean up resources and shut down gracefully."""
        if not self.running:
            return

        self.logger.info("Shutting down Task Queue Daemon...")
        try:
            # Update any in_progress tasks to failed on shutdown
            all_tasks = self.processor.manager.get_all_tasks()
            for task in all_tasks:
                if task['status'] == 'in_progress':
                    task_id = task['task_id']
                    error_msg = "Daemon terminated during processing"
                    self.processor.status_tracker.update_status(
                        task_id, "failed", error=error_msg
                    )
                    self.logger.warning(f"Task {task_id} status updated to failed: {error_msg}")

            self.processor.manager.close()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            self.running = False
            self.logger.info("Daemon shut down complete")
            
    def restart(self):
        """Restart the Task Queue Daemon process.

        This method shuts down the current daemon instance and starts a new one.
        It's useful for applying configuration changes or recovering from errors.

        Returns:
            None
        """
        self.logger.info("Restarting Task Queue Daemon...")
        self.shutdown()
        self.run()

    def handle_signal(self, signum, frame):
        """Handle termination signals."""
        self.logger.info(f"Received signal {signum}. Shutting down...")
        self.shutdown()
