import asyncio
import sys
sys.path.insert(0, 'src')

async def simple_test():
    """Simple test for CoordinatorAgent"""
    try:
        from agents.coordinator_agent import CoordinatorAgent

        print("✅ CoordinatorAgent imported successfully")

        # Simple config
        config = {
            "coordinator": {
                "mode": "auto",
                "max_retries": 1,
                "enable_parallel": False
            }
        }

        coordinator = CoordinatorAgent(config)
        print("✅ CoordinatorAgent created")

        await coordinator.initialize()
        print("✅ CoordinatorAgent initialized")

        print(f"Coordinator: {coordinator.name} ({coordinator.role})")
        print(f"Mode: {coordinator.mode}")
        print(f"Max Retries: {coordinator.max_retries}")
        print(f"Parallel: {coordinator.enable_parallel}")

        await coordinator.shutdown()
        print("✅ CoordinatorAgent shutdown complete")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    if result:
        print("🎉 Simple test passed!")
    else:
        print("❌ Simple test failed!")
