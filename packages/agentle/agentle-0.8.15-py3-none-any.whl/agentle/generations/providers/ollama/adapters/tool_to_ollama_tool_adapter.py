"""
Adapter module for converting Agentle Tool objects to Ollama Tool format.

This module provides the ToolToOllamaToolAdapter class, which transforms
Agentle's internal Tool representation into the Tool format expected by Ollama's
API. This conversion is necessary when using Agentle tools with Ollama models
that support function calling capabilities.

The adapter handles the mapping of Agentle tool definitions, including parameters,
types, and descriptions, to Ollama's schema-based function declaration format.
It includes comprehensive type mapping and JSON Schema conversion to match
Ollama's expected structure.

This adapter is typically used internally by the OllamaGenerationProvider when
preparing tool definitions to be sent to Ollama's API.

Example:
```python
from agentle.generations.providers.ollama._adapters.tool_to_ollama_tool_adapter import (
    ToolToOllamaToolAdapter
)
from agentle.generations.tools.tool import Tool

# Create an Agentle tool
weather_tool = Tool(
    name="get_weather",
    description="Get the current weather for a location",
    parameters={
        "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA",
            "required": True
        },
        "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "default": "celsius"
        }
    }
)

# Convert to Ollama's format
adapter = ToolToOllamaToolAdapter()
ollama_tool = adapter.adapt(weather_tool)

# Now use with Ollama's API
response = client.chat(
    model="llama3.1",
    messages=[{"role": "user", "content": "What's the weather in London?"}],
    tools=[ollama_tool]
)
```
"""

from __future__ import annotations

import logging
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Mapping,
    Sequence,
    TypedDict,
    Union,
    cast,
    override,
)

from rsb.adapters.adapter import Adapter

from agentle.generations.tools.tool import Tool

if TYPE_CHECKING:
    from ollama._types import Tool as OllamaTool

# Constants for validation
MAX_FUNCTION_NAME_LENGTH = 64
FUNCTION_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\.\-]*$")
MAX_PARAM_NAME_LENGTH = 64
PARAM_NAME_PATTERN = re.compile(r"^[a-zA-Z_$][a-zA-Z0-9_]*$")

# Special JSON Schema keywords that should be allowed despite not matching the normal pattern
JSON_SCHEMA_KEYWORDS = {"$schema", "$ref", "$id", "$defs", "$comment", "$vocabulary"}

# Type aliases for better readability
JSONValue = bool | int | float | str | list[Any] | dict[str, Any] | None
JSONObject = dict[str, JSONValue]


class _JSONSchemaDict(TypedDict, total=False):
    """Type definition for JSON Schema dictionary."""

    type: str
    description: str | None
    default: Any
    properties: dict[str, _JSONSchemaDict]
    items: _JSONSchemaDict | list[_JSONSchemaDict]
    required: list[str]
    minItems: int | None
    maxItems: int | None
    minLength: int | None
    maxLength: int | None
    pattern: str | None
    minimum: float | None
    maximum: float | None
    enum: list[Any] | None
    additionalProperties: bool | None


