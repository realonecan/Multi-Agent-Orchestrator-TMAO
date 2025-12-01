"""Test UI integration with agents."""
import asyncio
import sys

async def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    
    try:
        from src.agents.planner_agent import PlannerAgent
        print("✓ PlannerAgent imported")
    except Exception as e:
        print(f"✗ PlannerAgent import failed: {e}")
        return False
    
    try:
        from src.agents.builder_agent import BuilderAgent
        print("✓ BuilderAgent imported")
    except Exception as e:
        print(f"✗ BuilderAgent import failed: {e}")
        return False
    
    try:
        from src.agents.reviewer_agent import ReviewerAgent
        print("✓ ReviewerAgent imported")
    except Exception as e:
        print(f"✗ ReviewerAgent import failed: {e}")
        return False
    
    try:
        from src.agents.coordinator_agent import CoordinatorAgent
        print("✓ CoordinatorAgent imported")
    except Exception as e:
        print(f"✗ CoordinatorAgent import failed: {e}")
        return False
    
    try:
        from src.ui.adapters import publish_chat, publish_progress, publish_metrics
        print("✓ UI adapters imported")
    except Exception as e:
        print(f"✗ UI adapters import failed: {e}")
        return False
    
    return True

async def test_planner_events():
    """Test that Planner publishes events."""
    print("\nTesting Planner event publishing...")
    
    from src.agents.planner_agent import PlannerAgent, UI_ENABLED
    from src.ui.event_bus import event_bus
    
    print(f"UI_ENABLED in PlannerAgent: {UI_ENABLED}")
    
    if not UI_ENABLED:
        print("✗ UI not enabled in PlannerAgent!")
        return False
    
    # Subscribe to events
    events_received = []
    
    async def chat_handler(payload):
        events_received.append(('chat', payload))
        print(f"  Received chat: {payload.get('agent')} - {payload.get('text')[:50]}")
    
    async def progress_handler(payload):
        events_received.append(('progress', payload))
        print(f"  Received progress: {payload.get('phase')} - {payload.get('percent')}%")
    
    await event_bus.subscribe("chat", chat_handler)
    await event_bus.subscribe("progress", progress_handler)
    
    # Create planner and run task
    planner = PlannerAgent()
    await planner.initialize()
    
    print("Running planner task...")
    result = await planner.process_task("Build a simple API", {"language": "Python"})
    
    await planner.shutdown()
    
    print(f"\nTotal events received: {len(events_received)}")
    
    if len(events_received) == 0:
        print("✗ No events received from Planner!")
        return False
    
    print("✓ Planner published events successfully")
    return True

async def main():
    """Run all tests."""
    print("="*60)
    print("TMAO UI Integration Test")
    print("="*60)
    
    # Test imports
    if not await test_imports():
        print("\n✗ Import test failed")
        return
    
    print("\n" + "="*60)
    
    # Test Planner events
    if not await test_planner_events():
        print("\n✗ Planner event test failed")
        return
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
