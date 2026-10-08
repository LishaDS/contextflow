from typing import Dict


_metrics: Dict[str, int] = {
    "items_scanned": 0,
    "tasks_detected": 0,
    "duplicates_avoided": 0,
    "critical_tasks": 0,
    "notifications_sent": 0,
    "tasks_completed": 0,
    "sync_failures": 0,
}


def increment(metric: str, amount: int = 1) -> None:
    """Increment a ContextFlow metric."""

    if metric not in _metrics:
        _metrics[metric] = 0

    _metrics[metric] += amount


def get_metrics() -> Dict[str, int]:
    """Return a copy of the current metrics."""

    return dict(_metrics)


def reset_metrics() -> None:
    """Reset all metrics."""

    for key in _metrics:
        _metrics[key] = 0
