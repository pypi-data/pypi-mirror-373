# type: ignore (TODO: remove this)
from typing import (
    Type,
    Optional,
    Union,
    Any,
    get_origin,
    get_args,
    List,
    Dict,
    Tuple,
    Set,
    FrozenSet,
)
from pydantic import BaseModel, create_model, Field
import inspect


def make_fields_optional(model_class: Type[BaseModel]) -> Type[BaseModel]:
    """
    Create a new BaseModel class with all fields optional and defaulting to None.
    Recursively handles nested BaseModels and container types.

    Args:
        model_class: The Pydantic BaseModel class to transform

    Returns:
        A new BaseModel class with all fields optional

    Example:
        class User(BaseModel):
            name: str
            age: int

        OptionalUser = make_fields_optional(User)
        # OptionalUser now has: name: Optional[str] = None, age: Optional[int] = None
    """

    def transform_type(field_type: Type) -> Type:
        """Recursively transform a type to make it optional."""
        origin = get_origin(field_type)
        args = get_args(field_type)

        # Handle Union types (including Optional which is Union[T, None])
        if origin is Union:
            # Check if it's already Optional (Union[T, None])
            if type(None) in args:
                # Already optional, transform the non-None types
                non_none_args = tuple(
                    transform_type(arg) for arg in args if arg is not type(None)
                )
                if len(non_none_args) == 1:
                    return Optional[non_none_args[0]]
                else:
                    # Multiple non-None types in union
                    return Optional[Union[non_none_args]]
            else:
                # Regular Union without None, transform all args and make optional
                transformed_args = tuple(transform_type(arg) for arg in args)
                if len(transformed_args) == 1:
                    return Optional[transformed_args[0]]
                else:
                    return Optional[Union[transformed_args]]

        # Handle List types
        elif origin in (list, List):
            inner_type = args[0] if args else Any
            transformed_inner = transform_type(inner_type)
            return Optional[List[transformed_inner]]

        # Handle Dict types
        elif origin in (dict, Dict):
            if len(args) >= 2:
                key_type, value_type = args[0], args[1]
                transformed_value = transform_type(value_type)
                return Optional[Dict[key_type, transformed_value]]
            elif len(args) == 1:
                # Dict with only key type specified
                return Optional[Dict[args[0], Any]]
            else:
                return Optional[Dict[Any, Any]]

        # Handle Tuple types
        elif origin in (tuple, Tuple):
            if args:
                if len(args) == 2 and args[1] is Ellipsis:
                    # Variable length tuple: Tuple[T, ...]
                    transformed_inner = transform_type(args[0])
                    return Optional[Tuple[transformed_inner, ...]]
                else:
                    # Fixed length tuple: try to handle it
                    # Note: Dynamic tuple type creation is complex, so we simplify
                    transformed_args = [transform_type(arg) for arg in args]
                    # For simplicity, we'll treat it as a tuple of the transformed types
                    # This may not preserve exact tuple semantics but handles the common cases
                    if len(transformed_args) == 1:
                        return Optional[Tuple[transformed_args[0]]]
                    elif len(transformed_args) == 2:
                        return Optional[Tuple[transformed_args[0], transformed_args[1]]]
                    elif len(transformed_args) == 3:
                        return Optional[
                            Tuple[
                                transformed_args[0],
                                transformed_args[1],
                                transformed_args[2],
                            ]
                        ]
                    else:
                        # For more than 3 elements, fall back to general tuple
                        return Optional[tuple]
            else:
                return Optional[tuple]

        # Handle Set types
        elif origin in (set, Set):
            inner_type = args[0] if args else Any
            transformed_inner = transform_type(inner_type)
            return Optional[Set[transformed_inner]]

        # Handle FrozenSet types
        elif origin in (frozenset, FrozenSet):
            inner_type = args[0] if args else Any
            transformed_inner = transform_type(inner_type)
            return Optional[FrozenSet[transformed_inner]]

        # Handle nested BaseModel classes
        elif inspect.isclass(field_type) and issubclass(field_type, BaseModel):
            # Recursively transform nested BaseModel
            transformed_model = make_fields_optional(field_type)
            return Optional[transformed_model]

        # Handle primitive types and other classes
        else:
            return Optional[field_type]

    # Cache to avoid infinite recursion with self-referencing models
    if hasattr(make_fields_optional, "_cache"):
        cache = make_fields_optional._cache
    else:
        cache = make_fields_optional._cache = {}

    # Check cache first
    if model_class in cache:
        return cache[model_class]

    # Create placeholder to handle circular references
    new_class_name = f"{model_class.__name__}Optional"

    # Transform all fields
    new_fields = {}
    for field_name, field_info in model_class.model_fields.items():
        original_type = field_info.annotation
        transformed_type = transform_type(original_type)

        # Preserve field description if it exists
        field_kwargs = {"default": None}
        if field_info.description:
            field_kwargs["description"] = field_info.description

        new_fields[field_name] = (transformed_type, Field(**field_kwargs))

    # Create new model class
    new_model = create_model(new_class_name, **new_fields)

    # Cache the result
    cache[model_class] = new_model

    return new_model


def clear_optional_cache():
    """Clear the internal cache used by make_fields_optional."""
    if hasattr(make_fields_optional, "_cache"):
        make_fields_optional._cache.clear()


# Example usage and test cases
if __name__ == "__main__":
    # Define test models
    class Address(BaseModel):
        street: str
        city: str
        country: str = "USA"

    class User(BaseModel):
        name: str
        age: int
        email: str
        address: Address
        tags: List[str]
        metadata: Dict[str, Any]
        is_active: bool = True

    class Company(BaseModel):
        name: str
        employees: List[User]
        headquarters: Address
        revenue: Optional[float] = None

    # Transform models
    OptionalAddress = make_fields_optional(Address)
    OptionalUser = make_fields_optional(User)
    OptionalCompany = make_fields_optional(Company)

    # Test the transformed models
    print("Original Address fields:")
    for name, field in Address.model_fields.items():
        print(f"  {name}: {field.annotation}")

    print("\nOptional Address fields:")
    for name, field in OptionalAddress.model_fields.items():
        print(f"  {name}: {field.annotation}")

    # Create instances
    opt_address = OptionalAddress()
    opt_user = OptionalUser(name="John")  # Only provide some fields

    print(f"\nOptional address instance: {opt_address}")
    print(f"Optional user instance: {opt_user}")

    # Clear cache when done (optional)
    clear_optional_cache()
