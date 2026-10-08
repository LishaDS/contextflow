import asyncio
import json
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.database import engine, create_db_and_tables
from backend.models import Task
from backend.reminders import router as reminder_router
from backend.services.deadline_engine import (
    get_deadline_status,
    get_reminder_message,
    get_deadline_priority,
)
from backend.services.task_engine import classify_task
from backend.services.metrics import get_metrics, increment

from backend.connectors.sync import sync_outlook_items
from backend.connectors.teams_sync import sync_teams_items
from backend.connectors.servicenow_sync import sync_servicenow_items


# ---------------------------------------------------------
# Automatic synchronization scheduler
# ---------------------------------------------------------

SYNC_INTERVAL_SECONDS = 60


def run_all_syncs():

    outlook_tasks = sync_outlook_items()

    teams_tasks = sync_teams_items()

    servicenow_tasks = sync_servicenow_items()

    return {
        "Outlook": len(outlook_tasks),
        "Microsoft Teams": len(teams_tasks),
        "ServiceNow": len(servicenow_tasks),
        "created_tasks": (
            outlook_tasks
            + teams_tasks
            + servicenow_tasks
        ),
    }


async def automatic_sync_loop():

    while True:

        try:

            result = await asyncio.to_thread(
                run_all_syncs
            )

            print(
                "[ContextFlow Scheduler] "
                f"Sync completed: "
                f"Outlook={result['Outlook']}, "
                f"Teams={result['Microsoft Teams']}, "
                f"ServiceNow={result['ServiceNow']}"
            )

        except Exception as e:

            increment("sync_failures")

            print(
                "[ContextFlow Scheduler] "
                f"Sync failed: {e}"
            )

        await asyncio.sleep(
            SYNC_INTERVAL_SECONDS
        )


@asynccontextmanager
async def lifespan(app: FastAPI):

    scheduler_task = asyncio.create_task(
        automatic_sync_loop()
    )

    print(
        "[ContextFlow Scheduler] "
        "Automatic synchronization started."
    )

    try:

        yield

    finally:

        scheduler_task.cancel()

        try:

            await scheduler_task

        except asyncio.CancelledError:

            print(
                "[ContextFlow Scheduler] "
                "Automatic synchronization stopped."
            )


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------


app = FastAPI(
    title="ContextFlow API",
    lifespan=lifespan
)


