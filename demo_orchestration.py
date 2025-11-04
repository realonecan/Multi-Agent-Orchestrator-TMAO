"""
Complete Orchestration Demo.

Demonstrates the full multi-agent workflow: Planner creates a plan,
Builder executes the plan, showing the complete orchestration pipeline.

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
    from agents.builder_agent import BuilderAgent
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory.")
    IMPORTS_OK = False


async def demo_full_orchestration():
    """Demonstrate the complete orchestration workflow."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print("\n" + "="*70)
    print("🤖 COMPLETE MULTI-AGENT ORCHESTRATION DEMONSTRATION")
    print("="*70)

    # Create agents with comprehensive configuration
    planner_config = {
        "capabilities": ["planning", "task_decomposition", "optimization"],
        "max_subtasks": 6,
        "logging": {"level": "INFO"}
    }

    builder_config = {
        "capabilities": ["coding", "execution", "validation"],
        "execution_mode": "parallel",
        "max_concurrency": 3,
        "error_recovery": True,
        "logging": {"level": "INFO"}
    }

    planner = PlannerAgent(planner_config)
    builder = BuilderAgent(builder_config)

    await planner.initialize()
    await builder.initialize()

    # Comprehensive test scenarios
    scenarios = [
        {
            "name": "Web API Development",
            "task": "Build a REST API for user management with authentication",
            "planner_context": {
                "include_testing": True,
                "include_documentation": True,
                "framework": "FastAPI",
                "database": "PostgreSQL"
            },
            "builder_context": {
                "language": "Python",
                "framework": "FastAPI",
                "style": "production"
            }
        },
        {
            "name": "Data Analysis System",
            "task": "Create a data analysis pipeline for CSV processing",
            "planner_context": {
                "include_visualization": True,
                "output_format": "JSON",
                "analysis_types": ["statistical", "trends"]
            },
            "builder_context": {
                "language": "Python",
                "libraries": ["pandas", "matplotlib"],
                "style": "analytical"
            }
        }
    ]

    for scenario in scenarios:
        print(f"\n{'-'*60}")
        print(f"🎯 SCENARIO: {scenario['name']}")
        print(f"{'-'*60}")
        print(f"Task: {scenario['task']}")

        try:
            # Phase 1: Planning
            print(f"\n📋 PHASE 1: PLANNING")
            print(f"{'─'*40}")

            plan_result = await planner.process_task(
                task=scenario["task"],
                context=scenario["planner_context"]
            )

            print(f"\n{plan_result}")

            # Extract plan_id from planner's memory (simulated)
            recent_plans = await planner.get_recent_plans(limit=1)
            plan_id = recent_plans[0]["id"] if recent_plans else "demo_plan_001"

            # Phase 2: Building
            print(f"\n🔨 PHASE 2: BUILDING")
            print(f"{'─'*40}")

            build_result = await builder.process_task(
                task=scenario["task"],
                context={
                    "plan_id": plan_id,
                    "execution_mode": "parallel",
                    **scenario["builder_context"]
                }
            )

            print(f"\n{build_result}")

        except Exception as e:
            print(f"❌ Scenario '{scenario['name']}' failed: {e}")

    # Show execution history
    print(f"\n{'-'*60}")
    print("📊 EXECUTION SUMMARY")
    print(f"{'-'*60}")

    try:
        planner_history = await planner.get_recent_plans(limit=2)
        if planner_history:
            print(f"📋 Planner created {len(planner_history)} plans:")
            for plan in planner_history:
                print(f"   • {plan['content']['task_type']} - {len(plan['content']['subtasks'])} subtasks")

        builder_history = await builder.get_execution_history(limit=2)
        if builder_history:
            print(f"\n🔨 Builder executed {len(builder_history)} tasks:")
            for execution in builder_history:
                content = execution['content']
                if isinstance(content, dict) and 'execution_results' in content:
                    successful = sum(1 for r in content['execution_results'] if r.get('success', False))
                    total = len(content['execution_results'])
                    print(f"   • {successful}/{total} subtasks successful")

    except Exception as e:
        print(f"❌ Could not retrieve history: {e}")

    # Cleanup
    await planner.shutdown()
    await builder.shutdown()

    print(f"\n{'='*70}")
    print("✅ COMPLETE ORCHESTRATION DEMO FINISHED")
    print("="*70)


