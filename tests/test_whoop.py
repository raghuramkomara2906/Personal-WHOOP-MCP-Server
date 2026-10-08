import asyncio

from whoop_mcp.whoop_client import WhoopClient


async def main():
    client = WhoopClient()

    print("\nRECOVERY")
    print(await client.get_recovery_clean(days=7))

    print("\nSLEEP")
    print(await client.get_sleep_clean(days=7))

    print("\nCYCLES")
    print(await client.get_cycles_clean(days=7))

    print("\nWORKOUTS")
    print(await client.get_workouts_clean(days=30))

    print("\nBODY")
    print(await client.get_body_measurements_clean())


asyncio.run(main())