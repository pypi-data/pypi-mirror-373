from collections.abc import Mapping
from typing import Any

from agentle.agents.apis.array_schema import ArraySchema
from agentle.agents.apis.endpoint_parameter import EndpointParameter
from agentle.agents.apis.object_schema import ObjectSchema
from agentle.agents.apis.parameter_location import ParameterLocation
from agentle.agents.apis.primitive_schema import PrimitiveSchema


def object_param(
    name: str,
    description: str,
    properties: Mapping[str, ObjectSchema | ArraySchema | PrimitiveSchema],
    required_props: list[str] | None = None,
    required: bool = False,
    location: ParameterLocation = ParameterLocation.BODY,
    example: Mapping[str, Any] | None = None,
) -> EndpointParameter:
    """Create an object parameter with proper schema."""
    return EndpointParameter(
        name=name,
        description=description,
        parameter_schema=ObjectSchema(
            properties=properties, required=required_props or [], example=example
        ),
        location=location,
        required=required,
    )
