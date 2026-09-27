from typing import Any

from backend.services.task_engine import classify_task


def analyze_context(context: str) -> dict[str, Any]:
    """
    ContextFlow AI analysis interface.
    """

    if not context or not context.strip():
        return {
            "status": "error",
            "message": "Context cannot be empty",
            "tasks": []
        }

    task_info = classify_task(context)

    return {
        "status": "ready",
        "provider": "rule-based-mvp",
        "tasks": [
            {
                "title": context.strip(),
                "category": task_info["category"],
                "confidence": task_info["confidence"]
            }
        ]
    }
