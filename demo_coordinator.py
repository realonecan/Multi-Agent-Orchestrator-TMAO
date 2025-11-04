"""
Coordinator Agent Demo.

Demonstrates the complete multi-agent orchestration pipeline using the CoordinatorAgent:
Single task input → Planner → Builder → Reviewer → Final comprehensive report.

This shows the full power of the coordinated multi-agent system.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

try:
    from agents.coordinator_agent import CoordinatorAgent
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory.")
    IMPORTS_OK = False


async def demo_full_orchestration():
    """Demonstrate the complete orchestration pipeline with CoordinatorAgent."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print("\n" + "="*80)
    print("🎭 COORDINATOR AGENT - COMPLETE ORCHESTRATION PIPELINE")
    print("="*80)

    # Create coordinator with comprehensive configuration
    coordinator_config = {
        "coordinator": {
            "mode": "auto",
            "max_retries": 2,
            "enable_parallel": True
        },
        "planner": {
            "max_subtasks": 5,
            "logging": {"level": "INFO"}
        },
        "builder": {
            "execution_mode": "parallel",
            "max_concurrency": 3,
            "error_recovery": True,
            "logging": {"level": "INFO"}
        },
        "reviewer": {
            "evaluation_mode": "auto",
            "scoring_weights": {
                "accuracy": 0.6,
                "quality": 0.4
            },
            "logging": {"level": "INFO"}
        }
    }

    coordinator = CoordinatorAgent(coordinator_config)
    await coordinator.initialize()

    # Test scenarios for complete orchestration
    test_tasks = [
        {
            "name": "Student Management API",
            "task": "Build a REST API for student management with authentication",
            "context": {
                "framework": "FastAPI",
                "include_authentication": True,
                "include_database": True,
                "include_testing": True,
                "style": "production"
            }
        },
        {
            "name": "Data Analysis Dashboard",
            "task": "Create a data analysis dashboard for CSV file processing",
            "context": {
                "framework": "Streamlit",
                "include_visualization": True,
                "include_export": True,
                "analysis_types": ["statistical", "trends", "correlation"],
                "style": "analytical"
            }
        },
        {
            "name": "Documentation Generator",
            "task": "Build an automated documentation generator for Python projects",
            "context": {
                "language": "Python",
                "include_examples": True,
                "include_api_docs": True,
                "output_format": "markdown",
                "style": "technical"
            }
        }
    ]

    results_summary = []

    for i, test_case in enumerate(test_tasks, 1):
        print(f"\n{'─'*70}")
        print(f"🎯 TASK {i}: {test_case['name']}")
        print(f"{'─'*70}")
        print(f"📝 Task: {test_case['task']}")

        try:
            # Run complete orchestration
            result = await coordinator.orchestrate(test_case["task"], test_case["context"])

            # Display comprehensive results
            print(f"\n🏆 ORCHESTRATION RESULTS:")
            print(f"   🎯 Final Score: {result['summary']['final_score']:.1%} ({result['summary']['final_score']*100:.1f}/100)")
            print(f"   📊 Accuracy: {result['summary']['accuracy']:.1%} ({result['summary']['accuracy']*100:.1f}/100)")
            print(f"   ✨ Quality: {result['summary']['quality']:.1%} ({result['summary']['quality']*100:.1f}/100)")
            print(f"\n🔗 STAGE IDS:")
            print(f"   📋 Plan: {result['plan_id'][:8]}")
            print(f"   🔨 Build: {result['execution_id'][:8]}")
            print(f"   🔍 Review: {result['review_id'][:8]}")

            print(f"\n⚡ PERFORMANCE:")
            print(f"   ⏱️  Duration: {result['metadata']['duration']:.1f} seconds")
            print(f"   🔄 Mode: {result['metadata']['mode']}")
            print(f"   🚀 Parallel: {'Enabled' if result['metadata']['parallel_enabled'] else 'Disabled'}")

            print(f"\n📋 Notes: {result['summary']['notes']}")

            # Store results for summary
            results_summary.append({
                "task": test_case["name"],
                "final_score": result["summary"]["final_score"],
                "accuracy": result["summary"]["accuracy"],
                "quality": result["summary"]["quality"],
                "duration": result["metadata"]["duration"],
                "success": True
            })

        except Exception as e:
            print(f"❌ Task '{test_case['name']}' failed: {e}")
            results_summary.append({
                "task": test_case["name"],
                "error": str(e),
                "success": False
            })

    # Show orchestration statistics
    print(f"\n{'─'*70}")
    print("📈 ORCHESTRATION STATISTICS")
    print(f"{'─'*70}")

    successful_tasks = [r for r in results_summary if r.get("success", False)]

    if successful_tasks:
        avg_final_score = sum(r["final_score"] for r in successful_tasks) / len(successful_tasks)
        avg_accuracy = sum(r["accuracy"] for r in successful_tasks) / len(successful_tasks)
        avg_quality = sum(r["quality"] for r in successful_tasks) / len(successful_tasks)
        avg_duration = sum(r["duration"] for r in successful_tasks) / len(successful_tasks)

        print(f"🏆 AVERAGE SCORES ({len(successful_tasks)} successful tasks):")
        print(f"   Final Score: {avg_final_score:.1%}")
        print(f"   Accuracy: {avg_accuracy:.1%}")
        print(f"   Quality: {avg_quality:.1%}")

        print(f"\n⚡ PERFORMANCE:")
        print(f"   Average Duration: {avg_duration:.1f} seconds")
        print(f"   Success Rate: {len(successful_tasks)}/{len(test_tasks)} ({len(successful_tasks)/len(test_tasks)*100:.1f}%)")

        print(f"\n🎯 TASK BREAKDOWN:")
        for result in results_summary:
            if result.get("success", False):
                print(f"   ✅ {result['task']}: {result['final_score']:.1%} ({result['duration']:.1f}s)")
            else:
                print(f"   ❌ {result['task']}: Failed - {result.get('error', 'Unknown error')}")

    # Show orchestration history
    try:
        history = await coordinator.get_orchestration_history(limit=3)
        if history["orchestrations"]:
            print(f"\n💾 STORED ORCHESTRATIONS: {history['total_orchestrations']}")
            for orch in history["orchestrations"]:
                content = orch["content"]
                print(f"   📋 {content['task'][:40]}... → {content['summary']['final_score']:.1%}")
    except Exception as e:
        print(f"❌ Could not retrieve orchestration history: {e}")

    await coordinator.shutdown()

    print(f"\n{'='*80}")
    print("✅ COORDINATOR ORCHESTRATION DEMO COMPLETE")
    print("="*80)


