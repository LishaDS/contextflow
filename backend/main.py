from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import re
import uuid

from backend.database import engine, create_db_and_tables
from backend.models import Task


app = FastAPI(title="ContextFlow API")


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

create_db_and_tables()


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    deadline: str | None = None
    priority: str = "medium"
    source: str | None = None
    link: str | None = None
    depends_on: str | None = None


class ContextRequest(BaseModel):
    context: str


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def generate_task_id():
    return "T-" + str(uuid.uuid4())[:8].upper()


def normalize_title(title: str) -> str:
    title = title.lower().strip()

    # Remove polite prefixes
    title = re.sub(r"^(please|kindly)\s+", "", title)

    # Remove punctuation
    title = re.sub(r"[^\w\s]", "", title)

    # Compress spaces
    title = re.sub(r"\s+", " ", title).strip()

    return title


def extract_date(text: str):
    pattern = (
        r"\b(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d{1,2})\b"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    month = match.group(1)
    day = match.group(2)

    try:
        date_obj = datetime.strptime(
            f"{month} {day} 2026",
            "%B %d %Y"
        )

        return date_obj.strftime("%Y-%m-%d")

    except ValueError:
        return None


def extract_url(text: str):
    match = re.search(
        r"https?://[^\s]+",
        text
    )

    if not match:
        return None

    return match.group(0).rstrip(".,)")


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
    ]

    sentence_lower = sentence.lower()

    for phrase in supporting_phrases:

        if phrase in sentence_lower:
            return True

    return False


def is_action_sentence(sentence: str) -> bool:

    sentence_lower = sentence.lower().strip()

    # Supporting sentences should not become
    # separate tasks.
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
    }

    return values.get(
        priority.lower(),
        2
    )


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "ContextFlow backend is running!"
    }


# ---------------------------------------------------------
# Create task
# ---------------------------------------------------------

@app.post("/tasks")
def create_task(task_data: TaskCreate):

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

    return tasks


# ---------------------------------------------------------
# Complete task
# ---------------------------------------------------------

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str):

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

        # Check dependency
        if task.depends_on:

            dependency = session.get(
                Task,
                task.depends_on
            )

            if dependency and dependency.status != "COMPLETED":

                raise HTTPException(
                    status_code=400,
                    detail=f"Task is blocked by {dependency.task_id}"
                )

        task.status = "COMPLETED"

        session.add(task)
        session.commit()
        session.refresh(task)

    return task


# ---------------------------------------------------------
# Context Analyzer
# ---------------------------------------------------------

@app.post("/analyze-context")
def analyze_context(request: ContextRequest):

    context = request.context.strip()

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

            # -------------------------------------------------
            # Supporting information
            # -------------------------------------------------
            #
            # Example:
            #
            # "Please attend the workshop."
            #
            # "The workshop must be completed by October 5."
            #
            # The second sentence should enrich the first task.
            # -------------------------------------------------

            if is_supporting_sentence(sentence):

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

                        # Add deadline
                        if (
                            deadline
                            and not previous_task.deadline
                        ):

                            previous_task.deadline = deadline
                            changed = True

                        # Add resource link
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

            # -------------------------------------------------
            # Ignore non-action sentences
            # -------------------------------------------------

            if not is_action_sentence(sentence):
                continue

            # -------------------------------------------------
            # Extract task information
            # -------------------------------------------------

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

            normalized_new_title = normalize_title(
                title
            )

            # -------------------------------------------------
            # Duplicate detection
            # -------------------------------------------------

            existing_tasks = session.exec(
                select(Task)
            ).all()

            duplicate = None

            for existing in existing_tasks:

                if (
                    normalize_title(existing.title)
                    == normalized_new_title
                ):

                    duplicate = existing
                    break

            # -------------------------------------------------
            # Duplicate enrichment
            # -------------------------------------------------

            if duplicate:

                changed = False

                # Add newly discovered deadline
                if (
                    deadline
                    and not duplicate.deadline
                ):

                    duplicate.deadline = deadline
                    changed = True

                # Add newly discovered link
                if (
                    link
                    and not duplicate.link
                ):

                    duplicate.link = link
                    changed = True

                # Upgrade priority
                if (
                    priority_value(priority)
                    > priority_value(duplicate.priority)
                ):

                    duplicate.priority = priority
                    changed = True

                # Add dependency
                if (
                    previous_task_id
                    and not duplicate.depends_on
                ):

                    duplicate.depends_on = previous_task_id
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

                previous_task_id = duplicate.task_id

                continue

            # -------------------------------------------------
            # Dependency detection
            # -------------------------------------------------

            depends_on = None

            sentence_lower = sentence.lower()

            if (
                sentence_lower.startswith("after ")
                or "after completing" in sentence_lower
                or "after finishing" in sentence_lower
            ):

                depends_on = previous_task_id

            # -------------------------------------------------
            # Create new task
            # -------------------------------------------------

            task = Task(
                task_id=generate_task_id(),
                title=title,
                description=(
                    "Automatically extracted from "
                    "synthetic context"
                ),
                deadline=deadline,
                priority=priority,
                status="READY",
                source="ContextFlow Context Analyzer",
                link=link,
                depends_on=depends_on,
            )

            session.add(task)

            session.commit()

            session.refresh(task)

            created_tasks.append(
                task
            )

            previous_task_id = task.task_id

    return {
        "message": "Context analyzed successfully",
        "created_tasks": created_tasks,
        "duplicate_tasks": duplicate_tasks,
        "tasks": created_tasks,
    }


# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Context page
# ---------------------------------------------------------

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