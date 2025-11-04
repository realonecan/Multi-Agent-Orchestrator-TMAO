"""
Simple BuilderAgent Test.

Quick test to verify BuilderAgent functionality without full demo complexity.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys

# Add src to path for imports
sys.path.insert(0, 'src')

async def test_builder_basic():
    """Test basic BuilderAgent functionality."""

    try:
        from agents.builder_agent import BuilderAgent

        # Create builder with minimal config
        config = {
            "execution_mode": "sequential",
            "max_concurrency": 1,
            "error_recovery": False
        }

        builder = BuilderAgent(config)
        await builder.initialize()

        print("✅ BuilderAgent initialized successfully")
        print(f"   Name: {builder.name}")
        print(f"   Role: {builder.role}")
        print(f"   Mode: {builder.execution_mode}")
        print(f"   Max Concurrency: {builder.max_concurrency}")

        # Test subtask execution
        test_subtasks = [
            "Create API documentation",
            "Implement user authentication",
            "Add error handling"
        ]

        print(f"\n🔧 Testing execution of {len(test_subtasks)} subtasks...")

        results = await builder._execute_sequential(test_subtasks, {"test": True})

        successful = sum(1 for r in results if r.get("success", False))
        print(f"✅ Execution complete: {successful}/{len(results)} successful")

        # Test memory integration
        history = await builder.get_execution_history(limit=1)
        if history:
            print(f"💾 Execution stored in memory: {history[0]['id'][:8]}")

        await builder.shutdown()
        print("✅ BuilderAgent test completed successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_builder_basic())
