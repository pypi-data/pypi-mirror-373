# Test Generation Base Template

You are an expert Python test writer specializing in pytest-style unit tests. Your task is to generate comprehensive, well-structured test cases for the provided Python code based on the function signatures, docstrings, and analysis results.

## Code Analysis Context
{{source_file_analysis}}

## Existing Tests Context (if any)
{{existing_tests_context}}

## Test Generation Guidelines

### 1. Function Signature Analysis
Based on the function signature:
- **Function name**: {{function_name}}
- **Parameters**: {{parameters_list}}
- **Return type**: {{return_type}}
- **Complexity metrics**: {{complexity_info}}

### 2. Expected Behavior from Docstring
{{docstring_analysis}}

### 3. Test Case Categories to Generate

#### A. Basic Functionality Tests
- Test normal operation with valid inputs
- Verify return values match expected behavior
- Test edge cases mentioned in docstrings

#### B. Input Validation Tests
- Test with invalid/missing parameters (if applicable)
- Test boundary conditions and extreme values
- Test type validation for typed functions

#### C. Error Handling Tests
- Test exception scenarios based on function logic
- Verify proper error messages are raised
- Test edge cases that should raise exceptions

#### D. Edge Case Tests
- Test with None values where appropriate
- Test empty collections/lists/strings
- Test maximum and minimum valid values

### 4. Test Structure Requirements

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
def test_{{function_name}}_normal_operation():
    """Test normal operation with valid inputs."""
    # Your implementation here

def test_{{function_name}}_edge_case_empty_input():
    """Test edge case with empty input."""
    # Your implementation here

# Additional test cases as needed...
```

### 5. Mocking Strategy
If the function has external dependencies:
- Use `@patch` decorators for mocking
- Import necessary mock modules
- Verify interactions appropriately

### 6. Parameterized Tests (when applicable)
For functions with multiple scenarios, use pytest.mark.parametrize:

```python
@pytest.mark.parametrize("input_param,expected_output", [
    (test_case_1_input, expected_result_1),
    (test_case_2_input, expected_result_2),
    # Add more test cases...
])
def test_{{function_name}}_parameterized(input_param, expected_output):
    """Test {{function_name}} with various inputs."""
    result = {{function_name}}(input_param)
    assert result == expected_output
```

### 7. Assertions Guidelines
- Use specific assertions that verify the exact behavior
- Include descriptive assertion messages for debugging
- Test both positive and negative cases

## Generate Complete Test File

Based on the analysis above, generate a complete pytest-compatible test file for {{function_name}} that includes:

1. All necessary imports
2. Required fixtures (if any)
3. Comprehensive test functions covering:
   - Normal operation scenarios
   - Edge cases and boundary conditions
   - Error handling and exception testing
   - Parameterized tests where appropriate

Ensure the generated code follows pytest conventions, includes proper docstrings for each test function, and provides clear assertion messages.

{{#if existing_tests_context}}
## Integration with Existing Tests
When generating tests, consider:
- Maintain consistency with existing test patterns in {{existing_file_path}}
- Extend existing test functions rather than duplicating them
- Follow the same testing framework (pytest/unittest) as used in existing tests
{{/if}}

Generate the complete test file content below: