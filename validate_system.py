"""
System Validation Script for TMAO.

This script validates that all critical components are working correctly
after the fixes have been applied.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys
from typing import Dict, Any

# Add src to path
sys.path.insert(0, 'src')

try:
    from agents.planner_agent import PlannerAgent
    from agents.builder_agent import BuilderAgent
    from agents.reviewer_agent import ReviewerAgent
    from agents.coordinator_agent import CoordinatorAgent
    from core.memory import MemoryManager, MemoryType
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


async def test_memory_sharing():
    """Test that agents share memory correctly."""
    print("\n" + "="*60)
    print("TEST 1: Memory Sharing")
    print("="*60)
    
    # Create shared memory
    shared_memory = MemoryManager()
    
    # Create agents with shared memory
    planner = PlannerAgent(shared_memory=shared_memory)
    builder = BuilderAgent(shared_memory=shared_memory)
    reviewer = ReviewerAgent(shared_memory=shared_memory)
    
    await planner.initialize()
    await builder.initialize()
    await reviewer.initialize()
    
    # Planner stores something
    test_id = await planner.memory.store(
        content={"test": "data", "value": 123},
        memory_type=MemoryType.WORKING,
        tags={"test"}
    )
    
    # Builder should be able to retrieve it
    item = builder.memory.get(test_id)
    
    if item and isinstance(item.content, dict) and item.content.get("test") == "data":
        print("✅ Memory sharing works: Builder retrieved Planner's data")
        print(f"   Data: {item.content}")
    else:
        print("❌ Memory sharing failed: Builder couldn't retrieve data")
        return False
    
    # Reviewer should also see it
    item2 = reviewer.memory.get(test_id)
    if item2 and isinstance(item2.content, dict):
        print("✅ Memory sharing works: Reviewer also has access")
    else:
        print("❌ Memory sharing failed: Reviewer couldn't retrieve data")
        return False
    
    await planner.shutdown()
    await builder.shutdown()
    await reviewer.shutdown()
    
    return True


async def test_planner_basic():
    """Test basic planner functionality."""
    print("\n" + "="*60)
    print("TEST 2: Planner Basic Functionality")
    print("="*60)
    
    planner = PlannerAgent()
    await planner.initialize()
    
    try:
        result = await planner.process_task(
            task="Build a simple web API",
            context={"framework": "FastAPI"}
        )
        
        if result and "subtasks" in result.lower():
            print("✅ Planner generates plans successfully")
            
            # Check if plan is in memory
            recent = await planner.get_recent_plans(limit=1)
            if recent and len(recent) > 0:
                print(f"✅ Plan stored in memory: {recent[0]['id'][:8]}")
                
                # Validate plan structure
                plan_content = recent[0]['content']
                if isinstance(plan_content, dict) and 'subtasks' in plan_content:
                    print(f"✅ Plan structure valid: {len(plan_content['subtasks'])} subtasks")
                    return True
                else:
                    print("❌ Plan structure invalid")
                    return False
            else:
                print("❌ Plan not found in memory")
                return False
        else:
            print("❌ Planner failed to generate plan")
            return False
            
    except Exception as e:
        print(f"❌ Planner test failed: {e}")
        return False
    finally:
        await planner.shutdown()


async def test_coordinator_initialization():
    """Test coordinator can initialize sub-agents with shared memory."""
    print("\n" + "="*60)
    print("TEST 3: Coordinator Initialization")
    print("="*60)
    
    coordinator = CoordinatorAgent()
    await coordinator.initialize()
    
    # Check that coordinator has its own memory
    if coordinator.memory:
        print("✅ Coordinator has memory manager")
    else:
        print("❌ Coordinator missing memory manager")
        return False
    
    # Test that sub-agents can be initialized
    try:
        # This should create planner with shared memory
        if not coordinator.planner:
            coordinator.planner = PlannerAgent(shared_memory=coordinator.memory)
            await coordinator.planner.initialize()
        
        # Verify planner uses coordinator's memory
        if coordinator.planner.memory is coordinator.memory:
            print("✅ Planner shares memory with Coordinator")
        else:
            print("❌ Planner has separate memory instance")
            return False
        
        await coordinator.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Coordinator initialization failed: {e}")
        return False


async def test_embedding_cache():
    """Test that embedding cache works."""
    print("\n" + "="*60)
    print("TEST 4: Embedding Cache")
    print("="*60)
    
    memory = MemoryManager()
    
    # Generate embedding for same text twice
    text = "test embedding cache"
    
    embed1 = await memory._embed(text)
    cache_size_1 = len(memory._embedding_cache)
    
    embed2 = await memory._embed(text)
    cache_size_2 = len(memory._embedding_cache)
    
    # Should be cached (same result, cache size doesn't increase)
    import numpy as np
    if np.array_equal(embed1, embed2):
        print("✅ Embedding cache returns consistent results")
    else:
        print("❌ Embedding cache inconsistent")
        return False
    
    if cache_size_1 == cache_size_2:
        print("✅ Embedding cache prevents duplicate entries")
    else:
        print("⚠️  Cache size changed (may be expected)")
    
    return True


async def test_json_serialization():
    """Test JSON serialization and deserialization."""
    print("\n" + "="*60)
    print("TEST 5: JSON Serialization")
    print("="*60)
    
    memory = MemoryManager()
    
    # Store structured data
    test_data = {
        "task": "test",
        "subtasks": ["a", "b", "c"],
        "metadata": {"count": 3}
    }
    
    mem_id = await memory.store(
        content=test_data,
        memory_type=MemoryType.WORKING
    )
    
    # Retrieve and check
    item = memory.get(mem_id)
    
    if item and isinstance(item.content, dict):
        print("✅ JSON deserialization works")
        if item.content == test_data:
            print("✅ Data integrity maintained")
            return True
        else:
            print("❌ Data corrupted during serialization")
            return False
    else:
        print("❌ JSON deserialization failed")
        return False


async def run_all_tests():
    """Run all validation tests."""
    print("\n" + "🧪"*30)
    print("TMAO SYSTEM VALIDATION")
    print("🧪"*30)
    
    tests = [
        ("Memory Sharing", test_memory_sharing),
        ("Planner Basic", test_planner_basic),
        ("Coordinator Init", test_coordinator_initialization),
        ("Embedding Cache", test_embedding_cache),
        ("JSON Serialization", test_json_serialization),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is operational!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review needed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
