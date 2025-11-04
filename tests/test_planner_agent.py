"""
Tests for PlannerAgent.

This module contains unit tests for the PlannerAgent to ensure it works
correctly and integrates properly with the BaseAgent framework.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.planner_agent import PlannerAgent


@pytest.fixture
def planner_agent():
    """Create a PlannerAgent instance for testing."""
    config = {
        "capabilities": ["planning", "task_decomposition"],
        "max_subtasks": 5
    }
    return PlannerAgent(config)


@pytest.mark.asyncio
async def test_planner_initialization(planner_agent):
    """Test that PlannerAgent initializes correctly."""
    assert planner_agent.name == "Planner"
    assert planner_agent.role == "Task Decomposition & Strategic Planning"
    assert planner_agent.config is not None
    assert "planning" in planner_agent.config["capabilities"]


@pytest.mark.asyncio
async def test_task_classification(planner_agent):
    """Test task classification functionality."""
    # Test code-related task
    task_type = await planner_agent._classify_task("Write a Python REST API")
    assert task_type == "code_generation"

    # Test research-related task
    task_type = await planner_agent._classify_task("Research quantum computing")
    assert task_type == "research"

    # Test documentation task
    task_type = await planner_agent._classify_task("Create project documentation")
    assert task_type == "documentation"

    # Test general task
    task_type = await planner_agent._classify_task("Complete the assignment")
    assert task_type == "general"


@pytest.mark.asyncio
async def test_subtask_generation(planner_agent):
    """Test subtask generation functionality."""
    task = "Build a task management API"
    context = {"include_testing": True}

    subtasks = await planner_agent.generate_subtasks(task, "code_generation", context)

    assert isinstance(subtasks, list)
    assert len(subtasks) > 0
    assert all(isinstance(subtask, str) for subtask in subtasks)

    # Check that testing was included due to context
    testing_subtasks = [s for s in subtasks if "test" in s.lower()]
    assert len(testing_subtasks) > 0


@pytest.mark.asyncio
async def test_process_task_success(planner_agent):
    """Test successful task processing."""
    task = "Create a simple web application"
    context = {"framework": "Flask"}

    result = await planner_agent.process_task(task, context)

    assert isinstance(result, str)
    assert len(result) > 0
    assert "Task Planning Summary" in result
    assert "subtasks" in result.lower()


@pytest.mark.asyncio
async def test_process_task_with_error(planner_agent):
    """Test error handling in task processing."""
    # Mock the memory store to raise an error
    planner_agent.memory.store = AsyncMock(side_effect=Exception("Memory storage failed"))

    task = "Test task that should fail"
    context = {}

    # Should raise an exception
    with pytest.raises(Exception):
        await planner_agent.process_task(task, context)


@pytest.mark.asyncio
async def test_plan_optimization(planner_agent):
    """Test plan optimization functionality."""
    # First create a plan
    task = "Build a simple API"
    context = {}

    await planner_agent.process_task(task, context)

    # Get recent plans
    recent_plans = await planner_agent.get_recent_plans(limit=1)
    assert len(recent_plans) > 0

    plan_id = recent_plans[0]["id"]

    # Test optimization
    optimized_result = await planner_agent.optimize_plan(plan_id, "speed")

    assert isinstance(optimized_result, str)
    assert "optimization" in optimized_result.lower()
    assert "speed" in optimized_result.lower()


@pytest.mark.asyncio
async def test_memory_integration(planner_agent):
    """Test that the planner integrates correctly with memory."""
    # Mock memory to verify it's being called
    planner_agent.memory.store = AsyncMock(return_value="test_memory_id")
    planner_agent.memory.retrieve = AsyncMock(return_value=[])

    task = "Test memory integration"
    context = {}

    result = await planner_agent.process_task(task, context)

    # Verify memory store was called
    planner_agent.memory.store.assert_called()
    assert planner_agent.memory.store.call_count >= 2  # Main plan + subtasks


@pytest.mark.asyncio
async def test_template_usage(planner_agent):
    """Test that templates are used appropriately."""
    # Test that code generation template is used for code tasks
    task = "Write a Python script for data processing"
    subtasks = await planner_agent.generate_subtasks(task, "code_generation")

    # Should use the code generation template
    assert len(subtasks) >= 5  # Code template has 6 steps
    assert any("test" in subtask.lower() for subtask in subtasks)
    assert any("document" in subtask.lower() for subtask in subtasks)


if __name__ == "__main__":
    """Run the tests directly."""
    asyncio.run(asyncio.gather(
        test_planner_initialization(),
        test_task_classification(),
        test_subtask_generation()
    ))
    print("✅ Basic tests completed successfully!")
