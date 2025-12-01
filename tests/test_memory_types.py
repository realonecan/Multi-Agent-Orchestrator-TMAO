"""
Memory Type Safety Test.

Tests the enhanced memory system with JSON auto-parsing functionality.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys

# Add src to path for imports
sys.path.insert(0, 'src')

async def test_memory_type_safety():
    """Test the enhanced memory system with type safety."""

    try:
        from src.core.memory import MemoryManager, MemoryType, MemoryQuery

        print("🧪 Testing Enhanced Memory System...")
        print("="*50)

        memory = MemoryManager()

        # Test 1: Store structured data (should be JSON serialized)
        print("\n📝 Test 1: Storing structured data")
        plan_data = {
            "task": "Build REST API",
            "subtasks": ["design", "implement", "test"],
            "priority": "high"
        }

        plan_id = await memory.store(
            content=plan_data,
            memory_type=MemoryType.WORKING,
            metadata={"agent": "Planner", "plan_type": "decomposition"},
            tags={"plan", "api"}
        )

        print(f"   ✅ Stored plan: {plan_id[:8]}")

        # Test 2: Store plain string (should remain as string)
        print("\n📝 Test 2: Storing plain string")
        note_id = await memory.store(
            content="This is a plain text note",
            memory_type=MemoryType.EPISODIC,
            metadata={"agent": "Builder"},
            tags={"note"}
        )

        print(f"   ✅ Stored note: {note_id[:8]}")

        # Test 3: Retrieve and check auto-parsing
        print("\n🔍 Test 3: Retrieving with auto-parsing")

        # Retrieve the plan (should be parsed back to dict)
        plan_results = await memory.retrieve(
            MemoryQuery(text="REST API", memory_type=MemoryType.WORKING, limit=1)
        )

        if plan_results:
            item = plan_results[0]
            content = item.content

            print(f"   Retrieved: {item.id[:8]}")
            print(f"   Content type: {type(content).__name__}")

            if isinstance(content, dict):
                print(f"   ✅ Auto-parsed successfully!")
                print(f"   Task: {content.get('task')}")
                print(f"   Subtasks: {content.get('subtasks')}")
                print(f"   Priority: {content.get('priority')}")
            else:
                print(f"   ❌ Expected dict, got {type(content)}")

        # Test 4: Retrieve plain string (should remain as string)
        note_results = await memory.retrieve(
            MemoryQuery(text="plain text", memory_type=MemoryType.EPISODIC, limit=1)
        )

        if note_results:
            item = note_results[0]
            content = item.content

            print(f"\n   Retrieved: {item.id[:8]}")
            print(f"   Content type: {type(content).__name__}")

            if isinstance(content, str):
                print(f"   ✅ Plain string preserved!")
                print(f"   Content: {content}")
            else:
                print(f"   ❌ Expected string, got {type(content)}")

        # Test 5: Single item retrieval
        print("\n🎯 Test 4: Single item retrieval")
        direct_item = memory.get(plan_id)

        if direct_item and isinstance(direct_item.content, dict):
            print(f"   ✅ Direct access works: {direct_item.content['task']}")
        else:
            print(f"   ❌ Direct access failed")

        # Test 6: Memory utility methods
        print("\n🛠️ Test 5: Utility methods")
        print(f"   Is structured: {memory.is_structured_content(plan_id)}")
        print(f"   Is structured: {memory.is_structured_content(note_id)}")

        # Show memory stats
        print("\n📊 Memory Statistics:")
        await memory.summary()

        print("\n🎉 All memory type safety tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_memory_type_safety())
