from typing import Any, Optional
from datetime import datetime


def classify_task(title: str) -> dict[str, Any]:
    """
    Classify a task based on its title.
    """

    text = title.lower()

    category = "general"

    if any(
        word in text
        for word in [
            "training",
            "course",
            "workshop",
            "assessment",
        ]
    ):
        category = "learning"

    elif any(
        word in text
        for word in [
            "review",
            "audit",
            "compliance",
        ]
    ):
        category = "compliance"

    elif any(
        word in text
        for word in [
            "register",
            "registration",
            "form",
            "declaration",
            "enrollment",
        ]
    ):
        category = "administrative"

    elif any(
        word in text
        for word in [
            "access",
            "infrastructure",
            "monitoring",
            "cloud",
        ]
    ):
        category = "technical"

    return {
        "category": category,
        "confidence": 0.9,
    }


def calculate_priority(
    title: str,
    deadline: Optional[str] = None,
    explicit_priority: Optional[str] = None,
) -> dict[str, Any]:
    """
    Calculate an explainable task priority.

    Factors:
    - explicit priority
    - deadline proximity
    - critical/urgent wording
    - operational/technical impact
    """

    text = title.lower()

    score = 0
    reasons = []

    # Explicit priority
    if explicit_priority:
        priority = explicit_priority.lower()

        if priority == "critical":
            score += 100
            reasons.append("Explicitly marked critical")

        elif priority == "high":
            score += 70
            reasons.append("Explicitly marked high priority")

        elif priority == "medium":
            score += 40
            reasons.append("Explicitly marked medium priority")

    # Urgency keywords
    if any(
        word in text
        for word in [
            "urgent",
            "critical",
            "immediately",
            "asap",
        ]
    ):
        score += 50
        reasons.append("Urgency indicated by task wording")

    # Operational impact
    if any(
        word in text
        for word in [
            "infrastructure",
            "access",
            "security",
            "production",
            "incident",
            "change",
        ]
    ):
        score += 25
        reasons.append("Potential operational impact")

    # Deadline proximity
    if deadline:
        try:
            deadline_date = datetime.strptime(
                deadline,
                "%Y-%m-%d"
            ).date()

            today = datetime.now().date()
            days_remaining = (
                deadline_date - today
            ).days

            if days_remaining < 0:
                score += 100
                reasons.append("Task is overdue")

            elif days_remaining == 0:
                score += 90
                reasons.append("Due today")

            elif days_remaining <= 2:
                score += 70
                reasons.append(
                    "Deadline is within 2 days"
                )

            elif days_remaining <= 5:
                score += 45
                reasons.append(
                    "Deadline is within 5 days"
                )

            elif days_remaining <= 7:
                score += 25
                reasons.append(
                    "Deadline is within 7 days"
                )

        except ValueError:
            pass

    # Convert score to priority
    if score >= 100:
        priority = "critical"

    elif score >= 70:
        priority = "high"

    elif score >= 40:
        priority = "medium"

    else:
        priority = "low"

    if not reasons:
        reasons.append(
            "No immediate urgency or high-impact indicators detected"
        )

    return {
        "priority": priority,
        "priority_score": score,
        "priority_reason": "; ".join(reasons),
    }