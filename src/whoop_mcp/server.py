from mcp.server import MCPServer

from whoop_mcp.analytics import (
    build_weekly_health_summary,
    calculate_recovery_summary,
)
from whoop_mcp.whoop_client import WhoopClient


mcp = MCPServer(
    "Personal WHOOP MCP"
)


@mcp.tool()
async def whoop_server_status() -> dict:
    """
    Check whether the Personal WHOOP MCP server
    is running and whether WHOOP is accessible.

    Use this tool when checking connection status
    or troubleshooting WHOOP connectivity.
    """

    try:
        client = WhoopClient()
        await client.get_profile()

        return {
            "status": "running",
            "server": "Personal WHOOP MCP",
            "whoop_connected": True,
        }

    except Exception as exc:
        return {
            "status": "running",
            "server": "Personal WHOOP MCP",
            "whoop_connected": False,
            "message": str(exc),
        }


@mcp.tool()
async def get_my_whoop_profile() -> dict:
    """
    Retrieve basic information about the connected
    WHOOP account.

    Use this tool when the user asks which WHOOP
    account is connected or asks for basic profile
    information.
    """

    client = WhoopClient()

    profile = await client.get_profile()

    # Avoid exposing unnecessary identifiers/email.
    return {
        "provider": "WHOOP",
        "first_name": profile.get(
            "first_name"
        ),
        "last_name": profile.get(
            "last_name"
        ),
    }


@mcp.tool()
async def get_my_whoop_recovery(
    days: int = 7,
) -> dict:
    """
    Retrieve recent WHOOP recovery metrics.

    Includes recovery score, resting heart rate,
    HRV, SpO2, skin temperature, and recovery state.

    Use this tool when the user asks about recovery,
    readiness, HRV, resting heart rate, or individual
    recent recovery values.

    Args:
        days: Number of recent days to retrieve.
              Must be between 1 and 90.
    """

    if days < 1 or days > 90:
        raise ValueError(
            "days must be between 1 and 90"
        )

    client = WhoopClient()

    records = await client.get_recovery_clean(
        days=days
    )

    return {
        "days_requested": days,
        "records": records,
    }


@mcp.tool()
async def get_my_whoop_cycles(
    days: int = 7,
) -> dict:
    """
    Retrieve recent WHOOP daily cycle/activity data.

    Includes daily strain, heart rate, energy
    expenditure, and related physiological metrics.

    Use this tool when the user asks about daily
    strain, activity load, cycle data, or general
    daily activity.

    Args:
        days: Number of recent days to retrieve.
              Must be between 1 and 90.
    """

    if days < 1 or days > 90:
        raise ValueError(
            "days must be between 1 and 90"
        )

    client = WhoopClient()

    records = await client.get_cycles_clean(
        days=days
    )

    return {
        "days_requested": days,
        "records": records,
    }


@mcp.tool()
async def get_my_whoop_sleep(
    days: int = 7,
) -> dict:
    """
    Retrieve recent WHOOP sleep information.

    Includes sleep performance, efficiency,
    consistency, sleep stages, respiratory rate,
    and sleep timing.

    Use this tool when the user asks about sleep
    quality, duration, efficiency, REM sleep,
    deep sleep, consistency, or recent sleep records.

    Args:
        days: Number of recent days to retrieve.
              Must be between 1 and 90.
    """

    if days < 1 or days > 90:
        raise ValueError(
            "days must be between 1 and 90"
        )

    client = WhoopClient()

    records = await client.get_sleep_clean(
        days=days
    )

    return {
        "days_requested": days,
        "records": records,
    }


@mcp.tool()
async def get_my_whoop_workouts(
    days: int = 30,
) -> dict:
    """
    Retrieve recent WHOOP workout records.

    Includes activity type, workout strain,
    heart rate, energy expenditure, distance,
    and other available workout metrics.

    Use this tool when the user asks about workouts,
    exercise history, training intensity, workout
    strain, or recent physical activities.

    Args:
        days: Number of recent days to retrieve.
              Must be between 1 and 90.
    """

    if days < 1 or days > 90:
        raise ValueError(
            "days must be between 1 and 90"
        )

    client = WhoopClient()

    records = await client.get_workouts_clean(
        days=days
    )

    return {
        "days_requested": days,
        "records": records,
    }


@mcp.tool()
async def get_my_whoop_body_measurements() -> dict:
    """
    Retrieve WHOOP body measurements.

    Use this tool when the user asks about stored
    measurements such as height, weight, or maximum
    heart rate.
    """

    client = WhoopClient()

    return await (
        client.get_body_measurements_clean()
    )


@mcp.tool()
async def get_today_health_snapshot() -> dict:
    """
    Retrieve a concise snapshot of the user's latest
    WHOOP recovery, sleep, daily activity, and workouts.

    Use this tool for broad current-state questions:
    - How am I doing today?
    - How ready am I today?
    - Give me today's WHOOP summary.
    - How are my recovery and sleep today?
    """

    client = WhoopClient()

    recovery = await client.get_recovery_clean(
        days=2
    )

    sleep = await client.get_sleep_clean(
        days=2
    )

    cycles = await client.get_cycles_clean(
        days=2
    )

    workouts = await client.get_workouts_clean(
        days=2
    )

    return {
        "latest_recovery": (
            recovery[0]
            if recovery
            else None
        ),
        "latest_sleep": (
            sleep[0]
            if sleep
            else None
        ),
        "latest_activity": (
            cycles[0]
            if cycles
            else None
        ),
        "recent_workouts": workouts,
    }


@mcp.tool()
async def get_weekly_health_summary() -> dict:
    """
    Generate a deterministic 7-day WHOOP health
    and fitness summary.

    Combines recovery, HRV, resting heart rate,
    sleep, daily strain, and workout information.

    Use this tool when the user asks:
    - How was my week?
    - Give me my weekly WHOOP summary.
    - How have recovery and sleep been this week?
    - Summarize my recent health and training data.
    """

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

    return build_weekly_health_summary(
        recovery_records=recovery,
        sleep_records=sleep,
        cycle_records=cycles,
        workout_records=workouts,
    )


@mcp.tool()
async def get_recovery_trend(
    days: int = 14,
) -> dict:
    """
    Analyze WHOOP recovery trends over a recent
    period using recovery score, HRV, and resting
    heart rate.

    Use this tool when the user asks:
    - Is my recovery improving?
    - How has my HRV changed?
    - Show my recovery trend.
    - Compare my recent recovery levels.

    Args:
        days: Number of recent days to analyze.
              Must be between 2 and 90.
    """

    if days < 2 or days > 90:
        raise ValueError(
            "days must be between 2 and 90"
        )

    client = WhoopClient()

    recovery = await client.get_recovery_clean(
        days=days
    )

    summary = calculate_recovery_summary(
        recovery
    )

    return {
        "period_days": days,
        **summary,
    }