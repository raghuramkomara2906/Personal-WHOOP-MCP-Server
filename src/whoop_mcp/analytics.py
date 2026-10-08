from statistics import mean


def _safe_mean(values: list[float | int | None]) -> float | None:
    cleaned = [
        value
        for value in values
        if isinstance(value, (int, float))
    ]

    if not cleaned:
        return None

    return round(mean(cleaned), 2)


def _safe_min(values: list[float | int | None]) -> float | None:
    cleaned = [
        value
        for value in values
        if isinstance(value, (int, float))
    ]

    if not cleaned:
        return None

    return min(cleaned)


def _safe_max(values: list[float | int | None]) -> float | None:
    cleaned = [
        value
        for value in values
        if isinstance(value, (int, float))
    ]

    if not cleaned:
        return None

    return max(cleaned)
def calculate_recovery_summary(
    records: list[dict],
) -> dict:
    if not records:
        return {
            "records_analyzed": 0,
            "message": "No recovery data available.",
        }

    recovery_scores = [
        record.get("recovery_score")
        for record in records
    ]

    hrv_values = [
        record.get("hrv_ms")
        for record in records
    ]

    resting_hr_values = [
        record.get("resting_heart_rate")
        for record in records
    ]

    latest = records[0]

    previous = (
        records[1]
        if len(records) > 1
        else None
    )

    recovery_change = None

    if (
        previous
        and isinstance(
            latest.get("recovery_score"),
            (int, float),
        )
        and isinstance(
            previous.get("recovery_score"),
            (int, float),
        )
    ):
        recovery_change = round(
            latest["recovery_score"]
            - previous["recovery_score"],
            2,
        )

    return {
        "records_analyzed": len(records),
        "latest_date": latest.get("date"),
        "latest_recovery": latest.get(
            "recovery_score"
        ),
        "latest_hrv_ms": latest.get("hrv_ms"),
        "latest_resting_heart_rate": latest.get(
            "resting_heart_rate"
        ),
        "average_recovery": _safe_mean(
            recovery_scores
        ),
        "average_hrv_ms": _safe_mean(
            hrv_values
        ),
        "average_resting_heart_rate": _safe_mean(
            resting_hr_values
        ),
        "highest_recovery": _safe_max(
            recovery_scores
        ),
        "lowest_recovery": _safe_min(
            recovery_scores
        ),
        "recovery_change_from_previous_day":
            recovery_change,
    }
def calculate_sleep_summary(
    records: list[dict],
) -> dict:
    if not records:
        return {
            "records_analyzed": 0,
            "message": "No sleep data available.",
        }

    main_sleep_records = [
        record
        for record in records
        if not record.get("nap")
    ]

    records_to_use = (
        main_sleep_records
        if main_sleep_records
        else records
    )

    performance = [
        record.get(
            "sleep_performance_percentage"
        )
        for record in records_to_use
    ]

    efficiency = [
        record.get(
            "sleep_efficiency_percentage"
        )
        for record in records_to_use
    ]

    consistency = [
        record.get(
            "sleep_consistency_percentage"
        )
        for record in records_to_use
    ]

    respiratory_rate = [
        record.get("respiratory_rate")
        for record in records_to_use
    ]

    latest = records_to_use[0]

    return {
        "records_analyzed": len(records_to_use),
        "latest_date": latest.get("date"),
        "latest_sleep_performance": latest.get(
            "sleep_performance_percentage"
        ),
        "average_sleep_performance": _safe_mean(
            performance
        ),
        "average_sleep_efficiency": _safe_mean(
            efficiency
        ),
        "average_sleep_consistency": _safe_mean(
            consistency
        ),
        "average_respiratory_rate": _safe_mean(
            respiratory_rate
        ),
    }
def calculate_cycle_summary(
    records: list[dict],
) -> dict:
    if not records:
        return {
            "records_analyzed": 0,
            "message": "No cycle data available.",
        }

    strain = [
        record.get("strain")
        for record in records
    ]

    average_hr = [
        record.get("average_heart_rate")
        for record in records
    ]

    max_hr = [
        record.get("max_heart_rate")
        for record in records
    ]

    latest = records[0]

    return {
        "records_analyzed": len(records),
        "latest_date": latest.get("date"),
        "latest_strain": latest.get("strain"),
        "average_strain": _safe_mean(strain),
        "highest_strain": _safe_max(strain),
        "average_heart_rate": _safe_mean(
            average_hr
        ),
        "highest_max_heart_rate": _safe_max(
            max_hr
        ),
    }
def calculate_workout_summary(
    records: list[dict],
) -> dict:
    if not records:
        return {
            "workout_count": 0,
            "message": "No workout data available.",
        }

    strain = [
        record.get("strain")
        for record in records
    ]

    return {
        "workout_count": len(records),
        "average_workout_strain": _safe_mean(
            strain
        ),
        "highest_workout_strain": _safe_max(
            strain
        ),
        "recent_activities": [
            {
                "date": record.get("date"),
                "sport_name": record.get(
                    "sport_name"
                ),
                "strain": record.get("strain"),
                "average_heart_rate":
                    record.get(
                        "average_heart_rate"
                    ),
                "max_heart_rate":
                    record.get(
                        "max_heart_rate"
                    ),
            }
            for record in records[:5]
        ],
    }

def build_weekly_health_summary(
    recovery_records: list[dict],
    sleep_records: list[dict],
    cycle_records: list[dict],
    workout_records: list[dict],
) -> dict:
    return {
        "recovery": calculate_recovery_summary(
            recovery_records
        ),
        "sleep": calculate_sleep_summary(
            sleep_records
        ),
        "activity": calculate_cycle_summary(
            cycle_records
        ),
        "workouts": calculate_workout_summary(
            workout_records
        ),
    }