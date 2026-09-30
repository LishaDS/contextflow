from datetime import datetime


def get_deadline_status(deadline: str | None, status: str = "READY") -> str:
    if not deadline:
        return "No deadline"

    if status == "COMPLETED":
        return "Completed"

    try:
        due_date = datetime.strptime(deadline, "%Y-%m-%d").date()
        today = datetime.now().date()

        days_left = (due_date - today).days

        if days_left < 0:
            return "Overdue"

        if days_left == 0:
            return "Due Today"

        if days_left <= 2:
            return "Due Soon"

        return "On Track"

    except ValueError:
        return "Invalid Deadline"


def get_days_remaining(deadline: str | None) -> int | None:
    if not deadline:
        return None

    try:
        due_date = datetime.strptime(deadline, "%Y-%m-%d").date()
        today = datetime.now().date()

        return (due_date - today).days

    except ValueError:
        return None


def get_reminder_message(deadline: str | None, status: str = "READY") -> str:
    if status == "COMPLETED":
        return "Task completed"

    days_left = get_days_remaining(deadline)

    if days_left is None:
        return "No deadline set"

    if days_left < 0:
        return f"Overdue by {abs(days_left)} day(s)"

    if days_left == 0:
        return "Due today"

    if days_left == 1:
        return "Due tomorrow"

    if days_left <= 2:
        return f"{days_left} days remaining"

    return f"{days_left} days remaining"
