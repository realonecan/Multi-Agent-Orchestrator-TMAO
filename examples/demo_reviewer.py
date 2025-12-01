"""
Reviewer Agent Demo.

Demonstrates the complete multi-agent orchestration pipeline:
Planner creates plan → Builder executes → Reviewer evaluates.

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
    from agents.reviewer_agent import ReviewerAgent
    from core.memory import MemoryType, MemoryManager
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory.")
    IMPORTS_OK = False


async def demo_complete_pipeline():
    """Demonstrate the complete Planner → Builder → Reviewer pipeline."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print("\n" + "="*70)
    print("🎭 COMPLETE MULTI-AGENT ORCHESTRATION PIPELINE")
    print("="*70)

    # Create all agents with comprehensive configuration
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

    reviewer_config = {
        "capabilities": ["review", "analysis", "optimization"],
        "reviewer": {
            "evaluation_mode": "auto",
            "scoring_weights": {
                "accuracy": 0.6,
                "quality": 0.4
            }
        },
        "logging": {"level": "INFO"}
    }

    # Create shared memory for all agents
    shared_memory = MemoryManager()

    planner = PlannerAgent(planner_config, shared_memory=shared_memory)
    builder = BuilderAgent(builder_config, shared_memory=shared_memory)
    reviewer = ReviewerAgent(reviewer_config, shared_memory=shared_memory)

    await planner.initialize()
    await builder.initialize()
    await reviewer.initialize()

    # Test scenarios for complete pipeline
    scenarios = [
        {
            "name": "REST API Development",
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
            "name": "Data Analysis Script",
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
        print(f"\n{'─'*60}")
        print(f"🎯 PROJECT: {scenario['name']}")
        print(f"{'─'*60}")
        print(f"Task: {scenario['task']}")

        try:
            # Phase 1: Planning
            print(f"\n📋 PHASE 1: PLANNING")
            print(f"{'━'*40}")

            plan_result = await planner.process_task(
                task=scenario["task"],
                context=scenario["planner_context"]
            )

            print(f"\n{plan_result}")

            # Get the plan ID for the next phase
            recent_plans = await planner.get_recent_plans(limit=1)
            plan_id = recent_plans[0]["id"] if recent_plans else None

            if not plan_id:
                print("❌ No plan ID found, skipping to next scenario")
                continue

            # Phase 2: Building
            print(f"\n🔨 PHASE 2: BUILDING")
            print(f"{'━'*40}")

            build_result = await builder.process_task(
                task=scenario["task"],
                context={
                    "plan_id": plan_id,
                    "execution_mode": "parallel",
                    **scenario["builder_context"]
                }
            )

            print(f"\n{build_result}")

            # Get the build ID for review
            recent_executions = await builder.get_execution_history(limit=1)
            builder_id = recent_executions[0]["id"] if recent_executions else None

            if not builder_id:
                print("❌ No builder ID found, skipping review")
                continue

            # Phase 3: Review
            print(f"\n🔍 PHASE 3: REVIEW")
            print(f"{'━'*40}")

            review_result = await reviewer.review_execution(plan_id, builder_id)

            # Create comprehensive review summary
            review_summary = await reviewer._create_review_summary(review_result)
            print(f"\n{review_summary}")

            # Show detailed metrics
            print(f"\n📊 DETAILED METRICS:")
            print(f"   Accuracy: {review_result['accuracy']:.1%} ({review_result['accuracy']*100:.1f}/100)")
            print(f"   Quality: {review_result['quality']:.1%} ({review_result['quality']*100:.1f}/100)")
            print(f"   Final Score: {review_result['final_score']:.1%} ({review_result['final_score']*100:.1f}/100)")
            if review_result['missing']:
                print(f"\n⚠️  ISSUES IDENTIFIED:")
                for issue in review_result['missing'][:3]:  # Show first 3 issues
                    print(f"   • {issue}")

            print(f"\n✅ Review notes: {review_result['notes']}")

        except Exception as e:
            print(f"❌ Scenario '{scenario['name']}' failed: {e}")
            import traceback
            traceback.print_exc()

    # Show final statistics
    print(f"\n{'─'*60}")
    print("📈 PIPELINE STATISTICS")
    print(f"{'─'*60}")

    try:
        # Get statistics from all agents
        planner_history = await planner.get_recent_plans(limit=2)
        builder_history = await builder.get_execution_history(limit=2)
        reviewer_history = await reviewer.get_review_history(limit=2)

        print(f"📋 Planner created {len(planner_history)} plans")
        print(f"🔨 Builder executed {len(builder_history)} tasks")
        print(f"🔍 Reviewer completed {len(reviewer_history)} reviews")

        if reviewer_history:
            # Calculate average scores
            avg_accuracy = sum(r['content']['accuracy'] for r in reviewer_history) / len(reviewer_history)
            avg_quality = sum(r['content']['quality'] for r in reviewer_history) / len(reviewer_history)
            avg_final = sum(r['content']['final_score'] for r in reviewer_history) / len(reviewer_history)

            print(f"\n🏆 AVERAGE SCORES:")
            print(f"   Accuracy: {avg_accuracy:.1%}")
            print(f"   Quality: {avg_quality:.1%}")
            print(f"   Final: {avg_final:.1%}")

    except Exception as e:
        print(f"❌ Could not calculate statistics: {e}")

    # Cleanup
    await planner.shutdown()
    await builder.shutdown()
    await reviewer.shutdown()

    print(f"\n{'='*70}")
    print("✅ COMPLETE ORCHESTRATION PIPELINE DEMO FINISHED")
    print("="*70)


async def demo_review_scenarios():
    """Demonstrate different review scenarios and edge cases."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'─'*60}")
    print("🧪 REVIEW SCENARIOS & EDGE CASES")
    print(f"{'─'*60}")

    # Create shared memory for all agents
    shared_memory = MemoryManager()

    reviewer = ReviewerAgent({
        "reviewer": {
            "evaluation_mode": "auto",
            "scoring_weights": {"accuracy": 0.7, "quality": 0.3}
        }
    }, shared_memory=shared_memory)

    await reviewer.initialize()

    # Test scenarios with different outcomes
    test_cases = [
        {
            "name": "Perfect Execution",
            "plan_data": {
                "original_task": "Create API endpoints",
                "task_type": "code_generation",
                "subtasks": ["Design endpoints", "Implement handlers", "Add tests"]
            },
            "execution_data": {
                "execution_mode": "sequential",
                "execution_results": [
                    {"index": 0, "success": True, "result": "API design complete", "execution_time": 1.2},
                    {"index": 1, "success": True, "result": "Handler implementation done", "execution_time": 1.8},
                    {"index": 2, "success": True, "result": "Tests added successfully", "execution_time": 1.5}
                ]
            },
            "expected_accuracy": 1.0
        },
        {
            "name": "Partial Success",
            "plan_data": {
                "original_task": "Build documentation system",
                "task_type": "documentation",
                "subtasks": ["Structure docs", "Write content", "Add examples", "Review format"]
            },
            "execution_data": {
                "execution_mode": "parallel",
                "execution_results": [
                    {"index": 0, "success": True, "result": "Documentation structured", "execution_time": 2.1},
                    {"index": 1, "success": True, "result": "Content written", "execution_time": 1.9},
                    {"index": 2, "success": False, "error": "Example generation failed", "execution_time": 0.5},
                    {"index": 3, "success": True, "result": "Format reviewed", "execution_time": 1.1}
                ]
            },
            "expected_accuracy": 0.75
        },
        {
            "name": "Failed Execution",
            "plan_data": {
                "original_task": "Deploy to production",
                "task_type": "deployment",
                "subtasks": ["Build artifacts", "Run tests", "Deploy to server"]
            },
            "execution_data": {
                "execution_mode": "sequential",
                "execution_results": [
                    {"index": 0, "success": False, "error": "Build failed", "execution_time": 0.3},
                    {"index": 1, "success": False, "error": "Tests not run", "execution_time": 0.0},
                    {"index": 2, "success": False, "error": "Deployment aborted", "execution_time": 0.0}
                ]
            },
            "expected_accuracy": 0.0
        }
    ]

    for test_case in test_cases:
        print(f"\n🔬 Testing: {test_case['name']}")

        try:
            # Store test data in memory
            plan_id = await reviewer.memory.store(
                content=test_case["plan_data"],
                memory_type=MemoryType.WORKING,
                metadata={"agent": "Planner", "test_case": test_case["name"]},
                tags={"plan", "test"}
            )

            builder_id = await reviewer.memory.store(
                content=test_case["execution_data"],
                memory_type=MemoryType.WORKING,
                metadata={"agent": "Builder", "test_case": test_case["name"]},
                tags={"execution", "test"}
            )

            # Perform review
            review_result = await reviewer.review_execution(plan_id, builder_id)

            print(f"   📊 Results: {review_result['accuracy']:.1%} accuracy, {review_result['quality']:.1%} quality")
            print(f"   🎯 Expected: ~{test_case['expected_accuracy']:.1%} accuracy")
            # Verify review was stored
            history = await reviewer.get_review_history(limit=1)
            if history:
                print(f"   💾 Review stored: {history[0]['id'][:8]}")

        except Exception as e:
            print(f"   ❌ Test failed: {e}")

    await reviewer.shutdown()


async def demo_similarity_analysis():
    """Demonstrate the cosine similarity analysis in reviews."""

    if not IMPORTS_OK:
        print("❌ Cannot run demo due to import errors.")
        return

    print(f"\n{'─'*60}")
    print("🧮 SIMILARITY ANALYSIS DEMO")
    print(f"{'─'*60}")

    # Create shared memory for all agents
    shared_memory = MemoryManager()

    reviewer = ReviewerAgent(shared_memory=shared_memory)
    await reviewer.initialize()

    # Test similarity calculations
    test_pairs = [
        {
            "name": "High Similarity",
            "text1": "Create API endpoints for user management with authentication",
            "text2": "Built REST API with user authentication endpoints and proper validation",
            "expected": "high"
        },
        {
            "name": "Medium Similarity",
            "text1": "Write comprehensive documentation for the project",
            "text2": "Created basic README file with installation instructions",
            "expected": "medium"
        },
        {
            "name": "Low Similarity",
            "text1": "Research machine learning algorithms for NLP",
            "text2": "Implemented basic calculator in JavaScript",
            "expected": "low"
        }
    ]

    for pair in test_pairs:
        print(f"\n📊 {pair['name']}:")
        print(f"   Plan: {pair['text1'][:50]}...")
        print(f"   Execution: {pair['text2'][:50]}...")

        similarity = await reviewer._calculate_similarity(pair['text1'], pair['text2'])

        print(f"   🔍 Similarity: {similarity:.1%}")

        if pair['expected'] == "high" and similarity > 0.7:
            print(f"   ✅ Correctly identified high similarity")
        elif pair['expected'] == "medium" and 0.3 < similarity < 0.7:
            print(f"   ✅ Correctly identified medium similarity")
        elif pair['expected'] == "low" and similarity < 0.3:
            print(f"   ✅ Correctly identified low similarity")
        else:
            print(f"   ⚠️  Similarity score ({similarity:.1%}) doesn't match expected {pair['expected']}")

    await reviewer.shutdown()


if __name__ == "__main__":
    """Run the reviewer agent demonstrations."""

    async def main():
        print("🚀 Starting ReviewerAgent Demonstrations...")

        # Run complete pipeline demo
        await demo_complete_pipeline()

        # Run review scenarios
        await demo_review_scenarios()

        # Run similarity analysis
        await demo_similarity_analysis()

        print("\n🎉 All ReviewerAgent demonstrations completed successfully!")
        print("\n✨ Demonstrated capabilities:")
        print("   • Complete Planner → Builder → Reviewer pipeline")
        print("   • Automated quality assessment and scoring")
        print("   • Cosine similarity analysis for content matching")
        print("   • Comprehensive error handling and edge cases")
        print("   • Memory integration for persistent reviews")

    # Check if imports are working
    if IMPORTS_OK:
        # Run the async main function
        asyncio.run(main())
    else:
        print("❌ Cannot run demonstrations due to import errors.")
        print("Please ensure all dependencies are installed:")
        print("  pip install rich pyyaml numpy")
