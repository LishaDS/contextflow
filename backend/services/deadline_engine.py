from datetime import datetime
from typing import Optional


def get_days_remaining(deadline: Optional[str]) -> Optional[int]:
    """
    Return the number of days remaining until the deadline.
    """

    if not deadline:
        return None

    try:
        deadline_date = datetime.strptime(
            deadline,
            "%Y-%m-%d"
        ).date()

        today = datetime.now().date()

        return (deadline_date - today).days

    except ValueError:
        return None


def get_deadline_status(
    deadline: Optional[str],
    status: str = "READY"
) -> str:
    """
    Determine the current deadline status.
    """

    if status == "COMPLETED":
        return "Completed"

    days_remaining = get_days_remaining(deadline)

    if days_remaining is None:
        return "No deadline"

    if days_remaining < 0:
        return "Overdue"

    if days_remaining == 0:
        return "Due Today"

    if days_remaining <= 2:
        return "Due Soon"

    return "On Track"


def get_deadline_priority(
    deadline: Optional[str],
    status: str = "READY"
) -> Optional[str]:
    """
    Dynamically escalate priority based on deadline proximity.
    """

    if status == "COMPLETED":
        return None

    days_remaining = get_days_remaining(deadline)

    if days_remaining is None:
        return None

    if days_remaining <= 0:
        return "critical"

    if days_remaining <= 2:
        return "high"

    if days_remaining <= 5:
        return "medium"

    return "low"


def get_reminder_message(
    deadline: Optional[str],
    status: str = "READY"
) -> str:
    """
    Generate a human-readable reminder message.
    """

    if status == "COMPLETED":
        return "Task completed"

    days_remaining = get_days_remaining(deadline)

    if days_remaining is None:
        return "No deadline set"

    if days_remaining < 0:
        return (
            f"Overdue by {abs(days_remaining)} day(s)"
        )

    if days_remaining == 0:
        return "Due today"

    if days_remaining == 1:
        return "1 day remaining"

    return f"{days_remaining} days remaining"