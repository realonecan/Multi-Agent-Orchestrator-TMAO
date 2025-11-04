"""
Simple BuilderAgent Test with Context.

Test BuilderAgent directly with plan data in context.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys

# Add src to path for imports
sys.path.insert(0, 'src')

async def test_builder_with_context():
    """Test BuilderAgent with plan data directly in context."""

    try:
        from agents.builder_agent import BuilderAgent

        print("🔨 Testing BuilderAgent with Direct Context...")
        print("="*50)

        # Create builder
        builder = BuilderAgent({
            "execution_mode": "sequential",
            "max_concurrency": 1,
            "error_recovery": False
        })

        await builder.initialize()

        # Mock plan data (similar to what PlannerAgent creates)
        mock_plan_data = {
            "original_task": "Create a simple calculator",
            "task_type": "code_generation",
            "subtasks": [
                "Design calculator interface",
                "Implement basic arithmetic functions",
                "Add input validation",
                "Create user interface"
            ],
            "context": {"include_gui": True},
            "timestamp": asyncio.get_event_loop().time()
        }

        # Mock context with plan data
        test_context = {
            "plan_id": "mock_plan_123",
            "plan_data": mock_plan_data,
            "subtasks": mock_plan_data["subtasks"],
            "execution_mode": "sequential"
        }

        print(f"📋 Test context keys: {list(test_context.keys())}")
        print(f"📋 Plan data type: {type(test_context['plan_data'])}")
        print(f"📋 Subtasks count: {len(test_context['subtasks'])}")

        # Test BuilderAgent with context
        result = await builder.process_task("Create a simple calculator", test_context)

        print(f"   ✅ BuilderAgent completed successfully")
        print(f"   📊 Result length: {len(result)} characters")

        # Check execution history
        history = await builder.get_execution_history(limit=1)
        if history:
            execution_id = history[0]["id"]
            print(f"   💾 Execution stored: {execution_id[:8]}")

            # Test ReviewerAgent
            from agents.reviewer_agent import ReviewerAgent
            from src.core.memory import MemoryType

            reviewer = ReviewerAgent()
            await reviewer.initialize()

            # Store mock plan in reviewer memory for testing
            plan_id = await reviewer.memory.store(
                content=mock_plan_data,
                memory_type=MemoryType.WORKING,
                metadata={"agent": "Planner"},
                tags={"plan"}
            )

            # Test review
            review_result = await reviewer.review_execution(plan_id, execution_id)
            print(f"   ✅ Review completed: {review_result['accuracy']:.1%} accuracy, {review_result['quality']:.1%} quality")

            await reviewer.shutdown()
        else:
            print("   ❌ No execution found in history")

        await builder.shutdown()

        print("\n🎉 Context test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_builder_with_context())
