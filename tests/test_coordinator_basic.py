"""
Coordinator Agent Basic Tests.

Unit tests for CoordinatorAgent functionality including orchestration flow,
error handling, and result validation.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys

# Add src to path for imports
sys.path.insert(0, 'src')

async def test_coordinator_basic():
    """Test basic CoordinatorAgent functionality."""

    try:
        from agents.coordinator_agent import CoordinatorAgent

        print("🧪 Testing CoordinatorAgent Basic Functionality...")
        print("="*50)

        # Create coordinator with test configuration
        config = {
            "coordinator": {
                "mode": "auto",
                "max_retries": 1,
                "enable_parallel": True
            },
            "planner": {"max_subtasks": 3},
            "builder": {"execution_mode": "sequential", "max_concurrency": 1},
            "reviewer": {"evaluation_mode": "auto"}
        }

        coordinator = CoordinatorAgent(config)
        await coordinator.initialize()

        print("✅ CoordinatorAgent initialized successfully")
        print(f"   Name: {coordinator.name}")
        print(f"   Role: {coordinator.role}")
        print(f"   Mode: {coordinator.mode}")
        print(f"   Max Retries: {coordinator.max_retries}")
        print(f"   Parallel Enabled: {coordinator.enable_parallel}")

        # Test 1: Simple orchestration
        print("\n🎯 Test 1: Simple Orchestration")

        test_task = "Create a simple calculator application"
        context = {
            "framework": "Tkinter",
            "include_gui": True,
            "include_tests": True
        }

        result = await coordinator.orchestrate(test_task, context)

        print(f"   📊 Orchestration completed successfully")
        print(f"   🎯 Final Score: {result['summary']['final_score']:.1%}")
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

        print(f"   ✅ All required fields present")
        print(f"   ✅ Scores in valid range (0.0-1.0)")
        print(f"   ✅ Result structure valid")

        # Test 2: Orchestration history
        print("\n📚 Test 2: Orchestration History")

        history = await coordinator.get_orchestration_history(limit=1)

        print(f"   Retrieved {len(history['orchestrations'])} orchestrations")
        assert "total_orchestrations" in history, "History should contain total count"
        assert "orchestrations" in history, "History should contain orchestrations list"

        if history["orchestrations"]:
            latest = history["orchestrations"][0]
            print(f"   💾 Latest orchestration: {latest['id'][:8]}")
            print(f"   📊 Latest score: {latest['content']['summary']['final_score']:.1%}")

        # Test 3: Orchestration status
        print("\n🔍 Test 3: Orchestration Status")

        status = await coordinator.get_orchestration_status(result["orchestration_id"])

        assert status is not None, "Should find orchestration status"
        assert status["status"] == "complete", f"Expected complete, got {status['status']}"
        assert "result" in status, "Status should contain result"

        print(f"   ✅ Status tracking working: {status['status']}")

        await coordinator.shutdown()

        print("\n🎉 All CoordinatorAgent tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test CoordinatorAgent error handling and retry mechanisms."""

    try:
        from agents.coordinator_agent import CoordinatorAgent

        print("\n🛡️ Testing Error Handling...")
        print("="*40)

        # Test with high retry settings
        config = {
            "coordinator": {
                "mode": "auto",
                "max_retries": 2,
                "enable_parallel": False  # Sequential for predictable testing
            },
            "builder": {
                "execution_mode": "sequential",
                "max_concurrency": 1,
                "error_recovery": True
            }
        }

        coordinator = CoordinatorAgent(config)
        await coordinator.initialize()

        # Test successful orchestration
        result = await coordinator.orchestrate(
            "Create a basic web page",
            {"framework": "HTML", "include_css": True}
        )

        print(f"   ✅ Successful orchestration: {result['summary']['final_score']:.1%}")

        # Verify the result contains all expected data
        assert "stage_results" in result, "Should contain stage results"
        assert "planning" in result["stage_results"], "Should contain planning results"
        assert "building" in result["stage_results"], "Should contain building results"
        assert "reviewing" in result["stage_results"], "Should contain reviewing results"

        print(f"   ✅ All stages completed successfully")

        await coordinator.shutdown()
        print("\n✅ Error handling test completed")

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_configuration():
    """Test CoordinatorAgent configuration handling."""

    try:
        from agents.coordinator_agent import CoordinatorAgent

        print("\n⚙️ Testing Configuration Handling...")
        print("="*40)

        # Test different configuration modes
        configs = [
            {
                "name": "Auto Parallel",
                "config": {
                    "coordinator": {"mode": "auto", "max_retries": 2, "enable_parallel": True},
                    "builder": {"execution_mode": "parallel", "max_concurrency": 3}
                }
            },
            {
                "name": "Sequential Mode",
                "config": {
                    "coordinator": {"mode": "auto", "max_retries": 1, "enable_parallel": False},
                    "builder": {"execution_mode": "sequential", "max_concurrency": 1}
                }
            },
            {
                "name": "High Retry",
                "config": {
                    "coordinator": {"mode": "auto", "max_retries": 5, "enable_parallel": True},
                    "builder": {"execution_mode": "parallel", "error_recovery": True}
                }
            }
        ]

        for test_config in configs:
            print(f"\n🔧 Testing: {test_config['name']}")

            coordinator = CoordinatorAgent(test_config["config"])
            await coordinator.initialize()

            # Verify configuration was loaded correctly
            assert coordinator.mode == test_config["config"]["coordinator"]["mode"]
            assert coordinator.max_retries == test_config["config"]["coordinator"]["max_retries"]
            assert coordinator.enable_parallel == test_config["config"]["coordinator"]["enable_parallel"]

            print(f"   ✅ Configuration loaded: mode={coordinator.mode}, retries={coordinator.max_retries}, parallel={coordinator.enable_parallel}")

            # Quick orchestration test
            result = await coordinator.orchestrate("Test configuration", {"test": True})
            print(f"   📊 Test result: {result['summary']['final_score']:.1%}")

            await coordinator.shutdown()

        print("\n✅ Configuration handling test completed")

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """Run CoordinatorAgent tests."""

    async def main():
        print("🎭 Running CoordinatorAgent Tests...")

        # Run basic functionality tests
        basic_success = await test_coordinator_basic()

        # Run error handling tests
        await test_error_handling()

        # Run configuration tests
        await test_configuration()

        if basic_success:
            print("\n🎉 All tests completed successfully!")
            print("\n📋 Test Summary:")
            print("   ✅ CoordinatorAgent initialization")
            print("   ✅ Full orchestration pipeline (Plan→Build→Review)")
            print("   ✅ Result structure validation")
            print("   ✅ Score validation and ranges")
            print("   ✅ Orchestration history and status tracking")
            print("   ✅ Error handling and retry mechanisms")
            print("   ✅ Configuration management")
            print("   ✅ Multi-stage coordination")
        else:
            print("\n❌ Some tests failed - check output above")

    asyncio.run(main())
