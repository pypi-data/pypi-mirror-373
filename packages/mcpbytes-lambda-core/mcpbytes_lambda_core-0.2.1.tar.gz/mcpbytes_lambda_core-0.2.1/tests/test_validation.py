"""
Unit tests for mcpbytes_lambda.core.validation module.
"""

import pytest
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from mcpbytes_lambda.core.validation import (
    python_type_to_json_schema,
    dataclass_to_json_schema,
    generate_tool_schema,
    extract_prompt_arguments,
    create_tool_annotations,
    validate_tool_parameters,
    extract_param_description,
)
from mcpbytes_lambda.core.types import ToolAnnotations, PromptArgument


class TestPythonTypeToJsonSchema:
    """Test python_type_to_json_schema function."""
    
    def test_primitive_types(self):
        """Test conversion of primitive Python types."""
        assert python_type_to_json_schema(str) == {"type": "string"}
        assert python_type_to_json_schema(int) == {"type": "integer"}
        assert python_type_to_json_schema(float) == {"type": "number"}
        assert python_type_to_json_schema(bool) == {"type": "boolean"}
    
    def test_none_type(self):
        """Test conversion of NoneType."""
        assert python_type_to_json_schema(type(None)) == {"type": "null"}
    
    def test_optional_types(self):
        """Test conversion of Optional types."""
        # Optional[str] should resolve to string schema
        schema = python_type_to_json_schema(Optional[str])
        assert schema == {"type": "string"}
    
    def test_list_types(self):
        """Test conversion of List types."""
        schema = python_type_to_json_schema(List[str])
        expected = {"type": "array", "items": {"type": "string"}}
        assert schema == expected
    
    def test_dict_types(self):
        """Test conversion of Dict types."""
        schema = python_type_to_json_schema(Dict[str, int])
        expected = {"type": "object", "additionalProperties": {"type": "integer"}}
        assert schema == expected
    
    def test_union_types(self):
        """Test conversion of Union types."""
        schema = python_type_to_json_schema(Union[str, int])
        expected = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        assert schema == expected
    
    def test_fallback_for_complex_types(self):
        """Test fallback behavior for complex types."""
        # Should fallback to object type for unknown types
        schema = python_type_to_json_schema(object)
        assert schema == {"type": "object"}


class TestDataclassToJsonSchema:
    """Test dataclass_to_json_schema function."""
    
    def test_simple_dataclass(self):
        """Test conversion of simple dataclass."""
        @dataclass
        class SimpleData:
            name: str
            age: int
            active: bool = True
        
        schema = dataclass_to_json_schema(SimpleData)
        expected = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "active": {"type": "boolean"}
            },
            "required": ["name", "age"]
        }
        assert schema == expected
    
    def test_dataclass_with_optional_fields(self):
        """Test dataclass with optional fields."""
        @dataclass
        class OptionalData:
            required_field: str
            optional_field: Optional[str] = None
        
        schema = dataclass_to_json_schema(OptionalData)
        assert "required_field" in schema["required"]
        assert "optional_field" not in schema["required"]


class TestGenerateToolSchema:
    """Test generate_tool_schema function."""
    
    def test_simple_function(self):
        """Test schema generation for simple function."""
        def simple_func(name: str, age: int) -> str:
            return f"Hello {name}, age {age}"
        
        schema = generate_tool_schema(simple_func)
        expected = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        assert schema == expected
    
    def test_function_with_defaults(self):
        """Test schema generation for function with default values."""
        def func_with_defaults(name: str, greeting: str = "Hello") -> str:
            return f"{greeting} {name}"
        
        schema = generate_tool_schema(func_with_defaults)
        assert "name" in schema["required"]
        assert "greeting" not in schema["required"]
        assert "greeting" in schema["properties"]
    
    def test_function_with_docstring_descriptions(self):
        """Test schema generation with parameter descriptions from docstring."""
        def documented_func(name: str, age: int) -> str:
            """
            A documented function.
            
            Args:
                name: The person's name
                age: The person's age in years
            """
            return f"Hello {name}, age {age}"
        
        schema = generate_tool_schema(documented_func)
        assert schema["properties"]["name"]["description"] == "The person's name"
        assert schema["properties"]["age"]["description"] == "The person's age in years"
    
    def test_function_without_type_hints(self):
        """Test schema generation for function without type hints."""
        def untyped_func(name, age):
            return f"Hello {name}, age {age}"
        
        schema = generate_tool_schema(untyped_func)
        # Should still generate schema with string fallback
        assert schema["type"] == "object"
        assert "properties" in schema