app.include_router(
    reminder_router
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


create_db_and_tables()


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------


class TaskCreate(BaseModel):

    title: str
    description: str | None = None
    deadline: str | None = None
    priority: str = "medium"
    category: str = "general"
    confidence: float = 0.0
    source: str | None = None
    link: str | None = None
    depends_on: str | None = None


class ContextRequest(BaseModel):

    context: str


class TaskStatusUpdate(BaseModel):

    status: str


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------


def generate_task_id():

    return "T-" + str(
        uuid.uuid4()
    )[:8].upper()


def normalize_title(title: str) -> str:

    title = title.lower().strip()

    title = re.sub(
        r"^(please|kindly)\s+",
        "",
        title
    )

    title = re.sub(
        r"[^\w\s]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title


def extract_date(text: str):

    pattern = (
        r"\b(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d{1,2})"
        r"(?:,\s*(\d{4}))?\b"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:

        return None

    year = match.group(3)

    if not year:

        year = "2026"

    try:

        date_obj = datetime.strptime(
            f"{match.group(1)} {match.group(2)} {year}",
            "%B %d %Y"
        )

        return date_obj.strftime(
            "%Y-%m-%d"
        )

    except ValueError:

        return None


def extract_url(text: str):

    match = re.search(
        r"https?://[^\s]+",
        text
    )

    if not match:

        return None

    return match.group(0).rstrip(
        ".,)"
    )


def is_supporting_sentence(sentence: str) -> bool:

    supporting_phrases = [
        "must be completed",
        "must be submitted",
        "must be finished",
        "is due",
        "are due",
        "deadline",
        "due by",
        "due on",
        "available at",
        "available here",
        "resources are",
        "resource is",
        "required action:",
        "applications:",
    ]

    sentence_lower = sentence.lower()

    for phrase in supporting_phrases:

        if phrase in sentence_lower:

            return True

    return False


def is_action_sentence(sentence: str) -> bool:

    sentence_lower = sentence.lower().strip()

    if is_supporting_sentence(sentence):

        return False

    action_words = [
        "complete",
        "attend",
        "submit",
        "finish",
        "register",
        "review",
        "prepare",
        "upload",
        "download",
        "fill",
        "fill out",
        "apply",
        "join",
        "schedule",
        "create",
        "send",
        "read",
        "watch",
        "study",
        "perform",
        "check",
        "request",
        "requested",
        "required",
        "renew",
        "declare",
        "enroll",
        "enrollment",
        "access",
        "approval",
        "approve",
        "provide",
        "confirm",
        "update",
        "verify",
        "activate",
        "configure",
        "install",
        "raise",
        "raise a ticket",
        "open",
    ]

    for word in action_words:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            sentence_lower
        ):

            return True

    return False


def detect_priority(text: str) -> str:

    text_lower = text.lower()

    high_words = [
        "urgent",
        "critical",
        "immediately",
        "asap",
        "high priority",
        "emergency",
    ]

    low_words = [
        "optional",
        "when possible",
        "low priority",
        "whenever possible",
    ]

    for word in high_words:

        if word in text_lower:

            return "high"

    for word in low_words:

        if word in text_lower:

            return "low"

    return "medium"


def priority_value(priority: str) -> int:

    values = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    return values.get(
        priority.lower(),
        2
    )


# ---------------------------------------------------------
# Basic API
# ---------------------------------------------------------


@app.get("/")
def root():

    return {
        "message": "ContextFlow backend is running!"
    }


# ---------------------------------------------------------
# Task creation
# ---------------------------------------------------------


@app.post("/tasks")
def create_task(
    task_data: TaskCreate
):

    task_id = generate_task_id()

    task = Task(
        task_id=task_id,
        title=task_data.title,
        description=task_data.description,
        deadline=task_data.deadline,
        priority=task_data.priority,
        category=task_data.category,
        confidence=task_data.confidence,
        status="READY",
        source=task_data.source,
        link=task_data.link,
        depends_on=task_data.depends_on,
    )

    with Session(engine) as session:

        session.add(task)

        session.commit()

        session.refresh(task)

    return task


# ---------------------------------------------------------
# Get tasks
# ---------------------------------------------------------


@app.get("/tasks")
def get_tasks():

    with Session(engine) as session:

        tasks = session.exec(
            select(Task)
        ).all()

    result = []

    for task in tasks:

        task_data = task.model_dump()

        task_data["deadline_status"] = (
            get_deadline_status(
                task.deadline,
                task.status
            )
        )

        task_data["reminder_message"] = (
            get_reminder_message(
                task.deadline,
                task.status
            )
        )

        dynamic_priority = get_deadline_priority(
            task.deadline,
            task.status
        )

        if dynamic_priority:

            if (
                priority_value(dynamic_priority)
                > priority_value(task.priority)
            ):

                task_data["effective_priority"] = (
                    dynamic_priority
                )

            else:

                task_data["effective_priority"] = (
                    task.priority
                )

        else:

            task_data["effective_priority"] = (
                task.priority
            )

        priority_reasons = []

        if task.priority.lower() == "critical":

            priority_reasons.append(
                "Task is explicitly marked critical"
            )

        elif task.priority.lower() == "high":

            priority_reasons.append(
                "Task is explicitly marked high priority"
            )

        elif task.priority.lower() == "low":

            priority_reasons.append(
                "Task is explicitly marked low priority"
            )

        if task.deadline:

            if (
                task_data["deadline_status"]
                == "Overdue"
            ):

                priority_reasons.append(
                    "Task is overdue"
                )

            elif (
                task_data["deadline_status"]
                == "Due Today"
            ):

                priority_reasons.append(
                    "Deadline is today"
                )

            elif (
                task_data["deadline_status"]
                == "Due Soon"
            ):

                priority_reasons.append(
                    "Deadline is within 2 days"
                )

        if not priority_reasons:

            priority_reasons.append(
                "No immediate urgency detected"
            )

        task_data["priority_reason"] = (
            "; ".join(priority_reasons)
        )

        result.append(task_data)

    return result


# ---------------------------------------------------------
# Complete task
# ---------------------------------------------------------


@app.patch(
    "/tasks/{task_id}/complete"
)
def complete_task(
    task_id: str
):

    with Session(engine) as session:

        task = session.get(
            Task,
            task_id
        )

        if not task:

            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        if task.depends_on:

            dependency = session.get(
                Task,
                task.depends_on
            )

            if (
                dependency
                and dependency.status != "COMPLETED"
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Task is blocked by "
                        f"{dependency.task_id}"
                    )
                )

        task.status = "COMPLETED"

        session.add(task)

        session.commit()

        session.refresh(task)

    return task


# ---------------------------------------------------------
# Task status
# ---------------------------------------------------------


@app.patch(
    "/tasks/{task_id}/status"
)
def update_task_status(
    task_id: str,
    status_data: TaskStatusUpdate
):

    allowed_statuses = {
        "READY",
        "IN PROGRESS",
        "BLOCKED",
        "COMPLETED",
    }

    new_status = (
        status_data.status
        .strip()
        .upper()
    )

    if new_status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Allowed statuses: "
                "READY, IN PROGRESS, BLOCKED, COMPLETED"
            )
        )

    with Session(engine) as session:

        task = session.get(
            Task,
            task_id
        )

        if not task:

            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        if (
            new_status == "COMPLETED"
            and task.depends_on
        ):

            dependency = session.get(
                Task,
                task.depends_on
            )

            if (
                dependency
                and dependency.status != "COMPLETED"
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Task is blocked by "
                        f"{dependency.task_id}"
                    )
                )

        task.status = new_status

        session.add(task)

        session.commit()

        session.refresh(task)

    return task


