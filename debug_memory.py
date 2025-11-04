"""
Memory Debug Script.

Debug the memory retrieval issue between PlannerAgent and BuilderAgent.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys

# Add src to path for imports
sys.path.insert(0, 'src')

async def debug_memory_retrieval():
    """Debug the memory retrieval issue between agents."""

    try:
        from agents.planner_agent import PlannerAgent
        from agents.builder_agent import BuilderAgent
        from agents.reviewer_agent import ReviewerAgent
        from src.core.memory import MemoryType

        print("🔍 Debugging Memory Retrieval...")
        print("="*50)

        # Create agents
        planner = PlannerAgent()
        builder = BuilderAgent()
        reviewer = ReviewerAgent()

        await planner.initialize()
        await builder.initialize()
        await reviewer.initialize()

        # Test task
        test_task = "Create a simple calculator"
        context = {"include_testing": True}

        print(f"\n📝 Test Task: {test_task}")

        # Step 1: Planner creates plan
        print("\n📋 Step 1: Planner creates plan")
        plan_result = await planner.process_task(test_task, context)
        print(f"   ✅ Plan created: {len(plan_result)} characters")

        # Get plan ID
        recent_plans = await planner.get_recent_plans(limit=1)
        if not recent_plans:
            print("   ❌ No plan found in recent plans")
            return

        plan_id = recent_plans[0]["id"]
        print(f"   📋 Plan ID: {plan_id[:8]}")

        # Step 2: Check what's actually stored in memory
        print("\n💾 Step 2: Check memory contents")

        # Direct memory access from planner
        planner_plan_item = planner.memory.get(plan_id)
        if planner_plan_item:
            print(f"   ✅ Planner memory access: {type(planner_plan_item.content)}")
            if isinstance(planner_plan_item.content, dict):
                print(f"   📋 Subtasks in plan: {len(planner_plan_item.content.get('subtasks', []))}")
                print(f"   📋 First subtask: {planner_plan_item.content.get('subtasks', [None])[0] if planner_plan_item.content.get('subtasks') else 'None'}")
            else:
                print(f"   ❌ Plan content is not a dict: {type(planner_plan_item.content)}")
                print(f"   📄 Content preview: {str(planner_plan_item.content)[:100]}...")
        else:
            print(f"   ❌ Plan not found in planner memory")

        # Step 3: Test CoordinatorAgent approach (direct context passing)
        print("\n🎭 Step 3: Test CoordinatorAgent approach")

        # Get plan data from planner
        planner_plan_item = planner.memory.get(plan_id)
        if planner_plan_item and isinstance(planner_plan_item.content, dict):
            plan_data = planner_plan_item.content
            subtasks = plan_data.get("subtasks", [])

            print(f"   ✅ Got plan data: {len(subtasks)} subtasks")

            # Simulate CoordinatorAgent passing data to BuilderAgent
            builder_context = {
                "plan_id": plan_id,
                "plan_data": plan_data,
                "subtasks": subtasks,
                "execution_mode": "sequential"
            }

            # Test BuilderAgent with direct context
            try:
                result = await builder.process_task(test_task, builder_context)
                print(f"   ✅ BuilderAgent with direct context: SUCCESS")
                print(f"   📊 Execution result length: {len(result)} characters")

                # Check if execution was stored
                recent_executions = await builder.get_execution_history(limit=1)
                if recent_executions:
                    execution_id = recent_executions[0]["id"]
                    print(f"   💾 Execution stored: {execution_id[:8]}")

                    # Test ReviewerAgent
                    print("\n🔍 Step 4: Test ReviewerAgent")

                    # Simulate ReviewerAgent review
                    review_result = await reviewer.review_execution(plan_id, execution_id)
                    print(f"   ✅ Review completed: {review_result['accuracy']:.1%} accuracy, {review_result['quality']:.1%} quality")

                else:
                    print("   ❌ No execution found in builder history")

            except Exception as e:
                print(f"   ❌ BuilderAgent failed: {e}")
        else:
            print(f"   ❌ Could not get plan data from planner")

        await planner.shutdown()
        await builder.shutdown()
        await reviewer.shutdown()

        print("\n🔚 Debug complete")

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_memory_retrieval())