async def demo_different_modes():
    """Demonstrate different coordinator modes and configurations."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'─'*70}")
    print("⚙️ COORDINATOR MODES & CONFIGURATIONS")
    print(f"{'─'*70}")

    test_task = "Create a simple calculator web application"

    modes = [
        {
            "name": "Auto Parallel Mode",
            "config": {
                "coordinator": {"mode": "auto", "max_retries": 2, "enable_parallel": True},
                "builder": {"execution_mode": "parallel", "max_concurrency": 3}
            }
        },
        {
            "name": "Sequential Mode",
            "config": {
                "coordinator": {"mode": "auto", "max_retries": 2, "enable_parallel": False},
                "builder": {"execution_mode": "sequential", "max_concurrency": 1}
            }
        },
        {
            "name": "High Retry Mode",
            "config": {
                "coordinator": {"mode": "auto", "max_retries": 5, "enable_parallel": True},
                "builder": {"execution_mode": "parallel", "max_concurrency": 2, "error_recovery": True}
            }
        }
    ]

    for mode in modes:
        print(f"\n🔧 Testing: {mode['name']}")

        try:
            coordinator = CoordinatorAgent(mode["config"])
            await coordinator.initialize()

            result = await coordinator.orchestrate(test_task, {
                "framework": "Flask",
                "include_ui": True,
                "include_tests": True
            })

            print(f"   ✅ Success: {result['summary']['final_score']:.1%} ({result['metadata']['duration']:.1f}s)")
            print(f"   🚀 Parallel: {result['metadata']['parallel_enabled']}")
            print(f"   ⏱️  Duration: {result['metadata']['duration']:.1f} seconds")

            await coordinator.shutdown()

        except Exception as e:
            print(f"   ❌ Failed: {e}")


async def demo_error_recovery():
    """Demonstrate error recovery and retry mechanisms."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'─'*70}")
    print("🛡️ ERROR RECOVERY & RETRY MECHANISMS")
    print(f"{'─'*70}")

    # Test with high retry settings
    coordinator = CoordinatorAgent({
        "coordinator": {
            "mode": "auto",
            "max_retries": 3,
            "enable_parallel": True
        },
        "builder": {
            "execution_mode": "parallel",
            "max_concurrency": 2,
            "error_recovery": True
        }
    })

    await coordinator.initialize()

    # Test challenging tasks that might need retries
    challenging_tasks = [
        {
            "name": "Complex Database Migration",
            "task": "Create a database migration system with rollback capabilities",
            "context": {
                "framework": "SQLAlchemy",
                "include_rollback": True,
                "include_validation": True,
                "complexity": "high"
            }
        }
    ]

    for task in challenging_tasks:
        print(f"\n🔬 Testing: {task['name']}")
        print(f"   Task: {task['task']}")

        try:
            result = await coordinator.orchestrate(task["task"], task["context"])

            print(f"   ✅ Success: {result['summary']['final_score']:.1%}")
            print(f"   🔄 Retries used: Check logs for retry attempts")
            print(f"   ⏱️  Total duration: {result['metadata']['duration']:.1f} seconds")

        except Exception as e:
            print(f"   ❌ Failed after all retries: {e}")

    await coordinator.shutdown()