# ---------------------------------------------------------
# Context analysis
# ---------------------------------------------------------


def analyze_context_logic(
    context: str
):

    context = context.strip()

    if not context:

        raise HTTPException(
            status_code=400,
            detail="Context cannot be empty"
        )

    sentences = re.split(
        r"(?<=[.!?])\s+",
        context
    )

    created_tasks = []

    duplicate_tasks = []

    previous_task_id = None

    with Session(engine) as session:

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:

                continue

            if is_supporting_sentence(
                sentence
            ):

                if previous_task_id:

                    previous_task = session.get(
                        Task,
                        previous_task_id
                    )

                    if previous_task:

                        deadline = extract_date(
                            sentence
                        )

                        link = extract_url(
                            sentence
                        )

                        changed = False

                        if (
                            deadline
                            and not previous_task.deadline
                        ):

                            previous_task.deadline = (
                                deadline
                            )

                            changed = True

                        if (
                            link
                            and not previous_task.link
                        ):

                            previous_task.link = link

                            changed = True

                        if changed:

                            session.add(
                                previous_task
                            )

                            session.commit()

                            session.refresh(
                                previous_task
                            )

                continue

            if not is_action_sentence(
                sentence
            ):

                continue

            title = sentence

            deadline = extract_date(
                sentence
            )

            link = extract_url(
                sentence
            )

            priority = detect_priority(
                sentence
            )

            normalized_new_title = (
                normalize_title(title)
            )

            existing_tasks = session.exec(
                select(Task)
            ).all()

            duplicate = None

            for existing in existing_tasks:

                if (
                    normalize_title(
                        existing.title
                    )
                    == normalized_new_title
                ):

                    duplicate = existing

                    break

            if duplicate:

                changed = False

                if (
                    deadline
                    and not duplicate.deadline
                ):

                    duplicate.deadline = deadline

                    changed = True

                if (
                    link
                    and not duplicate.link
                ):

                    duplicate.link = link

                    changed = True

                if (
                    priority_value(priority)
                    > priority_value(
                        duplicate.priority
                    )
                ):

                    duplicate.priority = priority

                    changed = True

                if (
                    previous_task_id
                    and not duplicate.depends_on
                ):

                    duplicate.depends_on = (
                        previous_task_id
                    )

                    changed = True

                if changed:

                    session.add(
                        duplicate
                    )

                    session.commit()

                    session.refresh(
                        duplicate
                    )

                duplicate_tasks.append(
                    duplicate
                )

                previous_task_id = (
                    duplicate.task_id
                )

                continue

            depends_on = None

            sentence_lower = (
                sentence.lower()
            )

            if (
                sentence_lower.startswith("after ")
                or "after completing"
                in sentence_lower
                or "after finishing"
                in sentence_lower
                or "after starting"
                in sentence_lower
                or "before starting"
                in sentence_lower
            ):

                depends_on = previous_task_id

            task_info = classify_task(
                title
            )

            task = Task(
                task_id=generate_task_id(),
                title=title,
                description=(
                    "Automatically extracted from "
                    "synthetic context"
                ),
                deadline=deadline,
                priority=priority,
                category=task_info["category"],
                confidence=task_info["confidence"],
                status="READY",
                source=(
                    "ContextFlow Context Analyzer"
                ),
                link=link,
                depends_on=depends_on,
            )

            session.add(task)

            session.commit()

            session.refresh(task)

            created_tasks.append(task)

            previous_task_id = task.task_id

    return {
        "message": (
            "Context analyzed successfully"
        ),
        "created_tasks": created_tasks,
        "duplicate_tasks": duplicate_tasks,
        "tasks": created_tasks,
    }


