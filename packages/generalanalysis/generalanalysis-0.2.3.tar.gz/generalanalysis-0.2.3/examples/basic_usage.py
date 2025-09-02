"""Basic usage examples for the General Analysis SDK."""

import asyncio
import json
import os

import generalanalysis


def sync_example() -> None:
    """Basic synchronous usage example."""
    print("=== Synchronous Example ===\n")

    client = generalanalysis.Client()

    guards = client.guards.list()
    for guard in guards:
        print(f"Guard[{guard.id}]: {guard.name}")

    if guards:
        guard = guards[0]
        result = client.guards.invoke(guard_id=guard.id, text="Hello world")

        result_dict = result.to_dict()
        print(f"Result as dict: {result_dict}")

        result_json = result.to_json(indent=2)
        print(f"Result as JSON:\n{result_json}")


async def async_example() -> None:
    """Basic asynchronous usage example."""
    print("\n=== Asynchronous Example ===\n")

    async with generalanalysis.AsyncClient() as client:
        guards = await client.guards.list()

        if guards:
            guard = guards[0]
            result = await client.guards.invoke(guard_id=guard.id, text="Hello world")

            result_json = result.to_json(indent=2)
            print(f"Async result (JSON):\n{result_json}")


def logs_example() -> None:
    """Example of viewing guard invocation logs."""
    print("\n=== Guard Logs Example ===\n")

    client = generalanalysis.Client()
    logs = client.guards.list_logs(page=1, page_size=1)

    if logs.items:
        log_json = logs.to_json(indent=2)
        print(log_json)


def main() -> None:
    """Run examples."""
    if not os.environ.get("GA_API_KEY"):
        print("Warning: No API key found. Set GA_API_KEY.")
        return

    try:
        sync_example()
        asyncio.run(async_example())
        logs_example()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
