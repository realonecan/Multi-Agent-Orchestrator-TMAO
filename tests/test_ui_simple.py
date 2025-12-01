"""Simple UI test - press 1 to test Planner."""
import asyncio
from src.ui.terminal_ui import TMAOCommandCenter

async def auto_test():
    """Automatically test the UI without keyboard input."""
    print("Creating Command Center...")
    cc = TMAOCommandCenter()
    
    # Subscribe to events first
    print("Subscribing to events...")
    await cc._subscribe_events()
    
    # Manually trigger planner demo
    print("Running Planner demo...")
    await cc._run_planner_demo()
    
    # Give events time to process
    await asyncio.sleep(0.5)
    
    print("\nDone! Check if chat panel received messages.")
    print(f"Chat panel has {len(cc.chat_panel.messages)} messages")
    
    for msg in cc.chat_panel.messages:
        print(f"  - {msg.agent}: {msg.text[:50]}")

if __name__ == "__main__":
    asyncio.run(auto_test())
