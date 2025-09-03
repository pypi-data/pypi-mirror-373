from agentle.agents.apis.endpoint_parameter import EndpointParameter
from agentle.agents.apis.parameter_location import ParameterLocation
from agentle.agents.apis.primitive_schema import PrimitiveSchema


def string_param(
    name: str,
    description: str,
    required: bool = False,
    enum: list[str] | None = None,
    default: str | None = None,
    location: ParameterLocation = ParameterLocation.QUERY,
) -> EndpointParameter:
    """Create a string parameter."""
    return EndpointParameter(
        name=name,
        description=description,
        parameter_schema=PrimitiveSchema(type="string", enum=enum),
        location=location,
        required=required,
        default=default,
    )
