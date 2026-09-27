from typing import Any


def analyze_context(context: str) -> dict[str, Any]:
    """
    ContextFlow AI analysis interface.

    This service prepares a stable interface for a future LLM provider.
    The current MVP keeps execution deterministic and does not allow
    the AI layer to directly modify the database.
    """

    if not context or not context.strip():
        return {
            "status": "error",
            "message": "Context cannot be empty",
            "tasks": []
        }

    return {
        "status": "ready",
        "provider": "rule-based-mvp",
        "tasks": []
    }  
