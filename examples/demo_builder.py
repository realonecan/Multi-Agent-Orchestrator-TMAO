"""
Builder Agent Demo.

Demonstrates how the BuilderAgent executes planned subtasks and generates
mock implementations for various types of tasks.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

try:
    from agents.builder_agent import BuilderAgent
    from agents.planner_agent import PlannerAgent
    from core.memory import MemoryManager
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory.")
    IMPORTS_OK = False


async def demo_builder_with_planner():
    """Demonstrate BuilderAgent working with PlannerAgent."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print("\n" + "="*60)
    print("🔨 BUILDER AGENT + PLANNER DEMONSTRATION")
    print("="*60)

    # Create agents
    planner_config = {
        "capabilities": ["planning", "task_decomposition"],
        "max_subtasks": 5
    }

    builder_config = {
        "capabilities": ["coding", "execution", "validation"],
        "execution_mode": "sequential",
        "max_concurrency": 2,
        "error_recovery": True
    }

    # Create shared memory for both agents
    shared_memory = MemoryManager()

    planner = PlannerAgent(planner_config, shared_memory=shared_memory)
    builder = BuilderAgent(builder_config, shared_memory=shared_memory)

    await planner.initialize()
    await builder.initialize()

    # Test tasks for planning and building
    test_tasks = [
        {
            "task": "Build a REST API for user management",
            "context": {
                "framework": "FastAPI",
                "include_authentication": True,
                "include_database": True
            }
        },
        {
            "task": "Create a data analysis script for CSV processing",
            "context": {
                "language": "Python",
                "include_visualization": True,
                "output_format": "JSON"
            }
        }
    ]

    for i, test_case in enumerate(test_tasks, 1):
        print(f"\n{'-'*50}")
        print(f"DEMO {i}: {test_case['task'][:50]}...")
        print(f"{'-'*50}")

        try:
            # Step 1: Planning phase
            print("📋 PLANNING PHASE:")
            plan_result = await planner.process_task(
                task=test_case["task"],
                context=test_case["context"]
            )

            print(plan_result)

            # Get the actual plan ID from planner
            recent_plans = await planner.get_recent_plans(limit=1)
            if recent_plans:
                plan_id = recent_plans[0]["id"]
                print(f"📋 Retrieved plan: {plan_id[:8]}")
            else:
                print("❌ No plan found, skipping building phase")
                continue

            # Step 2: Building phase
            print("\n🔨 BUILDING PHASE:")
            build_result = await builder.process_task(
                task=test_case["task"],
                context={
                    "plan_id": plan_id,
                    "execution_mode": "sequential",
                    **test_case["context"]
                }
            )

            print(build_result)

        except Exception as e:
            print(f"❌ Demo {i} failed: {e}")

    # Cleanup
    await planner.shutdown()
    await builder.shutdown()

    print(f"\n{'='*60}")
    print("✅ BUILDER + PLANNER DEMO COMPLETE")
    print("="*60)


async def demo_builder_standalone():
    """Demonstrate BuilderAgent standalone functionality."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'-'*50}")
    print("🔨 BUILDER AGENT STANDALONE DEMO")
    print(f"{'-'*50}")

    # Create shared memory for standalone demo
    shared_memory = MemoryManager()

    # Create builder with parallel execution
    config = {
        "capabilities": ["coding", "execution", "validation"],
        "execution_mode": "parallel",
        "max_concurrency": 3,
        "error_recovery": True
    }

    builder = BuilderAgent(config, shared_memory=shared_memory)
    await builder.initialize()

    # Mock subtasks for execution
    mock_subtasks = [
        "Design API endpoints and data structures",
        "Implement user authentication system",
        "Create database models and relationships",
        "Add input validation and error handling",
        "Write comprehensive unit tests"
    ]

    print(f"Executing {len(mock_subtasks)} subtasks in parallel mode...")

    # Execute subtasks manually (simulating what would come from planner)
    context = {"framework": "FastAPI", "language": "Python"}
    results = await builder._execute_parallel(mock_subtasks, context)

    # Show results
    successful = sum(1 for r in results if r.get("success", False))
    print(f"\n📊 Execution Results: {successful}/{len(results)} successful")

    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success") else "❌"
        print(f"  {i}. {status} {result['subtask'][:40]}... ({result.get('execution_time', 0):.2f}s)")
        if not result.get("success"):
            print(f"     Error: {result.get('error', 'Unknown')}")

    # Show execution history
    try:
        history = await builder.get_execution_history(limit=1)
        if history:
            print(f"\n💾 Stored in memory: {history[0]['id'][:8]}")
            print(f"   Results: {len(history[0]['content']['execution_results'])} subtasks")
    except Exception as e:
        print(f"❌ Could not retrieve execution history: {e}")

    await builder.shutdown()


async def demo_execution_modes():
    """Demonstrate different execution modes."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'-'*50}")
    print("⚡ EXECUTION MODES DEMONSTRATION")
    print(f"{'-'*50}")

    # Test both execution modes
    modes = ["sequential", "parallel"]
    mock_subtasks = [
        "Analyze project requirements",
        "Design system architecture",
        "Implement core functionality",
        "Add testing and validation"
    ]

    for mode in modes:
        print(f"\n🔧 Testing {mode.upper()} mode:")

        # Create shared memory for each mode test
        shared_memory = MemoryManager()

        config = {
            "execution_mode": mode,
            "max_concurrency": 2,
            "error_recovery": True
        }

        builder = BuilderAgent(config, shared_memory=shared_memory)
        await builder.initialize()

        context = {"mode_demo": True}
        results = []

        if mode == "parallel":
            results = await builder._execute_parallel(mock_subtasks, context)
        else:
            results = await builder._execute_sequential(mock_subtasks, context)

        successful = sum(1 for r in results if r.get("success", False))
        total_time = sum(r.get('execution_time', 0) for r in results)

        print(f"   ✅ {successful}/{len(results)} completed in {total_time:.2f} seconds")

        await builder.shutdown()


async def demo_error_recovery():
    """Demonstrate error recovery functionality."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'-'*50}")
    print("🛡️ ERROR RECOVERY DEMONSTRATION")
    print(f"{'-'*50}")

    # Create shared memory for error recovery test
    shared_memory = MemoryManager()

    # Test error recovery
    builder = BuilderAgent({
        "execution_mode": "sequential",
        "error_recovery": True,
        "max_concurrency": 1
    }, shared_memory=shared_memory)

    await builder.initialize()

    # Mock a subtask that will fail
    failing_subtask = "Execute impossible operation that will fail"

    print(f"Testing error recovery with: {failing_subtask}")

    try:
        result = await builder._execute_subtask(failing_subtask, {}, 0)
        print(f"Unexpected success: {result}")
    except Exception as e:
        print(f"Expected error occurred: {e}")
        print("Error recovery should handle this gracefully in full execution.")

    await builder.shutdown()


if __name__ == "__main__":
    """Run the builder agent demonstrations."""

    async def main():
        print("🚀 Starting BuilderAgent Demonstrations...")

        # Run integrated demo
        await demo_builder_with_planner()

        # Run standalone demo
        await demo_builder_standalone()

        # Run execution modes demo
        await demo_execution_modes()

        # Run error recovery demo
        await demo_error_recovery()

        print("\n🎉 All BuilderAgent demonstrations completed successfully!")

    # Check if imports are working
    if IMPORTS_OK:
        # Run the async main function
        asyncio.run(main())
    else:
        print("❌ Cannot run demonstrations due to import errors.")
        print("Please ensure all dependencies are installed:")
        print("  pip install rich pyyaml numpy")
