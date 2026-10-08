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
    Calculate an explainable multi-factor task priority.

    Priority factors:

    1. Deadline urgency       - 20 points
    2. Urgency indicators     - 15 points
    3. Importance             - 15 points
    4. Criticality / CVR      - 20 points
    5. Consequence / impact   - 20 points
    6. Explicit priority      - 10 points

    Total possible score: 100.

    The model is intentionally explainable so that every priority
    decision can be shown to the user.
    """

    text = title.lower()

    # ---------------------------------------------------------
    # 1. DEADLINE URGENCY — maximum 20
    # ---------------------------------------------------------

    deadline_score = 0
    deadline_reason = "No deadline urgency detected"

    if deadline:
        try:
            deadline_date = datetime.strptime(
                deadline,
                "%Y-%m-%d",
            ).date()

            today = datetime.now().date()
            days_remaining = (
                deadline_date - today
            ).days

            if days_remaining < 0:
                deadline_score = 20
                deadline_reason = "Task is overdue"

            elif days_remaining == 0:
                deadline_score = 20
                deadline_reason = "Deadline is today"

            elif days_remaining <= 2:
                deadline_score = 17
                deadline_reason = "Deadline is within 2 days"

            elif days_remaining <= 5:
                deadline_score = 13
                deadline_reason = "Deadline is within 5 days"

            elif days_remaining <= 7:
                deadline_score = 9
                deadline_reason = "Deadline is within 7 days"

            elif days_remaining <= 14:
                deadline_score = 5
                deadline_reason = "Deadline is within 14 days"

            else:
                deadline_score = 0
                deadline_reason = "Deadline is not immediately urgent"

        except ValueError:
            deadline_reason = "Deadline format could not be evaluated"

    # ---------------------------------------------------------
    # 2. URGENCY — maximum 15
    # ---------------------------------------------------------

    urgency_score = 0
    urgency_reason = "No explicit urgency indicators"

    if any(
        word in text
        for word in [
            "emergency",
            "immediately",
            "asap",
            "urgent",
            "critical",
            "now",
        ]
    ):
        urgency_score = 15
        urgency_reason = "Strong urgency indicators detected"

    elif any(
        word in text
        for word in [
            "priority",
            "time-sensitive",
            "immediate",
            "today",
        ]
    ):
        urgency_score = 10
        urgency_reason = "Moderate urgency indicators detected"

    elif any(
        word in text
        for word in [
            "soon",
            "promptly",
        ]
    ):
        urgency_score = 6
        urgency_reason = "Mild urgency indicators detected"

    # ---------------------------------------------------------
    # 3. IMPORTANCE — maximum 15
    # ---------------------------------------------------------

    importance_score = 0
    importance_reason = "No strong importance indicators detected"

    if any(
        word in text
        for word in [
            "mandatory",
            "required",
            "must",
            "compliance",
            "deadline",
            "approval",
        ]
    ):
        importance_score = 15
        importance_reason = "Task appears mandatory or business-important"

    elif any(
        word in text
        for word in [
            "assigned",
            "onboarding",
            "review",
            "assessment",
            "registration",
        ]
    ):
        importance_score = 10
        importance_reason = "Task appears important to the workflow"

    elif any(
        word in text
        for word in [
            "complete",
            "submit",
            "update",
        ]
    ):
        importance_score = 5
        importance_reason = "Task contains an actionable requirement"

    # ---------------------------------------------------------
    # 4. CRITICALITY / CVR — maximum 20
    # ---------------------------------------------------------

    criticality_score = 0
    criticality_reason = "No criticality indicators detected"

    if any(
        word in text
        for word in [
            "production",
            "outage",
            "incident",
            "security breach",
            "critical",
            "system failure",
            "service disruption",
        ]
    ):
        criticality_score = 20
        criticality_reason = (
            "High criticality/CVR indicators detected"
        )

    elif any(
        word in text
        for word in [
            "security",
            "infrastructure",
            "access",
            "monitoring",
            "change",
            "availability",
        ]
    ):
        criticality_score = 14
        criticality_reason = (
            "Operational or security criticality detected"
        )

    elif any(
        word in text
        for word in [
            "cloud",
            "network",
            "server",
            "database",
        ]
    ):
        criticality_score = 8
        criticality_reason = (
            "Technical-system criticality detected"
        )

    # ---------------------------------------------------------
    # 5. CONSEQUENCE / IMPACT — maximum 20
    # ---------------------------------------------------------

    consequence_score = 0
    consequence_reason = "Low or unspecified consequence"

    if any(
        word in text
        for word in [
            "outage",
            "failure",
            "breach",
            "data loss",
            "production",
            "service disruption",
            "blocked",
        ]
    ):
        consequence_score = 20
        consequence_reason = (
            "Potentially severe operational consequence"
        )

    elif any(
        word in text
        for word in [
            "access",
            "security",
            "incident",
            "infrastructure",
            "deployment",
            "change",
        ]
    ):
        consequence_score = 14
        consequence_reason = (
            "Potential operational or security consequence"
        )

    elif any(
        word in text
        for word in [
            "compliance",
            "mandatory",
            "approval",
            "assessment",
        ]
    ):
        consequence_score = 8
        consequence_reason = (
            "Potential business or compliance consequence"
        )

    # ---------------------------------------------------------
    # 6. EXPLICIT PRIORITY — maximum 10
    # ---------------------------------------------------------

    explicit_score = 0
    explicit_reason = "No explicit priority supplied"

    if explicit_priority:
        priority = explicit_priority.lower().strip()

        if priority == "critical":
            explicit_score = 10
            explicit_reason = "Explicitly marked critical"

        elif priority == "high":
            explicit_score = 8
            explicit_reason = "Explicitly marked high priority"

        elif priority == "medium":
            explicit_score = 5
            explicit_reason = "Explicitly marked medium priority"

        elif priority == "low":
            explicit_score = 2
            explicit_reason = "Explicitly marked low priority"

    # ---------------------------------------------------------
    # FINAL SCORE
    # ---------------------------------------------------------

    score = (
        deadline_score
        + urgency_score
        + importance_score
        + criticality_score
        + consequence_score
        + explicit_score
    )

    # Keep score safely within 0–100.
    score = min(score, 100)

    # ---------------------------------------------------------
    # FINAL PRIORITY
    # ---------------------------------------------------------

    if score >= 75:
        priority = "critical"

    elif score >= 50:
        priority = "high"

    elif score >= 25:
        priority = "medium"

    else:
        priority = "low"

    # ---------------------------------------------------------
    # EXPLAINABLE REASON
    # ---------------------------------------------------------

    reasons = [
        deadline_reason,
        urgency_reason,
        importance_reason,
        criticality_reason,
        consequence_reason,
        explicit_reason,
    ]

    priority_reason = "; ".join(
        reason
        for reason in reasons
        if reason
    )

    return {
        "priority": priority,
        "priority_score": score,
        "priority_reason": priority_reason,
        "factor_scores": {
            "deadline_urgency": deadline_score,
            "urgency": urgency_score,
            "importance": importance_score,
            "criticality_cvr": criticality_score,
            "consequence_impact": consequence_score,
            "explicit_priority": explicit_score,
        },
    }
