from typing import Dict, Optional

from sqlmodel import Session, select

from backend.database import engine
from backend.models import Task
from backend.services.metrics import increment
from backend.services.task_engine import (
    classify_task,
    calculate_priority,
)


def ingest_item(item: Dict) -> Optional[Dict]:
    """
    Common ContextFlow ingestion pipeline.

    Used by:
    - Outlook
    - Microsoft Teams
    - ServiceNow

    Handles:
    - validation
    - duplicate detection
    - source-change detection
    - classification
    - deadline extraction/preservation
    - dynamic priority calculation
    - task creation
    - task updates
    - observability metrics
    - source information
    """

    increment("items_scanned")

    required_fields = [
        "source",
        "source_id",
        "title",
        "content",
        "source_url",
    ]

    for field in required_fields:
        if field not in item:
            return None

    classification = classify_task(item["title"])

    deadline = item.get("deadline")

    priority_result = calculate_priority(
        title=item["title"],
        deadline=deadline,
        explicit_priority=item.get("priority"),
    )

    with Session(engine) as session:

        existing_task = session.exec(
            select(Task).where(
                Task.source == item["source"],
                Task.source_id == item["source_id"],
            )
        ).first()

        # ---------------------------------------------------------
        # EXISTING TASK
        # ---------------------------------------------------------

        if existing_task:

            changed = (
                existing_task.title != item["title"]
                or existing_task.description != item["content"]
                or existing_task.deadline != deadline
                or existing_task.priority
                != priority_result["priority"]
                or existing_task.category
                != classification["category"]
                or existing_task.link != item["source_url"]
            )

            # No source-side change.
            if not changed:
                increment("duplicates_avoided")
                return None

            # Update source-derived fields.
            # User-controlled lifecycle status is preserved.
            existing_task.title = item["title"]
            existing_task.description = item["content"]
            existing_task.deadline = deadline
            existing_task.priority = priority_result["priority"]
            existing_task.category = classification["category"]
            existing_task.confidence = classification["confidence"]
            existing_task.link = item["source_url"]

            session.add(existing_task)
            session.commit()
            session.refresh(existing_task)

            if priority_result["priority"] == "critical":
                increment("critical_tasks")

            return {
                "task_id": existing_task.task_id,
                "title": existing_task.title,
                "source": existing_task.source,
                "source_id": existing_task.source_id,
                "link": existing_task.link,
                "deadline": existing_task.deadline,
                "priority": priority_result["priority"],
                "priority_score": priority_result["priority_score"],
                "priority_reason": priority_result["priority_reason"],
                "category": existing_task.category,
                "confidence": existing_task.confidence,
                "action_url": item.get("action_url"),
                "updated": True,
            }

        # ---------------------------------------------------------
        # NEW TASK
        # ---------------------------------------------------------

        task = Task(
            task_id=(
                f"CF-{item['source'].lower().replace(' ', '-')}"
                f"-{item['source_id']}"
            ),
            title=item["title"],
            description=item["content"],
            deadline=deadline,
            priority=priority_result["priority"],
            category=classification["category"],
            confidence=classification["confidence"],
            status="READY",
            source=item["source"],
            source_id=item["source_id"],
            link=item["source_url"],
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        increment("tasks_detected")

        if priority_result["priority"] == "critical":
            increment("critical_tasks")

        return {
            "task_id": task.task_id,
            "title": task.title,
            "source": task.source,
            "source_id": task.source_id,
            "link": task.link,
            "deadline": task.deadline,
            "priority": priority_result["priority"],
            "priority_score": priority_result["priority_score"],
            "priority_reason": priority_result["priority_reason"],
            "category": task.category,
            "confidence": task.confidence,
            "action_url": item.get("action_url"),
            "updated": False,
        }
