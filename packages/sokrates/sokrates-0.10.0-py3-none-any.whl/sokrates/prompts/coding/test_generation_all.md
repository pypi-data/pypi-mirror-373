# Generated Test Code requirements

## A. Basic Functionality Tests
- Test normal operation with valid inputs
- Verify return values match expected behavior
- Test edge cases mentioned in docstrings

## B. Input Validation Tests
- Test with invalid/missing parameters (if applicable)
- Test boundary conditions and extreme values
- Test type validation for typed functions

## C. Error Handling Tests
- Test exception scenarios based on function logic
- Verify proper error messages are raised
- Test edge cases that should raise exceptions

## D. Edge Case Tests
- Test with None values where appropriate
- Test empty collections/lists/strings
- Test maximum and minimum valid values

## Test Structure Requirements

Each test file should follow this structure:
```python
import pytest
from {{module_name}} import *

# Test fixtures if needed (based on existing patterns)
@pytest.fixture
def sample_data():
    # Setup fixture data
    pass

# Test functions following naming convention: test_functionname_scenario
def test_my_func_normal_operation():
    """Test normal operation with valid inputs."""
    # Your implementation here

def test_my_func_edge_case_empty_input():
    """Test edge case with empty input."""
    # Your implementation here

# Additional test cases as needed...
```

## Mocking Strategy
If the function has external dependencies:
- Use `@patch` decorators for mocking
- Import necessary mock modules
- Verify interactions appropriately

## Parameterized Tests (when applicable)
For functions with multiple scenarios, use pytest.mark.parametrize:

Example:
```python
@pytest.mark.parametrize("input_param,expected_output", [
    (test_case_1_input, expected_result_1),
    (test_case_2_input, expected_result_2),
    # Add more test cases...
])
def test_my_func_parameterized(input_param, expected_output):
    """Test my_func with various inputs."""
    result = my_func(input_param)
    assert result == expected_output
```

## Assertions Guidelines
- Use specific assertions that verify the exact behavior
- Include descriptive assertion messages for debugging
- Test both positive and negative cases

## Edge Case Test Guidelines
Edge cases to test.

1. **Boundary Conditions**: Test minimum/maximum valid values
2. **Type Variations**: Test different input types and conversions  
3. **Special Values**: Test NaN, None, empty strings, etc.
4. **Resource Limits**: Test memory/performance constraints
5. **Error Scenarios**: Test expected failures for invalid inputs

Ensure each test includes:
- Clear docstring explaining the edge case being tested
- Specific assertions that verify the behavior
- Appropriate pytest markers where needed (e.g., @pytest.mark.slow)

Generated tests should be robust and cover scenarios that might cause bugs in production.

## Validation Test Guidelines
1. **Type Validation**: Test correct and incorrect data types for each parameter
2. **Value Range Testing**: Test numeric boundaries and constraints  
3. **Structure Validation**: Test collection and structured input requirements
4. **Business Rule Compliance**: Test domain-specific constraint violations
5. **Edge Case Values**: Test boundary conditions and unusual but valid values

For each test, include:
- Clear parameter value specifications
- Expected exception types and messages
- Parameterized tests where multiple scenarios apply
- Descriptive docstrings explaining the validation being tested
- Appropriate pytest.mark decorators for categorization

Generated tests should ensure robust input validation and provide clear feedback when invalid inputs are provided.

# Task
Based on the analysis above, generate a complete pytest-compatible test file for the provided code:

1. All necessary imports
2. Required fixtures (if any)
3. Comprehensive test functions covering:
   - Normal operation scenarios
   - Edge cases and boundary conditions
   - Error handling and exception testing
   - Parameterized tests where appropriate

Ensure the generated code follows pytest conventions, includes proper docstrings for each test function, and provides clear assertion messages.

# Output formatting
Output SOLELY the python code. Add all explanations inline as comments. DO NOT print additional information outside the code.


# Code to test
Filepath: `{{source_file_path}}`
```
{{source_file_content}}
```
