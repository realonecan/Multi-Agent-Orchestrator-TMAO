"""
Simple Coordinator Test.

Tests the basic coordinator functionality to verify the fixes work.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys
sys.path.insert(0, 'src')

try:
    from agents.coordinator_agent import CoordinatorAgent
    from core.memory import MemoryManager
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


async def test_coordinator_basic():
    """Test basic coordinator functionality."""
    print("\n" + "="*60)
    print("TESTING COORDINATOR BASIC FUNCTIONALITY")
    print("="*60)

    # Create coordinator
    coordinator = CoordinatorAgent()
    await coordinator.initialize()

    # Test simple orchestration
    try:
        result = await coordinator.orchestrate("Create a simple calculator", {
            "language": "Python",
            "include_tests": True
        })

        print("✅ Coordinator orchestration successful!")
        print(f"   Final Score: {result['summary']['final_score']:.1%}")
        print(f"   Accuracy: {result['summary']['accuracy']:.1%}")
        print(f"   Quality: {result['summary']['quality']:.1%}")
        print(f"   Duration: {result['metadata']['duration']:.1f}s")

        return True

    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await coordinator.shutdown()


async def test_shared_memory_coordinator():
    """Test coordinator with explicit shared memory."""
    print("\n" + "="*60)
    print("TESTING COORDINATOR WITH SHARED MEMORY")
    print("="*60)

    # Create shared memory explicitly
    shared_memory = MemoryManager()

    # Create coordinator with shared memory
    coordinator = CoordinatorAgent(shared_memory=shared_memory)
    await coordinator.initialize()

    try:
        result = await coordinator.orchestrate("Build a simple API", {
            "framework": "FastAPI",
            "include_auth": True
        })

        print("✅ Coordinator with shared memory successful!")
        print(f"   Final Score: {result['summary']['final_score']:.1%}")
        print(f"   Plan ID: {result['plan_id'][:8]}")
        print(f"   Execution ID: {result['execution_id'][:8]}")
        print(f"   Review ID: {result['review_id'][:8]}")

        # Verify all IDs exist in shared memory
        plan_item = shared_memory.get(result['plan_id'])
        exec_item = shared_memory.get(result['execution_id'])
        review_item = shared_memory.get(result['review_id'])

        if plan_item:
            print("✅ Plan found in shared memory")
        else:
            print("❌ Plan not found in shared memory")
            return False

        if exec_item:
            print("✅ Execution found in shared memory")
        else:
            print("❌ Execution not found in shared memory")
            return False

        if review_item:
            print("✅ Review found in shared memory")
        else:
            print("❌ Review not found in shared memory")
            return False

        return True

    except Exception as e:
        print(f"❌ Coordinator shared memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await coordinator.shutdown()


async def main():
    """Run all coordinator tests."""
    print("🚀 Starting Coordinator Validation Tests...")

    tests = [
        ("Basic Coordinator", test_coordinator_basic),
        ("Shared Memory Coordinator", test_shared_memory_coordinator),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("COORDINATOR VALIDATION SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 ALL COORDINATOR TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
