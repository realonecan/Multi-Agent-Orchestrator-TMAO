import asyncio

async def main():
    from src.agents.coordinator_agent import CoordinatorAgent
    coord = CoordinatorAgent()
    await coord.initialize()
    task = "Create a small CLI tool that adds two numbers in Python"
    print(f"Running orchestration for: {task}")
    result = await coord.orchestrate(task, {})
    await coord.shutdown()
    print("\nSummary:")
    print(result.get("summary", {}))
    print("\nIDs:")
    print({k: result.get(k) for k in ("plan_id", "execution_id", "review_id")})

if __name__ == "__main__":
    asyncio.run(main())
