import asyncio

from whoop_mcp.analytics import (
    build_weekly_health_summary,
)
from whoop_mcp.whoop_client import WhoopClient


async def main():
    client = WhoopClient()

    recovery = await client.get_recovery_clean(
        days=7
    )

    sleep = await client.get_sleep_clean(
        days=7
    )

    cycles = await client.get_cycles_clean(
        days=7
    )

    workouts = await client.get_workouts_clean(
        days=7
    )

    summary = build_weekly_health_summary(
        recovery,
        sleep,
        cycles,
        workouts,
    )

    print(summary)


asyncio.run(main())