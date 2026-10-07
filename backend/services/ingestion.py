from typing import Dict, Optional

from sqlmodel import Session, select

from backend.database import engine
from backend.models import Task
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
    - classification
    - deadline preservation
    - dynamic priority calculation
    - task creation
    - source information
    """

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

    with Session(engine) as session:

        existing_task = session.exec(
            select(Task).where(
                Task.source == item["source"],
                Task.source_id == item["source_id"],
            )
        ).first()

        if existing_task:
            return None

        classification = classify_task(
            item["title"]
        )

        deadline = item.get("deadline")

        priority_result = calculate_priority(
            title=item["title"],
            deadline=deadline,
            explicit_priority=item.get("priority"),
        )

        task = Task(
            task_id=(
                f"CF-{item['source'].lower().replace(' ', '-')}"
                f"-{item['source_id']}"
            ),
            title=item["title"],
            description=item["content"],
            deadline=deadline,
            source=item["source"],
            source_id=item["source_id"],
            link=item["source_url"],
            status="READY",
            priority=priority_result["priority"],
            category=classification["category"],
            confidence=classification["confidence"],
        )

        session.add(task)
        session.commit()
        session.refresh(task)

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
        }