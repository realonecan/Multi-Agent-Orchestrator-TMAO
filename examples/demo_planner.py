"""
Planner Agent Demo.

Demonstrates how the PlannerAgent works by processing various types of tasks
and showing the planning and decomposition capabilities.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

try:
    from agents.planner_agent import PlannerAgent
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory.")
    IMPORTS_OK = False


async def demo_planner_agent():
    """Demonstrate the PlannerAgent functionality."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    # Create planner agent with configuration
    config = {
        "capabilities": ["planning", "task_decomposition", "optimization"],
        "max_subtasks": 10,
        "include_quality_checks": True
    }

    planner = PlannerAgent(config)
    await planner.initialize()

    print("\n" + "="*60)
    print("🧠 PLANNER AGENT DEMONSTRATION")
    print("="*60)

    # Test cases with different types of tasks
    test_tasks = [
        {
            "task": "Build a Python REST API for a task management system",
            "context": {
                "include_testing": True,
                "include_documentation": True,
                "framework": "FastAPI"
            }
        },
        {
            "task": "Research machine learning algorithms for natural language processing",
            "context": {
                "deadline": "2025-02-01",
                "focus_areas": ["transformers", "sequence models", "attention mechanisms"]
            }
        },
        {
            "task": "Create comprehensive documentation for a microservices architecture",
            "context": {
                "audience": "developers",
                "format": "markdown",
                "include_diagrams": True
            }
        }
    ]

    for i, test_case in enumerate(test_tasks, 1):
        print(f"\n{'-'*50}")
        print(f"DEMO {i}: {test_case['task'][:50]}...")
        print(f"{'-'*50}")

        try:
            # Process the task
            result = await planner.process_task(
                task=test_case["task"],
                context=test_case["context"]
            )

            print(f"\n📋 PLANNING RESULT:\n{result}")

        except Exception as e:
            print(f"❌ Demo task {i} failed: {e}")

        # Show recent plans
        if i == 1:  # After first task
            try:
                recent_plans = await planner.get_recent_plans(limit=1)
                if recent_plans:
                    print(f"\n💾 STORED IN MEMORY: {recent_plans[0]['id'][:8]}")
                    print(f"   Task Type: {recent_plans[0]['content']['task_type']}")
                    print(f"   Subtasks: {recent_plans[0]['content']['subtask_count']}")
            except Exception as e:
                print(f"❌ Could not retrieve recent plans: {e}")

    print(f"\n{'-'*50}")
    print("🧪 OPTIMIZATION DEMO")
    print(f"{'-'*50}")

    # Demonstrate plan optimization
    try:
        recent_plans = await planner.get_recent_plans(limit=1)
        if recent_plans:
            plan_id = recent_plans[0]["id"]
            print(f"Optimizing plan {plan_id[:8]}...")

            # Test different optimization goals
            optimization_goals = ["speed", "quality", "reliability"]

            for goal in optimization_goals:
                try:
                    optimized_result = await planner.optimize_plan(plan_id, goal)
                    print(f"\n🎯 {goal.upper()} OPTIMIZATION:")
                    print(optimized_result)

                except Exception as e:
                    print(f"❌ Optimization for {goal} failed: {e}")
        else:
            print("No plans available for optimization demo.")
    except Exception as e:
        print(f"❌ Optimization demo failed: {e}")

    # Cleanup
    await planner.shutdown()

    print(f"\n{'='*60}")
    print("✅ PLANNER AGENT DEMO COMPLETE")
    print("="*60)


async def demo_task_classification():
    """Demonstrate task classification capabilities."""

    planner = PlannerAgent()
    await planner.initialize()

    print(f"\n{'-'*50}")
    print("🧠 TASK CLASSIFICATION DEMO")
    print(f"{'-'*50}")

    test_tasks = [
        "Write a Python function to calculate fibonacci numbers",
        "Research the latest developments in quantum computing",
        "Create a comprehensive README for my open source project",
        "Design a database schema for an e-commerce platform",
        "Write unit tests for the authentication module"
    ]

    for task in test_tasks:
        task_type = await planner._classify_task(task)
        print(f"📋 Task: {task[:50]}...")
        print(f"   → Classified as: {task_type}")
        print()

    await planner.shutdown()


if __name__ == "__main__":
    """Run the planner agent demonstrations."""

    async def main():
        print("🚀 Starting PlannerAgent Demonstrations...")

        # Run the main demo
        await demo_planner_agent()

        # Run classification demo
        await demo_task_classification()

        print("\n🎉 All demonstrations completed successfully!")

    # Check if imports are working
    if IMPORTS_OK:
        # Run the async main function
        asyncio.run(main())
    else:
        print("❌ Cannot run demonstrations due to import errors.")
        print("Please ensure all dependencies are installed:")
        print("  pip install rich pyyaml numpy")
