from agentle.agents.apis.endpoint_parameter import EndpointParameter
from agentle.agents.apis.parameter_location import ParameterLocation
from agentle.agents.apis.primitive_schema import PrimitiveSchema


def integer_param(
    name: str,
    description: str,
    required: bool = False,
    minimum: int | None = None,
    maximum: int | None = None,
    default: int | None = None,
    location: ParameterLocation = ParameterLocation.QUERY,
) -> EndpointParameter:
    """Create an integer parameter."""
    return EndpointParameter(
        name=name,
        description=description,
        parameter_schema=PrimitiveSchema(
            type="integer", minimum=minimum, maximum=maximum
        ),
        location=location,
        required=required,
        default=default,
    )