class TestExtractPromptArguments:
    """Test extract_prompt_arguments function."""
    
    def test_simple_prompt_function(self):
        """Test extracting arguments from simple prompt function."""
        def simple_prompt(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"
        
        args = extract_prompt_arguments(simple_prompt)
        assert len(args) == 2
        
        name_arg = next(arg for arg in args if arg.name == "name")
        assert name_arg.required is True
        
        greeting_arg = next(arg for arg in args if arg.name == "greeting")
        assert greeting_arg.required is False
    
    def test_prompt_with_docstring(self):
        """Test extracting arguments with descriptions from docstring."""
        def documented_prompt(name: str, style: str = "formal") -> str:
            """
            Generate a greeting.
            
            Args:
                name: The person to greet
                style: The greeting style (formal or casual)
            """
            return f"Hello, {name}"
        
        args = extract_prompt_arguments(documented_prompt)
        name_arg = next(arg for arg in args if arg.name == "name")
        assert "person to greet" in name_arg.description
        
        style_arg = next(arg for arg in args if arg.name == "style")
        assert "greeting style" in style_arg.description


class TestCreateToolAnnotations:
    """Test create_tool_annotations function."""
    
    def test_default_annotations(self):
        """Test creating annotations with defaults."""
        annotations = create_tool_annotations()
        assert annotations.title is None
        assert annotations.readOnlyHint is False
        assert annotations.destructiveHint is False
        assert annotations.idempotentHint is False
        assert annotations.openWorldHint is True
    
    def test_custom_annotations(self):
        """Test creating annotations with custom values."""
        annotations = create_tool_annotations(
            title="Custom Tool",
            read_only=True,
            idempotent=True
        )
        assert annotations.title == "Custom Tool"
        assert annotations.readOnlyHint is True
        assert annotations.idempotentHint is True


class TestValidateToolParameters:
    """Test validate_tool_parameters function."""
    
    def test_valid_parameters(self):
        """Test validation with valid parameters."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        arguments = {"name": "John", "age": 30}
        
        errors = validate_tool_parameters(schema, arguments)
        assert len(errors) == 0
    
    def test_missing_required_parameter(self):
        """Test validation with missing required parameter."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        arguments = {"name": "John"}  # Missing 'age'
        
        errors = validate_tool_parameters(schema, arguments)
        assert len(errors) == 1
        assert "Missing required parameter: age" in errors[0]
    
    def test_wrong_parameter_type(self):
        """Test validation with wrong parameter type."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        arguments = {"name": "John", "age": "thirty"}  # Wrong type for age
        
        errors = validate_tool_parameters(schema, arguments)
        assert len(errors) == 1
        assert "age" in errors[0]
        assert "integer" in errors[0]
    
    def test_extra_parameters_allowed(self):
        """Test that extra parameters are allowed."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        arguments = {"name": "John", "extra": "value"}
        
        errors = validate_tool_parameters(schema, arguments)
        assert len(errors) == 0  # Extra parameters should be allowed
    
    def test_array_parameter_validation(self):
        """Test validation of array parameters."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["items"]
        }
        
        # Valid array
        arguments = {"items": ["a", "b", "c"]}
        errors = validate_tool_parameters(schema, arguments)
        assert len(errors) == 0
        
        # Invalid array (wrong item type)
        arguments = {"items": ["a", 123, "c"]}
        errors = validate_tool_parameters(schema, arguments)
        assert len(errors) == 1  # Implementation validates array item types
        assert "items" in errors[0]
        assert "array of a string" in errors[0]


class TestExtractParamDescription:
    """Test extract_param_description function."""
    
    def test_google_style_docstring(self):
        """Test extracting description from Google-style docstring."""
        def func_with_google_docs(name: str, age: int):
            """
            A function with Google-style documentation.
            
            Args:
                name: The person's name
                age: The person's age in years
            """
            pass
        
        name_desc = extract_param_description(func_with_google_docs, "name")
        age_desc = extract_param_description(func_with_google_docs, "age")
        
        assert name_desc == "The person's name"
        assert age_desc == "The person's age in years"
    
    def test_sphinx_style_docstring(self):
        """Test extracting description from Sphinx-style docstring."""
        def func_with_sphinx_docs(name: str):
            """
            A function with Sphinx-style documentation.
            
            :param name: The person's name
            """
            pass
        
        desc = extract_param_description(func_with_sphinx_docs, "name")
        assert desc == "The person's name"
    
    def test_no_docstring(self):
        """Test behavior when function has no docstring."""
        def func_without_docs(name: str):
            pass
        
        desc = extract_param_description(func_without_docs, "name")
        assert desc == ""
    
    def test_parameter_not_documented(self):
        """Test behavior when parameter is not documented."""
        def func_partial_docs(name: str, age: int):
            """
            A function with partial documentation.
            
            Args:
                name: The person's name
            """
            pass
        
        name_desc = extract_param_description(func_partial_docs, "name")
        age_desc = extract_param_description(func_partial_docs, "age")
        
        assert name_desc == "The person's name"
        assert age_desc == ""