class ToolToOllamaToolAdapter(Adapter[Tool[Any], "OllamaTool"]):
    """
    Adapter for converting Agentle Tool objects to Ollama Tool format.

    This adapter transforms Agentle's Tool objects into the function-based
    Tool format used by Ollama's API. It handles the mapping between
    Agentle's parameter definitions and Ollama's schema-based format, including
    type conversion, required parameters, and default values.

    The adapter implements Agentle's provider abstraction layer pattern, which allows
    tools defined once to be used across different AI providers without modification.

    Key features:
    - Conversion of parameter types to JSON Schema format
    - Handling of required parameters and nested objects
    - Support for enums, arrays, and complex types
    - Validation of function and parameter names
    - Comprehensive error handling and logging

    Example:
        ```python
        # Create an Agentle tool for database queries
        db_tool = Tool(
            name="query_database",
            description="Execute a database query",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute",
                    "required": True
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "required": False,
                    "default": 100
                }
            }
        )

        # Convert to Ollama's format
        adapter = ToolToOllamaToolAdapter()
        ollama_tool = adapter.adapt(db_tool)
        ```
    """

    def __init__(self) -> None:
        """Initialize the adapter with a logger."""
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def _validate_function_name(self, name: str) -> None:
        """Validate function name according to common API requirements."""
        if not name:
            raise ValueError("Function name cannot be empty")
        if len(name) > MAX_FUNCTION_NAME_LENGTH:
            raise ValueError(
                f"Function name cannot exceed {MAX_FUNCTION_NAME_LENGTH} characters"
            )
        if not FUNCTION_NAME_PATTERN.match(name):
            raise ValueError(
                "Function name must start with a letter or underscore and contain only "
                + "letters, numbers, underscores, dots, or dashes"
            )

    def _validate_parameter_name(self, name: str) -> None:
        """Validate parameter name according to JSON Schema requirements."""
        if not name:
            raise ValueError("Parameter name cannot be empty")
        if len(name) > MAX_PARAM_NAME_LENGTH:
            raise ValueError(
                f"Parameter name cannot exceed {MAX_PARAM_NAME_LENGTH} characters"
            )

        # Allow special JSON Schema keywords
        if name in JSON_SCHEMA_KEYWORDS:
            return

        if not PARAM_NAME_PATTERN.match(name):
            raise ValueError(
                "Parameter name must start with a letter, underscore, or $ and contain only letters, numbers, or underscores"
            )

    def _normalize_type(self, param_type: Union[str, Sequence[str]]) -> str:
        """Normalize parameter type to a standard JSON Schema type."""
        if isinstance(param_type, (list, tuple)):
            # Handle union types by taking the first type
            param_type = param_type[0] if param_type else "string"

        type_str = str(param_type).lower()

        # Type mapping from various formats to JSON Schema types
        type_mapping = {
            "str": "string",
            "string": "string",
            "int": "integer",
            "integer": "integer",
            "float": "number",
            "number": "number",
            "bool": "boolean",
            "boolean": "boolean",
            "list": "array",
            "array": "array",
            "dict": "object",
            "object": "object",
        }

        normalized_type = type_mapping.get(type_str, type_str)

        # Validate that it's a known JSON Schema type
        valid_types = {
            "string",
            "integer",
            "number",
            "boolean",
            "array",
            "object",
            "null",
        }
        if normalized_type not in valid_types:
            self._logger.warning(
                f"Unknown parameter type '{param_type}', defaulting to 'string'"
            )
            normalized_type = "string"

        return normalized_type

    def _create_property_from_param(
        self, param_info: Mapping[str, Any], param_name: str
    ) -> dict[str, Any]:
        """Create an Ollama Property from Agentle parameter info."""
        property_dict: dict[str, Any] = {}

        # Handle type
        param_type = param_info.get("type", "string")
        normalized_type = self._normalize_type(param_type)
        property_dict["type"] = normalized_type

        # Handle description
        if "description" in param_info:
            property_dict["description"] = str(param_info["description"])

        # Handle enum
        if "enum" in param_info:
            property_dict["enum"] = list(param_info["enum"])

        # Handle array items
        if normalized_type == "array" and "items" in param_info:
            items_info: Any = param_info["items"]
            if isinstance(items_info, dict):
                property_dict["items"] = self._create_property_from_param(
                    cast(dict[str, Any], items_info), f"{param_name}[items]"
                )
            else:
                # Simple type for items
                property_dict["items"] = {"type": self._normalize_type(str(items_info))}

        # Handle object properties (nested objects)
        if normalized_type == "object" and "properties" in param_info:
            nested_properties = {}
            nested_required = []

            for nested_name, nested_info in param_info["properties"].items():
                if isinstance(nested_info, dict):
                    self._validate_parameter_name(nested_name)
                    nested_properties[nested_name] = self._create_property_from_param(
                        cast(dict[str, Any], nested_info), f"{param_name}.{nested_name}"
                    )
                    if nested_info.get("required", False):
                        nested_required.append(nested_name)

            if nested_properties:
                property_dict["properties"] = nested_properties
            if nested_required:
                property_dict["required"] = nested_required

        # Handle constraints based on type
        if normalized_type == "string":
            if "minLength" in param_info:
                property_dict["minLength"] = int(param_info["minLength"])
            if "maxLength" in param_info:
                property_dict["maxLength"] = int(param_info["maxLength"])
            if "pattern" in param_info:
                property_dict["pattern"] = str(param_info["pattern"])

        elif normalized_type in ("integer", "number"):
            if "minimum" in param_info:
                property_dict["minimum"] = float(param_info["minimum"])
            if "maximum" in param_info:
                property_dict["maximum"] = float(param_info["maximum"])

        elif normalized_type == "array":
            if "minItems" in param_info:
                property_dict["minItems"] = int(param_info["minItems"])
            if "maxItems" in param_info:
                property_dict["maxItems"] = int(param_info["maxItems"])

        return property_dict

    def _convert_agentle_params_to_ollama_parameters(
        self, agentle_params: Mapping[str, Any]
    ) -> dict[str, Any]:
        """
        Convert Agentle's parameter format to Ollama's Parameters format.

        Agentle format:
        {
            'param1': {'type': 'str', 'required': True, 'description': '...'},
            'param2': {'type': 'int', 'required': False, 'default': 42}
        }

        Ollama Parameters format (matching the desired output):
        {
            'type': 'object',
            'properties': {
                'param1': {'type': 'string', 'description': '...'},
                'param2': {'type': 'integer'}
            },
            'required': ['param1']
        }
        """
        # Check if this is already in the correct format
        if "type" in agentle_params and agentle_params.get("type") == "object":
            return dict(agentle_params)

        # Convert from Agentle flat format
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param_info in agentle_params.items():
            if not isinstance(param_info, dict):
                continue

            # Validate parameter name
            self._validate_parameter_name(param_name)

            # Check if this parameter is required
            is_required = param_info.get("required", False)
            if is_required:
                required.append(param_name)

            # Create the property
            properties[param_name] = self._create_property_from_param(
                cast(dict[str, Any], param_info), param_name
            )

        # Build the parameters object according to Ollama's expected format
        parameters: dict[str, Any] = {"type": "object", "properties": properties}

        if required:
            parameters["required"] = required

        # Handle $defs if present in the original parameters
        if "$defs" in agentle_params:
            parameters["$defs"] = agentle_params["$defs"]

        return parameters

    @override
    def adapt(self, agentle_tool: Tool[Any]) -> OllamaTool:
        """
        Convert an Agentle Tool to an Ollama Tool.

        Args:
            agentle_tool: The Agentle Tool object to convert.

        Returns:
            OllamaTool: An Ollama Tool object matching the desired output structure.

        Raises:
            ValueError: If the tool name or parameters are invalid.
        """
        from ollama._types import Tool as OllamaTool

        # Validate function name
        self._validate_function_name(agentle_tool.name)

        self._logger.debug(f"Converting tool '{agentle_tool.name}' to Ollama format")

        # Create the function object
        function_dict: dict[str, Any] = {"name": agentle_tool.name}

        if agentle_tool.description:
            function_dict["description"] = agentle_tool.description

        # Convert parameters if they exist
        if agentle_tool.parameters:
            self._logger.debug(
                f"Converting parameters for tool '{agentle_tool.name}': {agentle_tool.parameters}"
            )

            parameters = self._convert_agentle_params_to_ollama_parameters(
                agentle_tool.parameters
            )
            function_dict["parameters"] = parameters

            # Log detailed parameter information
            if "properties" in parameters:
                self._logger.debug(
                    f"Tool '{agentle_tool.name}' has {len(parameters['properties'])} parameters:"
                )
                for param_name, param_schema in parameters["properties"].items():
                    param_type = param_schema.get("type", "unknown")
                    param_desc = param_schema.get("description", "")
                    is_required = param_name in parameters.get("required", [])
                    self._logger.debug(
                        f"  - {param_name}: type={param_type}, description='{param_desc}', required={is_required}"
                    )
                self._logger.debug(
                    f"Required parameters: {parameters.get('required', [])}"
                )
        else:
            self._logger.debug(f"Tool '{agentle_tool.name}' has no parameters")

        self._logger.info(
            f"Successfully created Ollama tool for '{agentle_tool.name}' with "
            + f"{len(function_dict.get('parameters', {}).get('properties', {}))} parameters"
        )

        return OllamaTool.model_validate(
            {"type": "function", "function": function_dict}
        )
