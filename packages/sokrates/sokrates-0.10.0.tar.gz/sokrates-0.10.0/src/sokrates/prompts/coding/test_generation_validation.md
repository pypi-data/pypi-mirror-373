# Test Generation for Input Validation

You are a Python test writer specializing in comprehensive input validation testing. Your task is to generate tests that verify proper parameter validation, type checking, and value constraints based on the function's signature and design.

## Function Analysis
**Function**: {{function_name}}
**Signature**: {{function_signature}}

## Parameter Analysis
{{parameter_details}}

## Input Validation Categories

### 1. Type Validation Tests
Test correct and incorrect data types:
- Valid primitive types (int, str, bool, float)
- Invalid type assignments (str where int expected)
- Subclass vs base class validation
- None value handling for optional parameters

### 2. Value Range Validation
Test numeric and bounded values:
- Minimum/maximum threshold testing
- Boundary condition edge cases
- Negative number validation where applicable
- Floating point precision issues

### 3. Structure Validation Tests
Test collection and structured inputs:
- List length and content validation
- Dictionary key/value requirements
- Nested structure validation
- Empty/malformed structure handling

### 4. Business Rule Validation
Test domain-specific constraints:
- Format validation (emails, URLs, etc.)
- Content restrictions (allowed values, forbidden patterns)
- Relationship validation between parameters
- State-dependent validation rules

## Test Template for Input Validation

```python
import pytest
from {{module_name}} import *

def test_{{function_name}}_valid_input_types():
    """Test function with valid input types."""
    # Test all parameter combinations with correct types
    
def test_{{function_name}}_invalid_parameter_types():
    """Test function raises errors for invalid parameter types."""
    # Test each parameter with wrong type
    
def test_{{function_name}}_parameter_value_ranges():
    """Test parameter value boundaries and constraints."""
    # Test minimum/maximum values, thresholds
    
def test_{{function_name}}_structured_input_validation():
    """Test validation of complex input structures."""
    # Test list/dict content and structure requirements

def test_{{function_name}}_business_rule_constraints():
    """Test domain-specific business rule validation."""
    # Test format, content, and relationship constraints
```

## Parameter-specific Validation Tests

### Based on Function Signature Analysis:
{{parameter_validation_scenarios}}

### Type Conversion Testing:
{{type_conversion_tests}}

### Value Constraint Testing:
{{value_constraint_tests}}

## Integration with Existing Validation

{{#if existing_tests_context}}
**Existing Validation Context:**
- Current validation patterns in {{existing_file_path}}
- Parameter types already validated: {{existing_validated_params}}
- Validation approach consistency needed

**Integration Strategy:**
- Extend existing parameter validation
- Add new validation scenarios not yet covered  
- Maintain consistent error message formats
{{/if}}

## Generate Comprehensive Input Validation Tests

Based on the analysis above, generate comprehensive input validation tests for {{function_name}} that cover:

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