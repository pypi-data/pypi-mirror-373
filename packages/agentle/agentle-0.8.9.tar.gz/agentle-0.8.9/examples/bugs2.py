# THE ISSUE: Pydantic field validation is resetting Tool's _callable_ref

# Let's test this theory step by step:

from agentle.generations.tools.tool import Tool
from pydantic import BaseModel, Field
from typing import Sequence, Any, Callable


def search_web(query: str) -> str:
    return f"Results for: {query}"


# 1. Test: Create Tool outside of any Pydantic model
print("=== TEST 1: Tool Creation ===")
tool = Tool.from_callable(search_web)
print(f"Tool _callable_ref: {tool._callable_ref}")
print(f"Tool ID: {id(tool)}")

# 2. Test: What happens when we put Tool in a simple list?
print("\n=== TEST 2: Simple List ===")
tool_list = [tool]
print(f"List tool _callable_ref: {tool_list[0]._callable_ref}")
print(f"List tool ID: {id(tool_list[0])} (same: {id(tool_list[0]) == id(tool)})")

# 3. Test: What happens with Pydantic Field validation?
print("\n=== TEST 3: Pydantic Field Validation ===")


class SimpleModel(BaseModel):
    # This mimics Agent's tools field
    tools: Sequence[Tool[Any] | Callable[..., object]] = Field(default_factory=list)


# Create model with our tool
print("Creating SimpleModel with tool...")
simple_model = SimpleModel(tools=[tool])

print(
    f"Model tool _callable_ref: {getattr(simple_model.tools[0], '_callable_ref', 'MISSING')}"
)
print(
    f"Model tool ID: {id(simple_model.tools[0])} (same: {id(simple_model.tools[0]) == id(tool)})"
)

# 4. Test: Does the original tool still have _callable_ref?
print(f"\nOriginal tool _callable_ref after model creation: {tool._callable_ref}")

# 5. Test: What if we create the model with a callable instead?
print("\n=== TEST 4: Pydantic with Callable ===")
model_with_callable = SimpleModel(tools=[search_web])
tool_from_callable = model_with_callable.tools[0]
print(f"Type: {type(tool_from_callable)}")
if hasattr(tool_from_callable, "_callable_ref"):
    print(f"Callable tool _callable_ref: {tool_from_callable._callable_ref}")

# 6. Test: Sequence validation behavior
print("\n=== TEST 5: Sequence Validation ===")

# Test if Sequence[Tool | Callable] causes the issue
from typing import Union


class TestModel(BaseModel):
    # Different field types to isolate the issue
    tools_list: list[Tool] = Field(default_factory=list)
    tools_sequence: Sequence[Tool] = Field(default_factory=list)
    tools_union: Sequence[Union[Tool, Callable]] = Field(default_factory=list)


# Test each field type
original_tool = Tool.from_callable(search_web)
print(f"Original tool _callable_ref: {original_tool._callable_ref}")

print("\nTesting list[Tool]...")
test1 = TestModel(tools_list=[original_tool])
print(
    f"list[Tool] _callable_ref: {getattr(test1.tools_list[0], '_callable_ref', 'MISSING')}"
)

print("\nTesting Sequence[Tool]...")
test2 = TestModel(tools_sequence=[original_tool])
print(
    f"Sequence[Tool] _callable_ref: {getattr(test2.tools_sequence[0], '_callable_ref', 'MISSING')}"
)

print("\nTesting Sequence[Union[Tool, Callable]]...")
test3 = TestModel(tools_union=[original_tool])
print(
    f"Union _callable_ref: {getattr(test3.tools_union[0], '_callable_ref', 'MISSING')}"
)

# 7. Test: Does this happen with frozen=False?
print("\n=== TEST 6: Frozen vs Non-Frozen ===")

# Check Tool's current frozen status
from agentle.generations.tools.tool import Tool as OriginalTool

print(f"Tool model_config frozen: {OriginalTool.model_config.get('frozen', 'not set')}")

# The issue might be in how Pydantic handles Sequence validation with frozen models
# Let's see if sequence conversion triggers reconstruction
test_sequence = list([original_tool])  # Convert to list explicitly
print(
    f"Explicit list conversion _callable_ref: {getattr(test_sequence[0], '_callable_ref', 'MISSING')}"
)

# Direct sequence assignment
import typing

test_seq: Sequence[Tool] = [original_tool]
print(
    f"Direct sequence assignment _callable_ref: {getattr(test_seq[0], '_callable_ref', 'MISSING')}"
)
