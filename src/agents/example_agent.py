"""
Example Agent Implementation.

This module demonstrates how to create a specialized agent by inheriting
from BaseAgent. This serves as a template for building new agents.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
from typing import Dict, Any

from .base_agent import BaseAgent


class ExampleAgent(BaseAgent):
    """
    Example agent implementation showing how to extend BaseAgent.

    This agent demonstrates the basic patterns for implementing
    specialized functionality while using the base class features.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the example agent."""
        super().__init__(
            name="ExampleAgent",
            role="Demonstrates BaseAgent usage patterns",
            config=config or {}
        )

        # Agent-specific attributes
        self.processed_tasks = 0

    async def process_task(self, task: str, context: Dict[str, Any]) -> str:
        """
        Process a task - this is where the agent's main logic goes.

        Args:
            task: The task description
            context: Additional context data

        Returns:
            The processing result
        """
        await self.log(f"🎯 Processing task: {task}", style="action")

        # Update progress
        await self.update_task_progress(0.2, "Starting task")

        # Simulate some work
        await self.sleep(1.0)

        await self.update_task_progress(0.6, "Processing data")

        # Store intermediate results
        await self.store_result(
            result=f"Intermediate result for: {task}",
            tags={"example", "intermediate"}
        )

        await self.sleep(0.5)

        await self.update_task_progress(1.0, "Completing task")

        # Final result
        result = f"✅ Task completed: {task}"

        await self.log(result, style="success")

        # Update counter
        self.processed_tasks += 1

        return result

    async def specialized_method(self) -> str:
        """
        Example of an agent-specific method.

        Returns:
            A specialized result
        """
        await self.log("🔧 Running specialized operation", style="thought")

        # Search memory for relevant information
        memories = await self.search_memory("specialized", limit=3)

        if memories:
            await self.log(f"📚 Found {len(memories)} relevant memories", style="info")

        return "Specialized operation completed"


# Example usage
async def demo():
    """Demonstrate how to use the ExampleAgent."""

    # Create and initialize agent
    config = {
        "capabilities": ["example", "demo"],
        "specialization": "demonstration"
    }

    agent = ExampleAgent(config)
    await agent.initialize()

    # Process a task
    result = await agent.process_task(
        task="Generate a simple example",
        context={"difficulty": "easy", "type": "demo"}
    )

    print(f"\nResult: {result}")

    # Communicate with another agent (mock)
    class MockAgent(BaseAgent):
        def __init__(self):
            super().__init__("MockAgent", "Mock for testing")

        async def process_task(self, task: str, context: Dict[str, Any]) -> str:
            return f"Mock response to: {task}"

    mock_agent = MockAgent()
    await mock_agent.initialize()

    # Demonstrate inter-agent communication
    response = await agent.communicate_with_agent(mock_agent, "Hello from ExampleAgent!")
    print(f"Communication: {response}")

    # Cleanup
    await agent.shutdown()
    await mock_agent.shutdown()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo())
