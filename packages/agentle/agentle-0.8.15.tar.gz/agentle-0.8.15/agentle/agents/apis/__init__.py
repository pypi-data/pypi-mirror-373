# yourpkg/__init__.py
from .object_schema import ObjectSchema
from .array_schema import ArraySchema
from .primitive_schema import PrimitiveSchema
from .endpoint_parameter import EndpointParameter

_types = {
    "ObjectSchema": ObjectSchema,
    "ArraySchema": ArraySchema,
    "PrimitiveSchema": PrimitiveSchema,
}


ObjectSchema.model_rebuild(_types_namespace=_types)
ArraySchema.model_rebuild(_types_namespace=_types)
PrimitiveSchema.model_rebuild(_types_namespace=_types)
EndpointParameter.model_rebuild(_types_namespace=_types)
