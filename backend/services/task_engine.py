from typing import Any


def classify_task(title: str) -> dict[str, Any]:
    text = title.lower()

    category = "general"

    if any(word in text for word in ["training", "course", "workshop"]):
        category = "learning"
    elif any(word in text for word in ["review", "audit", "compliance"]):
        category = "compliance"
    elif any(word in text for word in ["register", "registration", "form"]):
        category = "administrative"

    return {
        "category": category,
        "confidence": 0.9
    }