async def demo_different_execution_modes():
    """Demonstrate different execution modes and configurations."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'-'*60}")
    print("⚡ EXECUTION MODES COMPARISON")
    print(f"{'-'*60}")

    modes = ["sequential", "parallel"]
    mock_subtasks = [
        "Analyze requirements and constraints",
        "Design system architecture",
        "Implement core functionality",
        "Add error handling and validation",
        "Create comprehensive tests",
        "Write documentation"
    ]

    for mode in modes:
        print(f"\n🔧 Testing {mode.upper()} mode:")

        config = {
            "execution_mode": mode,
            "max_concurrency": 3 if mode == "parallel" else 1,
            "error_recovery": True
        }

        builder = BuilderAgent(config)
        await builder.initialize()

        # Execute with timing
        start_time = asyncio.get_event_loop().time()

        if mode == "parallel":
            results = await builder._execute_parallel(mock_subtasks, {"mode_test": True})
        else:
            results = await builder._execute_sequential(mock_subtasks, {"mode_test": True})

        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time

        successful = sum(1 for r in results if r.get("success", False))
        avg_time = sum(r.get('execution_time', 0) for r in results) / len(results)

        print(f"   ✅ {successful}/{len(results)} completed")
        print(f"   ⏱️  Total time: {total_time:.2f}s")
        print(f"   📈 Average per subtask: {avg_time:.2f}s")

        await builder.shutdown()


async def demo_error_scenarios():
    """Demonstrate error handling and recovery."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'-'*60}")
    print("🛡️ ERROR HANDLING DEMONSTRATION")
    print(f"{'-'*60}")

    # Test error recovery
    builder = BuilderAgent({
        "execution_mode": "sequential",
        "error_recovery": True,
        "max_concurrency": 1
    })

    await builder.initialize()

    # Mix of normal and problematic subtasks
    test_subtasks = [
        "Create API endpoints",  # Should succeed
        "Execute impossible operation",  # Should fail but recover
        "Generate documentation",  # Should succeed
        "Run invalid command",  # Should fail
        "Validate implementation"  # Should succeed
    ]

    print(f"Testing error recovery with {len(test_subtasks)} subtasks...")

    results = await builder._execute_sequential(test_subtasks, {"error_test": True})

    successful = sum(1 for r in results if r.get("success", False))
    failed = len(results) - successful

    print(f"\n📊 Error Recovery Results:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   🛡️ Recovery Rate: {successful / len(results) * 100:.1f}%")

    await builder.shutdown()


if __name__ == "__main__":
    """Run the complete orchestration demonstrations."""

    async def main():
        print("🚀 Starting Complete Multi-Agent Orchestration...")

        # Run full orchestration demo
        await demo_full_orchestration()

        # Run execution modes comparison
        await demo_different_execution_modes()

        # Run error handling demo
        await demo_error_scenarios()

        print("\n🎉 All orchestration demonstrations completed successfully!")
        print("\n✨ The system demonstrates:")
        print("   • Planner creates structured task breakdowns")
        print("   • Builder executes plans with parallel/sequential modes")
        print("   • Memory system maintains context across agents")
        print("   • Error recovery ensures robust operation")
        print("   • Progress tracking provides visibility")

    # Check if imports are working
    if IMPORTS_OK:
        # Run the async main function
        asyncio.run(main())
    else:
        print("❌ Cannot run demonstrations due to import errors.")
        print("Please ensure all dependencies are installed:")
        print("  pip install rich pyyaml numpy")
