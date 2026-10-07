from typing import List, Dict, Optional
from datetime import datetime
import re

from backend.connectors.outlook import get_new_outlook_items
from backend.services.ingestion import ingest_item


def extract_deadline(text: str) -> Optional[str]:
    """
    Extract a deadline such as:
    'by October 10'
    'by October 12'
    'by October 15'

    If the year is not mentioned, use the current year.
    """

    if not text:
        return None

    pattern = r"\bby\s+([A-Za-z]+)\s+(\d{1,2})\b"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    month_name = match.group(1)
    day = int(match.group(2))

    try:
        year = datetime.now().year

        deadline = datetime.strptime(
            f"{month_name} {day} {year}",
            "%B %d %Y"
        )

        return deadline.strftime("%Y-%m-%d")

    except ValueError:
        return None


def normalize_outlook_item(item: Dict) -> Dict:
    """
    Convert an Outlook item into the common
    ContextFlow ingestion format.

    All important source information is preserved.
    """

    return {
        "source": item["source"],
        "source_id": item["source_id"],
        "title": item["title"],
        "content": item["content"],
        "source_url": item["source_url"],
        "action_url": item.get("action_url"),
        "deadline": extract_deadline(item["content"]),
    }


def sync_outlook_items() -> List[Dict]:
    """
    Synchronize Outlook items through the
    common ContextFlow ingestion pipeline.

    The common ingestion layer handles:
    - duplicate detection
    - task creation
    - classification
    - database storage
    """

    created_tasks = []

    outlook_items = get_new_outlook_items()

    for item in outlook_items:

        normalized_item = normalize_outlook_item(item)

        created_task = ingest_item(
            normalized_item
        )

        if created_task:
            created_tasks.append(
                created_task
            )

    return created_tasks