@app.post("/analyze-context")
def analyze_context(
    request: ContextRequest
):

    return analyze_context_logic(
        request.context
    )


@app.post(
    "/analyze-context-extension"
)
async def analyze_context_extension(
    request: Request
):

    try:

        body = await request.json()

        context = body.get(
            "context",
            ""
        )

    except Exception:

        raw_body = await request.body()

        try:

            data = json.loads(
                raw_body.decode("utf-8")
            )

            context = data.get(
                "context",
                ""
            )

        except Exception:

            context = raw_body.decode(
                "utf-8"
            )

    return analyze_context_logic(
        context
    )


# ---------------------------------------------------------
# Manual synchronization endpoints
# ---------------------------------------------------------


@app.post("/sync/outlook")
def sync_outlook():

    created_tasks = sync_outlook_items()

    return {
        "message": (
            "Outlook synchronization completed"
        ),
        "created_tasks": created_tasks,
        "created_count": len(
            created_tasks
        ),
    }


@app.post("/sync/teams")
def sync_teams():

    created_tasks = sync_teams_items()

    return {
        "message": (
            "Microsoft Teams synchronization completed"
        ),
        "created_tasks": created_tasks,
        "created_count": len(
            created_tasks
        ),
    }


@app.post("/sync/servicenow")
def sync_servicenow():

    created_tasks = sync_servicenow_items()

    return {
        "message": (
            "ServiceNow synchronization completed"
        ),
        "created_tasks": created_tasks,
        "created_count": len(
            created_tasks
        ),
    }


@app.post("/sync/all")
def sync_all():

    result = run_all_syncs()

    return {
        "message": (
            "ContextFlow synchronization completed"
        ),
        "created_tasks": result[
            "created_tasks"
        ],
        "created_count": len(
            result["created_tasks"]
        ),
        "sources": {
            "Outlook": result["Outlook"],
            "Microsoft Teams": result[
                "Microsoft Teams"
            ],
            "ServiceNow": result[
                "ServiceNow"
            ],
        },
    }


# ---------------------------------------------------------
@app.get("/metrics")
def metrics():
    return get_metrics()


@app.post("/metrics/notification")
def record_notification():
    increment("notifications_sent")
    return get_metrics()


@app.post("/metrics/completion")
def record_completion():
    increment("tasks_completed")
    return get_metrics()


# Dashboard
# ---------------------------------------------------------


@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard():

    dashboard_path = Path(
        "frontend/index.html"
    )

    if not dashboard_path.exists():

        return HTMLResponse(
            "<h1>Dashboard not found</h1>",
            status_code=404
        )

    return HTMLResponse(
        dashboard_path.read_text(
            encoding="utf-8"
        )
    )


@app.get(
    "/context",
    response_class=HTMLResponse
)
def context_page():

    context_path = Path(
        "frontend/context.html"
    )

    if not context_path.exists():

        return HTMLResponse(
            "<h1>Context page not found</h1>",
            status_code=404
        )

    return HTMLResponse(
        context_path.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------
# ContextFlow realistic enterprise demo pages
# ---------------------------------------------------------


MOCK_SITE_NAMES = {
    "outlook",
    "teams",
    "outlook-security",
    "outlook-epfo",
    "teams-assessment",
    "servicenow",
    "access-request",
    "hr-benefits",
    "security-training",
    "epfo",
    "cloud-assessment",
    "servicenow-form",
    "access-request-form",
    "benefits-form",
}


@app.get(
    "/mock/{site}",
    response_class=HTMLResponse
)
def mock_site(site: str):

    if site not in MOCK_SITE_NAMES:

        return HTMLResponse(
            "<h1>Demo page not found</h1>",
            status_code=404
        )

    mock_path = Path(
        "frontend/mock_sites.html"
    )

    if not mock_path.exists():

        return HTMLResponse(
            "<h1>Mock sites file not found</h1>",
            status_code=404
        )

    return HTMLResponse(
        mock_path.read_text(
            encoding="utf-8"
        )
    )