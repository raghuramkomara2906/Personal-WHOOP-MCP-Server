def _round(value, digits=2):
    if isinstance(value, (int, float)):
        return round(value, digits)
    return value


def normalize_recovery_record(record: dict) -> dict:
    score = record.get("score") or {}
    created_at = record.get("created_at")

    return {
        "date": created_at[:10] if created_at else None,
        "recovery_score": score.get("recovery_score"),
        "resting_heart_rate": score.get("resting_heart_rate"),
        "hrv_ms": _round(score.get("hrv_rmssd_milli")),
        "spo2_percentage": _round(score.get("spo2_percentage")),
        "skin_temp_celsius": _round(score.get("skin_temp_celsius")),
        "score_state": record.get("score_state"),
    }


def normalize_recovery_collection(payload: dict) -> list[dict]:
    return [
        normalize_recovery_record(record)
        for record in payload.get("records", [])
    ]


def normalize_sleep_record(record: dict) -> dict:
    score = record.get("score") or {}
    stage_summary = score.get("stage_summary") or {}
    sleep_needed = score.get("sleep_needed") or {}

    start = record.get("start")
    end = record.get("end")

    return {
        "date": start[:10] if start else None,
        "start": start,
        "end": end,
        "nap": record.get("nap"),
        "score_state": record.get("score_state"),
        "sleep_performance_percentage": score.get(
            "sleep_performance_percentage"
        ),
        "sleep_consistency_percentage": score.get(
            "sleep_consistency_percentage"
        ),
        "sleep_efficiency_percentage": score.get(
            "sleep_efficiency_percentage"
        ),
        "respiratory_rate": _round(
            score.get("respiratory_rate")
        ),
        "time_in_bed_ms": stage_summary.get(
            "total_in_bed_time_milli"
        ),
        "awake_time_ms": stage_summary.get(
            "total_awake_time_milli"
        ),
        "light_sleep_ms": stage_summary.get(
            "total_light_sleep_time_milli"
        ),
        "deep_sleep_ms": stage_summary.get(
            "total_slow_wave_sleep_time_milli"
        ),
        "rem_sleep_ms": stage_summary.get(
            "total_rem_sleep_time_milli"
        ),
        "disturbances": stage_summary.get(
            "disturbance_count"
        ),
        "sleep_need_ms": sleep_needed.get(
            "baseline_milli"
        ),
    }


def normalize_sleep_collection(payload: dict) -> list[dict]:
    return [
        normalize_sleep_record(record)
        for record in payload.get("records", [])
    ]


def normalize_cycle_record(record: dict) -> dict:
    score = record.get("score") or {}

    start = record.get("start")

    return {
        "date": start[:10] if start else None,
        "start": start,
        "end": record.get("end"),
        "score_state": record.get("score_state"),
        "strain": _round(score.get("strain")),
        "kilojoule": _round(score.get("kilojoule")),
        "average_heart_rate": score.get(
            "average_heart_rate"
        ),
        "max_heart_rate": score.get(
            "max_heart_rate"
        ),
        "step_count": score.get("step_count"),
    }


def normalize_cycle_collection(payload: dict) -> list[dict]:
    return [
        normalize_cycle_record(record)
        for record in payload.get("records", [])
    ]


def normalize_workout_record(record: dict) -> dict:
    score = record.get("score") or {}

    start = record.get("start")

    return {
        "date": start[:10] if start else None,
        "start": start,
        "end": record.get("end"),
        "sport_name": record.get("sport_name"),
        "sport_id": record.get("sport_id"),
        "score_state": record.get("score_state"),
        "strain": _round(score.get("strain")),
        "average_heart_rate": score.get(
            "average_heart_rate"
        ),
        "max_heart_rate": score.get(
            "max_heart_rate"
        ),
        "kilojoule": _round(score.get("kilojoule")),
        "distance_meter": _round(
            score.get("distance_meter")
        ),
        "altitude_gain_meter": _round(
            score.get("altitude_gain_meter")
        ),
    }


def normalize_workout_collection(payload: dict) -> list[dict]:
    return [
        normalize_workout_record(record)
        for record in payload.get("records", [])
    ]


def normalize_body_measurements(payload: dict) -> dict:
    return {
        "height_meter": _round(
            payload.get("height_meter")
        ),
        "weight_kilogram": _round(
            payload.get("weight_kilogram")
        ),
        "max_heart_rate": payload.get(
            "max_heart_rate"
        ),
    }