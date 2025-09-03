from rsb.models.base_model import BaseModel
from rsb.models.field import Field


class StepMetric(BaseModel):
    """
    Performance metrics for an individual execution step.

    This class captures timing and execution details for a single step
    in the agent's execution process, providing granular insights into
    performance characteristics.

    Attributes:
        step_id: Unique identifier for the step
        step_type: Type of step (tool_execution, generation, etc.)
        duration_ms: Time taken for this step in milliseconds
        iteration: Iteration number this step belongs to
        tool_calls_count: Number of tool calls in this step
        generation_tokens: Number of tokens generated in this step (if applicable)
        cache_hits: Number of cache hits during this step
        cache_misses: Number of cache misses during this step
    """

    step_id: str = Field(description="Unique identifier for the step")
    step_type: str = Field(
        description="Type of step (tool_execution, generation, etc.)"
    )
    duration_ms: float = Field(description="Time taken for this step in milliseconds")
    iteration: int = Field(description="Iteration number this step belongs to")
    tool_calls_count: int = Field(
        default=0, description="Number of tool calls in this step"
    )
    generation_tokens: int | None = Field(
        default=None, description="Number of tokens generated in this step"
    )
    cache_hits: int = Field(
        default=0, description="Number of cache hits during this step"
    )
    cache_misses: int = Field(
        default=0, description="Number of cache misses during this step"
    )
