from datetime import datetime
import random

class Utils:
    """
    A utility class containing various helper functions for common operations.
    
    This class provides static methods for date/time formatting, random number generation,
    and other utility functions used throughout the application.
    """

    @staticmethod
    def current_date() -> str:
        """
        Gets the current date in YYYY-MM-DD format.

        Returns:
            str: The current date as a string in YYYY-MM-DD format.
        """
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def current_time() -> str:
        """
        Gets the current time in HH:MM:SS format.

        Returns:
            str: The current time as a string in HH:MM:SS format.
        """
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_current_datetime() -> str:
        """
        Gets the current date and time in YYYY-MM-DD HH:MM:SS format.

        Returns:
            str: The current date and time as a string in YYYY-MM-DD HH:MM:SS format.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def generate_random_int(min_value, max_value):
        """
        Generates a random integer between min_value and max_value (inclusive).

        Args:
            min_value: The minimum value (inclusive) for the random integer.
            max_value: The maximum value (inclusive) for the random integer.

        Returns:
            int: A random integer between min_value and max_value (inclusive).

        Raises:
            Exception: If min_value is greater than max_value.
        """
        if min_value > max_value:
          raise Exception("minimum must be below maximum")
        return random.randint(min_value, max_value)

    @staticmethod
    def generate_random_float(min_value: float, max_value: float) -> float:
        """
        Generates a random floating-point number between min_value and max_value (inclusive).

        Args:
            min_value (float): The minimum value (inclusive) for the random float.
            max_value (float): The maximum value (inclusive) for the random float.

        Returns:
            float: A random floating-point number between min_value and max_value (inclusive).

        Raises:
            Exception: If min_value is greater than max_value.
        """
        if min_value > max_value:
          raise Exception("minimum must be below maximum")
        return random.uniform(min_value, max_value)
