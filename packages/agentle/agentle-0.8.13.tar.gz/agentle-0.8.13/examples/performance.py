"""
Example usage of the new performance metrics feature.

This example demonstrates how to use the performance metrics to identify
optimization opportunities in your agent executions.
"""

import asyncio
from typing import Any
from agentle.agents.agent import Agent
from agentle.generations.providers.google.google_generation_provider import (
    GoogleGenerationProvider,
)


def example_tool(query: str) -> str:
    """An example tool that simulates some work."""
    import time

    time.sleep(0.1)  # Simulate some work
    return f"Result for: {query}"


async def main():
    # Create an agent with tools
    agent = Agent(
        name="Performance Test Agent",
        generation_provider=GoogleGenerationProvider(),
        model="gemini-2.5-flash",
        instructions="You are a helpful assistant that uses tools to answer questions.",
        tools=[example_tool],
        debug=True,  # Enable debug logging to see performance details
    )

    # Run the agent
    result = await agent.run_async(
        "Use the example tool to search for 'python performance'"
    )

    # Analyze the performance metrics
    if result.performance_metrics:
        metrics = result.performance_metrics

        print("🚀 PERFORMANCE ANALYSIS")
        print("=" * 50)
        print(f"Total execution time: {metrics.total_execution_time_ms:.2f}ms")
        print(f"Iterations: {metrics.iteration_count}")
        print(f"Tool calls: {metrics.tool_calls_count}")
        print(f"Tokens processed: {metrics.total_tokens_processed}")
        print(f"Cache hit rate: {metrics.cache_hit_rate:.1f}%")

        print("\n📊 TIME BREAKDOWN:")
        breakdown = metrics.get_breakdown_summary()
        for phase, percentage in breakdown.items():
            print(f"  {phase.replace('_', ' ').title()}: {percentage:.1f}%")

        print("\n⚡ AVERAGES:")
        print(f"  Generation time: {metrics.average_generation_time_ms:.2f}ms")
        print(f"  Tool execution time: {metrics.average_tool_execution_time_ms:.2f}ms")

        print("\n📈 STEP ANALYSIS:")
        print(f"  Longest step: {metrics.longest_step_duration_ms:.2f}ms")
        print(f"  Shortest step: {metrics.shortest_step_duration_ms:.2f}ms")

        print("\n🔍 DETAILED STEPS:")
        for i, step in enumerate(metrics.step_metrics, 1):
            print(f"  Step {i}: {step.step_type} - {step.duration_ms:.2f}ms")
            if step.tool_calls_count > 0:
                print(f"    ↳ Tool calls: {step.tool_calls_count}")
            if step.generation_tokens:
                print(f"    ↳ Tokens: {step.generation_tokens}")

        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        recommendations = metrics.get_optimization_recommendations()
        if recommendations:
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print("  ✅ No specific recommendations - performance looks good!")

        print("\n📝 FINAL RESPONSE:")
        print(f"  {result.text[:200]}{'...' if len(result.text) > 200 else ''}")


def performance_comparison_example():
    """
    Example showing how to compare performance across different agent configurations.
    """

    async def test_agent_performance(agent_name: str, agent: Agent) -> dict[str, Any]:
        """Test an agent and return performance metrics."""
        result = await agent.run_async("What is the capital of France?")

        if result.performance_metrics:
            return {
                "name": agent_name,
                "total_time": result.performance_metrics.total_execution_time_ms,
                "generation_time": result.performance_metrics.generation_time_ms,
                "tool_time": result.performance_metrics.tool_execution_time_ms,
                "iterations": result.performance_metrics.iteration_count,
                "tokens": result.performance_metrics.total_tokens_processed,
            }
        return {"name": agent_name, "error": "No metrics available"}

    async def compare_agents():
        # Agent without tools
        simple_agent = Agent(
            name="Simple Agent",
            generation_provider=GoogleGenerationProvider(),
            model="gemini-2.5-flash",
            instructions="You are a helpful assistant.",
        )

        # Agent with tools
        tool_agent = Agent(
            name="Tool Agent",
            generation_provider=GoogleGenerationProvider(),
            model="gemini-2.5-flash",
            instructions="You are a helpful assistant.",
            tools=[example_tool],
        )

        # Run performance tests
        simple_metrics = await test_agent_performance("Simple", simple_agent)
        tool_metrics = await test_agent_performance("Tool", tool_agent)

        print("🏁 PERFORMANCE COMPARISON")
        print("=" * 50)
        print(f"Simple Agent: {simple_metrics['total_time']:.2f}ms")
        print(f"Tool Agent: {tool_metrics['total_time']:.2f}ms")
        print(
            f"Difference: {tool_metrics['total_time'] - simple_metrics['total_time']:.2f}ms"
        )

        if tool_metrics["total_time"] > simple_metrics["total_time"]:
            overhead = (
                (tool_metrics["total_time"] / simple_metrics["total_time"]) - 1
            ) * 100
            print(f"Tool overhead: {overhead:.1f}%")

    return compare_agents


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
