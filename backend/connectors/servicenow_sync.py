from typing import List, Dict, Optional
from datetime import datetime
import re

from backend.connectors.servicenow import get_new_servicenow_items
from backend.services.ingestion import ingest_item


def extract_deadline(text: str) -> Optional[str]:
    """
    Extract a deadline such as:
    'by October 14'
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


def normalize_servicenow_item(item: Dict) -> Dict:
    """
    Convert a ServiceNow item into the common
    ContextFlow ingestion format.
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


def sync_servicenow_items() -> List[Dict]:
    """
    Synchronize ServiceNow items through the
    common ContextFlow ingestion pipeline.
    """

    created_tasks = []

    servicenow_items = get_new_servicenow_items()

    for item in servicenow_items:

        normalized_item = normalize_servicenow_item(item)

        created_task = ingest_item(
            normalized_item
        )

        if created_task:
            created_tasks.append(
                created_task
            )

    return created_tasks