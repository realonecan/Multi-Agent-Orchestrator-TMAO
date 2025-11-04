"""
Builder Agent Implementation.

This module implements the BuilderAgent which executes planned subtasks from the PlannerAgent.
The BuilderAgent simulates or performs actual work (code generation, document writing, analysis)
and stores results in memory for other agents to use.

The BuilderAgent serves as the execution engine in the multi-agent orchestration pipeline.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
from typing import Any, Dict, List

from .base_agent import BaseAgent
from src.core.memory import MemoryType, MemoryQuery

# UI event publishing
try:
    from src.ui.adapters import publish_chat, publish_progress
    UI_ENABLED = True
    
except ImportError:
    UI_ENABLED = False


class BuilderAgent(BaseAgent):
    """
    Builder Agent for task execution and implementation.

    The BuilderAgent receives planned subtasks from the PlannerAgent and executes
    or simulates their completion. It handles code generation, document writing,
    analysis, and other implementation tasks.

    Attributes:
        Inherits all attributes from BaseAgent
        execution_mode: How to execute subtasks (parallel/sequential)
        max_concurrency: Maximum concurrent subtask execution
        error_recovery: Whether to retry failed subtasks
    """

    def __init__(self, config: Dict[str, Any] = None, shared_memory=None):
        """
        Initialize the BuilderAgent.

        Args:
            config: Configuration dictionary with agent-specific settings
            shared_memory: Optional shared MemoryManager instance
        """
        super().__init__(
            name="Builder",
            role="Implementation & Execution",
            config=config or {},
            shared_memory=shared_memory
        )

        # Execution configuration
        self.execution_mode = self.config.get("execution_mode", "sequential")
        self.max_concurrency = self.config.get("max_concurrency", 3)
        self.error_recovery = self.config.get("error_recovery", True)

        # Execution state
        self._executed_subtasks = 0
        self._total_subtasks = 0

    async def process_task(self, task: str, context: Dict[str, Any]) -> str:
        """
        Process a building task by executing planned subtasks.

        Args:
            task: The main task description (used to find related plans)
            context: Additional context including plan_id, execution preferences, etc.

        Returns:
            Summary of execution results

        Raises:
            Exception: If task execution fails
        """
        try:
            await self.log(f"Building task: {task[:60]}...", style="action")
            await self.update_task_progress(0.1, "Starting execution")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Builder", f"Starting execution: {task[:50]}...", "build", "action")
                await publish_progress("build", 10.0, "Starting execution")

            # Get the plan_id from context or find the most recent plan
            plan_id = context.get("plan_id")
            if not plan_id:
                plan_id = await self._find_latest_plan(task)

            if not plan_id:
                raise ValueError(f"No plan found for task: {task}")

            await self.update_task_progress(0.2, f"Found plan: {plan_id[:8]}")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Builder", f"Found plan: {plan_id[:8]}", "build", "thought")

            # Check if plan_data is provided directly in context (from CoordinatorAgent)
            plan_data = context.get("plan_data")
            if plan_data and isinstance(plan_data, dict):
                subtasks = plan_data.get("subtasks", [])
                await self.log(f"📋 Using plan data from context: {len(subtasks)} subtasks", style="info")
            else:
                # Check if subtasks are provided directly in context
                direct_subtasks = context.get("subtasks")
                if direct_subtasks and isinstance(direct_subtasks, list):
                    subtasks = direct_subtasks
                    await self.log(f"📋 Using subtasks from context: {len(subtasks)} items", style="info")
                else:
                    # Retrieve subtasks from memory as fallback
                    await self.log(f"📋 No direct context data, retrieving from memory", style="thought")
                    subtasks = await self._get_subtasks_from_plan(plan_id)

            self._total_subtasks = len(subtasks)

            if not subtasks:
                raise ValueError(f"No subtasks found in plan {plan_id}")

            await self.update_task_progress(0.3, f"Retrieved {len(subtasks)} subtasks")
            await self.log(f"Executing {len(subtasks)} subtasks in {self.execution_mode} mode", style="info")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Builder", f"Executing {len(subtasks)} subtasks in {self.execution_mode} mode", "build", "action")
                await publish_progress("build", 30.0, f"Executing {len(subtasks)} subtasks")

            # Execute subtasks based on mode
            execution_results = []
            if self.execution_mode == "parallel" and len(subtasks) > 1:
                execution_results = await self._execute_parallel(subtasks, context)
            else:
                execution_results = await self._execute_sequential(subtasks, context)

            await self.update_task_progress(0.9, f"Executed {len(execution_results)} subtasks")
            
            # Publish to UI
            if UI_ENABLED:
                successful = sum(1 for r in execution_results if r.get("success", False))
                await publish_chat("Builder", f"Completed {successful}/{len(execution_results)} subtasks successfully", "build", "result")
                await publish_progress("build", 90.0, f"Executed {len(execution_results)} subtasks")

            # Create execution summary
            plan_id = context.get("plan_id", "unknown")
            summary = await self._create_execution_summary(task, execution_results, plan_id)

            await self.update_task_progress(1.0, "Build complete")

            await self.log(f"Build completed: {len(execution_results)} subtasks executed", style="success")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Builder", f"✓ Build complete! All subtasks executed", "build", "result")
                await publish_progress("build", 100.0, "Build complete")

            # Store final results
            await self.store_result(
                result={
                    "task": task,
                    "plan_id": plan_id,
                    "execution_results": execution_results,
                    "total_subtasks": len(subtasks),
                    "execution_mode": self.execution_mode,
                    "timestamp": asyncio.get_event_loop().time()
                },
                tags={"execution", "build", "complete"}
            )

            return summary

        except Exception as e:
            await self.handle_error(e, "task execution")
            raise

    async def _find_latest_plan(self, task: str) -> str:
        """
        Find the most recent plan related to the given task.

        Args:
            task: The task to find a plan for

        Returns:
            Plan ID if found, None otherwise
        """
        # Search for recent plans that might be related
        query = MemoryQuery(
            text=task[:50],  # Use first part of task as search term
            memory_type=MemoryType.WORKING,
            limit=5
        )

        results = await self.memory.retrieve(query)

        # Find the most recent plan with matching content
        for item in results:
            if (item.metadata.get("plan_type") == "task_decomposition" and
                task.lower() in item.content.get("original_task", "").lower()):
                return item.id

        return None

    async def _get_subtasks_from_plan(self, plan_id: str) -> List[str]:
        """
        Retrieve subtasks from a specific plan in memory.

        Args:
            plan_id: The plan ID to retrieve subtasks from

        Returns:
            List of subtask strings
        """
        # First try: Use the single item retrieval method that handles JSON parsing
        plan_item = self.memory.get(plan_id)

        if plan_item and isinstance(plan_item.content, dict):
            return plan_item.content.get("subtasks", [])

        # Second try: Search across all memory (shared system)
        from src.core.memory import MemoryQuery

        # Search for the plan by ID in the broader memory system
        plan_query = MemoryQuery(
            text=f"plan_type:task_decomposition",
            memory_type=MemoryType.WORKING,
            limit=10
        )

        plan_results = await self.memory.retrieve(plan_query)

        # Look for the specific plan by ID
        for item in plan_results:
            if item.id == plan_id and isinstance(item.content, dict):
                return item.content.get("subtasks", [])

        await self.log(f"❌ Plan {plan_id[:8]} not found in any memory", style="warning")
        return []

    async def _execute_sequential(self, subtasks: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute subtasks sequentially.

        Args:
            subtasks: List of subtasks to execute
            context: Execution context

        Returns:
            List of execution results
        """
        results = []

        for i, subtask in enumerate(subtasks):
            try:
                await self.log(f"Executing subtask {i+1}/{len(subtasks)}: {subtask[:40]}...", style="action")

                result = await self._execute_subtask(subtask, context, i)
                results.append(result)

                # Update progress
                progress = 0.3 + (0.6 * (i + 1) / len(subtasks))
                await self.update_task_progress(progress, f"Completed {i+1}/{len(subtasks)}")

                # Small delay between subtasks
                await self.sleep(0.2)

            except Exception as e:
                if self.error_recovery:
                    await self.log(f"Subtask {i+1} failed, attempting recovery...", style="warning")
                    # Retry once with error context
                    try:
                        recovery_context = context.copy()
                        recovery_context["retry"] = True
                        recovery_context["original_error"] = str(e)

                        result = await self._execute_subtask(subtask, recovery_context, i)
                        results.append(result)
                        await self.log(f"Subtask {i+1} recovered successfully", style="success")
                    except Exception as retry_error:
                        await self.log(f"❌ Subtask {i+1} failed permanently: {str(retry_error)}", style="error")
                        results.append({
                            "subtask": subtask,
                            "success": False,
                            "error": str(retry_error),
                            "index": i
                        })
                else:
                    await self.log(f"❌ Subtask {i+1} failed: {str(e)}", style="error")
                    results.append({
                        "subtask": subtask,
                        "success": False,
                        "error": str(e),
                        "index": i
                    })

        return results

    async def _execute_parallel(self, subtasks: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute subtasks in parallel with concurrency control.

        Args:
            subtasks: List of subtasks to execute
            context: Execution context

        Returns:
            List of execution results
        """
        await self.log(f"Executing {len(subtasks)} subtasks in parallel (max concurrency: {self.max_concurrency})", style="info")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def execute_with_semaphore(subtask: str, index: int) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self._execute_subtask(subtask, context, index)
                except Exception as e:
                    await self.log(f"Parallel subtask {index+1} failed: {str(e)}", style="error")
                    return {
                        "subtask": subtask,
                        "success": False,
                        "error": str(e),
                        "index": index
                    }

        # Create tasks for parallel execution
        tasks = [
            execute_with_semaphore(subtask, i)
            for i, subtask in enumerate(subtasks)
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                await self.log(f"❌ Parallel subtask {i+1} failed with exception: {str(result)}", style="error")
                processed_results.append({
                    "subtask": subtasks[i],
                    "success": False,
                    "error": str(result),
                    "index": i
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_subtask(self, subtask: str, context: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Execute a single subtask with simulation.

        Args:
            subtask: The subtask to execute
            context: Execution context
            index: Subtask index for tracking

        Returns:
            Execution result dictionary
        """
        # Check for fast mode (skip delays for testing)
        fast_mode = context.get("fast_mode", False)

        # Simulate work based on subtask type
        execution_time = await self._estimate_execution_time(subtask)

        # Skip actual sleep in fast mode
        if not fast_mode:
            await self.sleep(execution_time)

        # Generate mock result based on subtask content
        result = await self._generate_mock_result(subtask, context)

        # Store individual result
        await self.memory.store(
            content=result,
            memory_type=MemoryType.WORKING,
            metadata={
                "agent": self.name,
                "subtask": subtask,
                "subtask_index": index,
                "execution_time": execution_time,
                "fast_mode": fast_mode
            },
            tags={"subtask_result", "execution", f"step_{index+1}"}
        )

        return {
            "subtask": subtask,
            "success": True,
            "result": result,
            "index": index,
            "execution_time": execution_time
        }

    async def _estimate_execution_time(self, subtask: str) -> float:
        """
        Estimate execution time based on subtask complexity.

        Args:
            subtask: The subtask to estimate

        Returns:
            Estimated execution time in seconds
        """
        base_time = 1.0  # Base execution time

        # Adjust based on subtask content
        subtask_lower = subtask.lower()

        if any(keyword in subtask_lower for keyword in ["research", "analyze", "investigate"]):
            base_time = 2.0  # Research takes longer
        elif any(keyword in subtask_lower for keyword in ["implement", "code", "generate"]):
            base_time = 1.5  # Implementation takes medium time
        elif any(keyword in subtask_lower for keyword in ["test", "validate", "review"]):
            base_time = 1.2  # Testing/review is medium
        elif any(keyword in subtask_lower for keyword in ["document", "write"]):
            base_time = 1.8  # Documentation takes time

        # Add some randomness
        import random
        variation = random.uniform(0.5, 1.5)
        return base_time * variation

    async def _generate_mock_result(self, subtask: str, context: Dict[str, Any]) -> str:
        """
        Generate a mock result for the subtask.

        Args:
            subtask: The subtask that was executed
            context: Execution context

        Returns:
            Mock result string
        """
        subtask_lower = subtask.lower()

        # Generate appropriate mock output based on subtask type
        if any(keyword in subtask_lower for keyword in ["code", "implement", "generate"]):
            if "api" in subtask_lower:
                return self._generate_mock_api_code()
            elif "function" in subtask_lower:
                return self._generate_mock_function()
            else:
                return self._generate_mock_code()

        elif any(keyword in subtask_lower for keyword in ["document", "write", "readme"]):
            return self._generate_mock_documentation()

        elif any(keyword in subtask_lower for keyword in ["test", "validate"]):
            return self._generate_mock_tests()

        elif any(keyword in subtask_lower for keyword in ["research", "analyze"]):
            return self._generate_mock_analysis()

        elif any(keyword in subtask_lower for keyword in ["design", "architecture"]):
            return self._generate_mock_design()

        else:
            return f"✅ Completed: {subtask}"

    def _generate_mock_api_code(self) -> str:
        """Generate mock API code."""
        return '''```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task Management API")

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: int = 1

@app.post("/tasks")
async def create_task(task: TaskCreate):
    """Create a new task."""
    return {
        "id": "task_123",
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": "created"
    }
```'''

    def _generate_mock_function(self) -> str:
        """Generate mock function code."""
        return '''```python
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b
```'''

    def _generate_mock_code(self) -> str:
        """Generate generic mock code."""
        return '''```python
# Generated implementation
import asyncio

async def main():
    """Main execution function."""
    print("Task execution started")

    # Implementation logic here
    result = await perform_work()

    print(f"Task completed: {result}")
    return result

if __name__ == "__main__":
    asyncio.run(main())
```'''

    def _generate_mock_documentation(self) -> str:
        """Generate mock documentation."""
        return '''# Project Documentation

## Overview
This project implements a comprehensive task management system with multi-agent orchestration capabilities.

## Features
- Task planning and decomposition
- Parallel execution of subtasks
- Memory-based state management
- Comprehensive error handling

## Usage
```bash
python main.py --task "Build API"
```

## Architecture
The system consists of specialized agents working in coordination to accomplish complex tasks.'''

    def _generate_mock_tests(self) -> str:
        """Generate mock test code."""
        return '''```python
import pytest
from main import fibonacci

def test_fibonacci_basic():
    """Test basic fibonacci functionality."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5

def test_fibonacci_edge_cases():
    """Test edge cases."""
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765

@pytest.mark.asyncio
async def test_async_functionality():
    """Test async operations."""
    # Async test implementation
    assert True
```'''

    def _generate_mock_analysis(self) -> str:
        """Generate mock analysis results."""
        return '''# Analysis Results

## Summary
The analysis reveals several key findings:

### Performance Metrics
- Execution Time: 2.3 seconds average
- Memory Usage: 45MB peak
- Success Rate: 94.2%

### Key Insights
1. **Efficiency**: The parallel execution mode provides 40% performance improvement
2. **Reliability**: Error recovery mechanisms successfully handle 87% of failures
3. **Scalability**: System handles up to 10 concurrent subtasks effectively

### Recommendations
- Implement caching for frequently accessed subtasks
- Add monitoring dashboard for real-time metrics
- Consider distributed execution for large-scale tasks

## Conclusion
The implementation demonstrates robust performance and reliable operation.'''

    def _generate_mock_design(self) -> str:
        """Generate mock design documentation."""
        return '''# System Design

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Planner       │───▶│   Builder       │───▶│   Reviewer      │
│                 │    │                 │    │                 │
│ - Task Analysis │    │ - Code Gen      │    │ - Quality Check │
│ - Subtask Plan  │    │ - Execution     │    │ - Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Memory        │
                    │                 │
                    │ - Plans         │
                    │ - Results       │
                    │ - Context       │
                    └─────────────────┘
```

## Component Responsibilities
- **Planner**: Decomposes complex tasks into manageable subtasks
- **Builder**: Executes subtasks and generates implementations
- **Reviewer**: Validates results and provides feedback
- **Memory**: Maintains persistent state and context

## Design Patterns
- Observer pattern for inter-agent communication
- Strategy pattern for different execution modes
- Factory pattern for agent instantiation'''

    async def _create_execution_summary(self, task: str, results: List[Dict[str, Any]], plan_id: str) -> str:
        """
        Create a formatted summary of execution results.

        Args:
            task: The original task
            results: Execution results
            plan_id: The plan that was executed

        Returns:
            Formatted summary string
        """
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful

        summary = f"""
🔨 **Task Execution Summary**

**Original Task:** {task}

**Plan ID:** {plan_id[:8]}

**Execution Results:**
- Total Subtasks: {len(results)}
- Successful: {successful}
- Failed: {failed}
- Success Rate: {successful / len(results) * 100:.1f}%
- Execution Mode: {self.execution_mode}

**Performance Metrics:**
- Average Execution Time: {sum(r.get('execution_time', 0) for r in results if r.get('success')) / max(successful, 1):.2f} seconds
- Total Execution Time: {sum(r.get('execution_time', 0) for r in results):.2f} seconds

**Detailed Results:**
"""

        for i, result in enumerate(results, 1):
            status = "✅" if result.get("success") else "❌"
            summary += f"{i:2d}. {status} {result['subtask'][:50]}..."
            if not result.get("success"):
                summary += f" (Error: {result.get('error', 'Unknown')})"
            summary += "\n"

        summary += "\n✅ Build phase complete. Results stored in memory for review."

        return summary.strip()

    async def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent execution history from memory.

        Args:
            limit: Maximum number of executions to retrieve

        Returns:
            List of recent execution results
        """
        # Search by tags since execution results are stored with "execution" tag
        query = MemoryQuery(
            memory_type=MemoryType.WORKING,
            limit=limit * 2  # Get more to filter
        )

        results = await self.memory.retrieve(query)

        # Filter to only execution results from this agent
        filtered_results = []
        for item in results:
            # Check if this has the "execution" tag and is from this agent
            if (item.metadata.get("agent") == self.name and
                "execution" in item.tags):
                filtered_results.append(item)

        # Sort by timestamp (newest first)
        filtered_results.sort(key=lambda x: x.created_at, reverse=True)

        return [
            {
                "id": item.id,
                "content": item.content,
                "metadata": item.metadata,
                "created_at": item.created_at.isoformat()
            }
            for item in filtered_results[:limit]
        ]