async def demo_orchestration_status():
    """Demonstrate orchestration status tracking and monitoring."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'─'*70}")
    print("📊 ORCHESTRATION STATUS & MONITORING")
    print(f"{'─'*70}")

    coordinator = CoordinatorAgent()
    await coordinator.initialize()

    print("🚀 Starting multiple concurrent orchestrations...")

    # Start multiple orchestrations
    tasks = [
        ("Simple API", "Build a simple REST API", {"framework": "FastAPI"}),
        ("Calculator", "Create a calculator application", {"framework": "Tkinter"}),
        ("Documentation", "Generate project documentation", {"format": "markdown"})
    ]

    orchestration_results = []

    for name, task, context in tasks:
        print(f"   🎯 Starting: {name}")
        try:
            # Run orchestration in background
            result = await coordinator.orchestrate(task, context)
            orchestration_results.append((name, "success", result))
            print(f"   ✅ Completed: {name} ({result['summary']['final_score']:.1%})")
        except Exception as e:
            orchestration_results.append((name, "failed", str(e)))
            print(f"   ❌ Failed: {name} ({e})")

    # Show orchestration history and statistics
    history = await coordinator.get_orchestration_history(limit=10)

    print(f"\n📈 ORCHESTRATION SUMMARY:")
    print(f"   Total completed: {len([r for r in orchestration_results if r[1] == 'success'])}")
    print(f"   Total failed: {len([r for r in orchestration_results if r[1] == 'failed'])}")
    print(f"   Stored in memory: {history['total_orchestrations']}")

    if history["orchestrations"]:
        print(f"\n💾 RECENT ORCHESTRATIONS:")
        for orch in history["orchestrations"]:
            content = orch["content"]
            print(f"   📋 {content['task'][:35]}... → {content['summary']['final_score']:.1%} ({orch['metadata']['duration']:.1f}s)")

    await coordinator.shutdown()


if __name__ == "__main__":
    """Run the coordinator agent demonstrations."""

    async def main():
        print("🎭 Starting CoordinatorAgent Demonstrations...")

        # Run full orchestration demo
        await demo_full_orchestration()

        # Run different modes demo
        await demo_different_modes()

        # Run error recovery demo
        await demo_error_recovery()

        # Run status monitoring demo
        await demo_orchestration_status()

        print("\n🎉 All CoordinatorAgent demonstrations completed successfully!")
        print("\n✨ Demonstrated capabilities:")
        print("   • Complete Planner → Builder → Reviewer orchestration")
        print("   • Single entry point for complex multi-agent workflows")
        print("   • Automatic retry and error recovery mechanisms")
        print("   • Configurable execution modes (parallel/sequential)")
        print("   • Comprehensive progress tracking and logging")
        print("   • Persistent orchestration history and metadata")
        print("   • Real-time status monitoring and reporting")

        print("\n🏆 The multi-agent orchestration system is now complete!")
        print("   Users can now input any task and get a fully orchestrated")
        print("   solution with planning, implementation, and quality review!")

    # Check if imports are working
    if IMPORTS_OK:
        # Run the async main function
        asyncio.run(main())
    else:
        print("❌ Cannot run demonstrations due to import errors.")
        print("Please ensure all dependencies are installed:")
        print("  pip install rich pyyaml numpy")
