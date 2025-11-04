import asyncio
import sys
sys.path.insert(0, 'src')

async def fast_test():
    """Fast test for CoordinatorAgent with minimal delays"""
    try:
        from agents.coordinator_agent import CoordinatorAgent

        print("🧪 Testing CoordinatorAgent Fast Mode...")
        print("="*50)

        # Create coordinator with fast configuration
        config = {
            "coordinator": {
                "mode": "auto",
                "max_retries": 1,
                "enable_parallel": False  # Sequential for predictability
            },
            "planner": {"max_subtasks": 2},  # Limit subtasks
            "builder": {
                "execution_mode": "sequential",
                "max_concurrency": 1,
                # Override execution times to be much faster
                "fast_mode": True
            },
            "reviewer": {"evaluation_mode": "auto"}
        }

        coordinator = CoordinatorAgent(config)
        await coordinator.initialize()

        print("✅ CoordinatorAgent initialized successfully")
        print(f"   Name: {coordinator.name}")
        print(f"   Mode: {coordinator.mode}")
        print(f"   Parallel: {coordinator.enable_parallel}")

        # Test orchestration with simple task
        print("\n🎯 Testing orchestration...")
        test_task = "Create a simple function"
        context = {"fast_mode": True}

        result = await coordinator.orchestrate(test_task, context)

        print("   📊 Orchestration completed successfully"        print(f"   🎯 Final Score: {result['summary']['final_score']:.1%}")
        print(f"   📋 Plan ID: {result['plan_id'][:8]}")
        print(f"   🔨 Execution ID: {result['execution_id'][:8]}")
        print(f"   🔍 Review ID: {result['review_id'][:8]}")

        # Verify result structure
        required_fields = ["task", "plan_id", "execution_id", "review_id", "summary"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Verify summary structure
        summary = result["summary"]
        required_summary_fields = ["accuracy", "quality", "final_score", "notes"]
        for field in required_summary_fields:
            assert field in summary, f"Missing summary field: {field}"

        # Verify score ranges
        assert 0.0 <= summary["accuracy"] <= 1.0, f"Accuracy out of range: {summary['accuracy']}"
        assert 0.0 <= summary["quality"] <= 1.0, f"Quality out of range: {summary['quality']}"
        assert 0.0 <= summary["final_score"] <= 1.0, f"Final score out of range: {summary['final_score']}"

        print("   ✅ All required fields present"        print("   ✅ Scores in valid range (0.0-1.0)"        print("   ✅ Result structure valid"
        await coordinator.shutdown()

        print("\n🎉 Fast test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Fast test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(fast_test())
    if result:
        print("\n📋 Test Summary:")
        print("   ✅ CoordinatorAgent initialization")
        print("   ✅ Fast orchestration pipeline")
        print("   ✅ Result structure validation")
        print("   ✅ Score validation")
    else:
        print("\n❌ Fast test failed!")
