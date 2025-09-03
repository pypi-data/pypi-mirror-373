import pytest
from datetime import datetime
from unittest.mock import patch
import re

# Import Utils directly from sokrates package
from sokrates.utils import Utils

class TestUtils:
    def test_current_date_format(self):
        """Test that current_date returns date in YYYY-MM-DD format"""
        result = Utils.current_date()
        
        # Check that result is a string
        assert isinstance(result, str)
        
        # Check that it matches the expected format (YYYY-MM-DD)
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        assert re.match(date_pattern, result)
        
        # Verify it's a valid date by attempting to parse it
        try:
            datetime.strptime(result, "%Y-%m-%d")
        except ValueError:
            pytest.fail("Invalid date format returned")

    def test_current_time_format(self):
        """Test that current_time returns time in HH:MM:SS format"""
        result = Utils.current_time()
        
        # Check that result is a string
        assert isinstance(result, str)
        
        # Check that it matches the expected format (HH:MM:SS)
        time_pattern = r"^\d{2}:\d{2}:\d{2}$"
        assert re.match(time_pattern, result)
        
        # Verify it's a valid time by attempting to parse it
        try:
            datetime.strptime(result, "%H:%M:%S")
        except ValueError:
            pytest.fail("Invalid time format returned")

    def test_get_current_datetime_format(self):
        """Test that get_current_datetime returns datetime in YYYY-MM-DD HH:MM:SS format"""
        result = Utils.get_current_datetime()
        
        # Check that result is a string
        assert isinstance(result, str)
        
        # Check that it matches the expected format (YYYY-MM-DD HH:MM:SS)
        datetime_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        assert re.match(datetime_pattern, result)
        
        # Verify it's a valid datetime by attempting to parse it
        try:
            datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail("Invalid datetime format returned")

    def test_generate_random_int_valid_range(self):
        """Test that generate_random_int generates integers within the specified range"""
        min_val = 1
        max_val = 10
        
        # Generate multiple random numbers to ensure variety
        results = []
        for _ in range(10):
            result = Utils.generate_random_int(min_val, max_val)
            results.append(result)
            
            # Check that each result is within the valid range
            assert min_val <= result <= max_val
            assert isinstance(result, int)

    def test_generate_random_int_edge_cases(self):
        """Test generate_random_int with edge cases"""
        # Test same min and max values
        result = Utils.generate_random_int(5, 5)
        assert result == 5
        
        # Test negative numbers
        result = Utils.generate_random_int(-10, -1)
        assert -10 <= result <= -1
        assert isinstance(result, int)

    def test_generate_random_int_invalid_range(self):
        """Test that generate_random_int raises exception for invalid range"""
        with pytest.raises(Exception, match="minimum must be below maximum"):
            Utils.generate_random_int(10, 5)

    def test_generate_random_float_valid_range(self):
        """Test that generate_random_float generates floats within the specified range"""
        min_val = 1.0
        max_val = 10.0
        
        # Generate multiple random numbers to ensure variety
        results = []
        for _ in range(10):
            result = Utils.generate_random_float(min_val, max_val)
            results.append(result)
            
            # Check that each result is within the valid range
            assert min_val <= result <= max_val
            assert isinstance(result, float)

    def test_generate_random_float_edge_cases(self):
        """Test generate_random_float with edge cases"""
        # Test same min and max values
        result = Utils.generate_random_float(5.5, 5.5)
        assert result == 5.5
        
        # Test negative numbers
        result = Utils.generate_random_float(-10.5, -1.2)
        assert -10.5 <= result <= -1.2
        assert isinstance(result, float)

    def test_generate_random_float_invalid_range(self):
        """Test that generate_random_float raises exception for invalid range"""
        with pytest.raises(Exception, match="minimum must be below maximum"):
            Utils.generate_random_float(10.0, 5.0)

    @patch('sokrates.utils.datetime')
    def test_current_date_mocked(self, mock_datetime):
        """Test current_date with mocked datetime"""
        # Mock the datetime.now() to return a specific date
        mock_datetime.now.return_value = datetime(2023, 12, 25)
        mock_datetime.strptime = datetime.strptime
        
        result = Utils.current_date()
        assert result == "2023-12-25"

    @patch('sokrates.utils.datetime')
    def test_current_time_mocked(self, mock_datetime):
        """Test current_time with mocked datetime"""
        # Mock the datetime.now() to return a specific time
        mock_datetime.now.return_value = datetime(2023, 12, 25, 14, 30, 45)
        mock_datetime.strptime = datetime.strptime
        
        result = Utils.current_time()
        assert result == "14:30:45"

    @patch('sokrates.utils.datetime')
    def test_get_current_datetime_mocked(self, mock_datetime):
        """Test get_current_datetime with mocked datetime"""
        # Mock the datetime.now() to return a specific datetime
        mock_datetime.now.return_value = datetime(2023, 12, 25, 14, 30, 45)
        mock_datetime.strptime = datetime.strptime
        
        result = Utils.get_current_datetime()
        assert result == "2023-12-25 14:30:45"

    def test_consistency_of_datetime_functions(self):
        """Test that datetime functions are consistent with each other"""
        # Get all three values at roughly the same time
        date_part = Utils.current_date()
        time_part = Utils.current_time()
        
        # Format should be consistent with get_current_datetime
        full_datetime = Utils.get_current_datetime()
        date_and_time_parts = full_datetime.split(" ")
        
        assert date_part == date_and_time_parts[0]
        assert time_part == date_and_time_parts[1]

if __name__ == "__main__":
    pytest.main([__file__])
