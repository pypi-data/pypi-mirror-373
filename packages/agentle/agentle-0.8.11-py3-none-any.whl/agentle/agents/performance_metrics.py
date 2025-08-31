"""
Module for representing and managing agent execution results.

This module provides the AgentRunOutput class which encapsulates all data
produced during an agent's execution cycle. It represents both the final response
and metadata about the execution process, including conversation steps and structured outputs.

Example:
```python
from agentle.agents.agent import Agent
from agentle.generations.providers.google.google_generation_provider import GoogleGenerationProvider

# Create and run an agent
agent = Agent(
    generation_provider=GoogleGenerationProvider(),
    model="gemini-2.5-flash",
    instructions="You are a helpful assistant."
)

# The result is an AgentRunOutput object
result = agent.run("What is the capital of France?")

# Access different aspects of the result
text_response = result.generation.text
conversation_steps = result.steps
structured_data = result.parsed  # If using a response_schema
performance_metrics = result.performance_metrics  # New performance metrics
```
"""

import logging
from collections.abc import Sequence

from rsb.models.base_model import BaseModel
from rsb.models.field import Field

from agentle.agents.step_metric import StepMetric

logger = logging.getLogger(__name__)


class PerformanceMetrics(BaseModel):
    """
    Comprehensive performance metrics for agent execution.

    This class captures detailed timing information about various phases
    of agent execution, enabling developers to identify performance
    bottlenecks and optimization opportunities.

    Attributes:
        total_execution_time_ms: Total execution time from start to finish
        input_processing_time_ms: Time spent processing input and creating context
        static_knowledge_processing_time_ms: Time spent processing static knowledge
        mcp_tools_preparation_time_ms: Time spent preparing MCP tools
        generation_time_ms: Total time spent on AI model generations
        tool_execution_time_ms: Total time spent executing tools
        final_response_processing_time_ms: Time spent processing final response
        iteration_count: Number of iterations in the main execution loop
        tool_calls_count: Total number of tool calls made
        total_tokens_processed: Total number of tokens processed
        cache_hit_rate: Percentage of cache hits vs total cache operations
        step_metrics: Detailed metrics for each execution step
        average_generation_time_ms: Average time per generation call
        average_tool_execution_time_ms: Average time per tool execution
        longest_step_duration_ms: Duration of the longest step
        shortest_step_duration_ms: Duration of the shortest step
    """

    total_execution_time_ms: float = Field(
        description="Total execution time in milliseconds"
    )
    input_processing_time_ms: float = Field(
        description="Time spent processing input and creating context"
    )
    static_knowledge_processing_time_ms: float = Field(
        description="Time spent processing static knowledge"
    )
    mcp_tools_preparation_time_ms: float = Field(
        description="Time spent preparing MCP tools"
    )
    generation_time_ms: float = Field(
        description="Total time spent on AI model generations"
    )
    tool_execution_time_ms: float = Field(
        description="Total time spent executing tools"
    )
    final_response_processing_time_ms: float = Field(
        description="Time spent processing final response"
    )
    iteration_count: int = Field(
        description="Number of iterations in the main execution loop"
    )
    tool_calls_count: int = Field(description="Total number of tool calls made")
    total_tokens_processed: int = Field(description="Total number of tokens processed")
    cache_hit_rate: float = Field(
        description="Percentage of cache hits vs total cache operations"
    )
    step_metrics: Sequence[StepMetric] = Field(
        default_factory=list, description="Metrics for each execution step"
    )

    # Derived metrics for quick analysis
    average_generation_time_ms: float = Field(
        description="Average time per generation call"
    )
    average_tool_execution_time_ms: float = Field(
        description="Average time per tool execution"
    )
    longest_step_duration_ms: float = Field(description="Duration of the longest step")
    shortest_step_duration_ms: float = Field(
        description="Duration of the shortest step"
    )

    def get_breakdown_summary(self) -> dict[str, float]:
        """
        Get a summary breakdown of time spent in different phases.

        Returns:
            Dictionary with percentage of time spent in each phase.
        """
        if self.total_execution_time_ms == 0:
            return {}

        return {
            "input_processing": (
                self.input_processing_time_ms / self.total_execution_time_ms
            )
            * 100,
            "static_knowledge": (
                self.static_knowledge_processing_time_ms / self.total_execution_time_ms
            )
            * 100,
            "mcp_preparation": (
                self.mcp_tools_preparation_time_ms / self.total_execution_time_ms
            )
            * 100,
            "generation": (self.generation_time_ms / self.total_execution_time_ms)
            * 100,
            "tool_execution": (
                self.tool_execution_time_ms / self.total_execution_time_ms
            )
            * 100,
            "final_processing": (
                self.final_response_processing_time_ms / self.total_execution_time_ms
            )
            * 100,
        }

    def get_optimization_recommendations(self) -> list[str]:
        """
        Get performance optimization recommendations based on metrics.

        Returns:
            List of optimization recommendations.
        """
        recommendations = []
        breakdown = self.get_breakdown_summary()

        if breakdown.get("static_knowledge", 0) > 30:
            recommendations.append(
                "Consider caching static knowledge or reducing knowledge base size"
            )

        if breakdown.get("tool_execution", 0) > 50:
            recommendations.append(
                "Tool execution is the bottleneck - optimize tool implementations"
            )

        if breakdown.get("generation", 0) > 40:
            recommendations.append(
                "AI generation time is high - consider using a faster model or reducing prompt complexity"
            )

        if self.iteration_count > 5:
            recommendations.append(
                "High iteration count - consider improving tool design to reduce back-and-forth"
            )

        if self.cache_hit_rate < 80 and self.cache_hit_rate > 0:
            recommendations.append("Low cache hit rate - review caching strategy")

        if self.average_tool_execution_time_ms > 5000:
            recommendations.append(
                "Tools are slow on average - optimize individual tool implementations"
            )

        return recommendations
