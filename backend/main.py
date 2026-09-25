from fastapi import FastAPI
from sqlmodel import Session, select
from uuid import uuid4
from fastapi.responses import FileResponse
import re
from datetime import datetime

from .models import Task
from .database import create_db_and_tables, engine


app = FastAPI(title="ContextFlow API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "message": "ContextFlow backend is running!"
    }


@app.post("/tasks")
def create_task(task: Task):

    task.task_id = f"T-{str(uuid4())[:8].upper()}"

    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    return {
        "message": "Task created successfully",
        "task": task
    }


@app.get("/tasks")
def get_tasks():

    with Session(engine) as session:
        tasks = session.exec(
            select(Task)
        ).all()

    return {
        "tasks": tasks
    }


@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str):

    with Session(engine) as session:

        task = session.get(Task, task_id)

        if not task:
            return {
                "error": "Task not found"
            }

        if task.depends_on:

            dependency = session.get(
                Task,
                task.depends_on
            )

            if dependency and dependency.status != "COMPLETED":

                return {
                    "error":
                        "Task is blocked by an incomplete dependency",
                    "depends_on":
                        task.depends_on
                }

        task.status = "COMPLETED"

        session.add(task)
        session.commit()
        session.refresh(task)

    return {
        "message": "Task completed successfully",
        "task": task
    }


@app.post("/analyze-context")
def analyze_context(data: dict):

    context = data.get("context", "").strip()

    if not context:
        return {
            "error": "No context provided"
        }

    sentences = re.split(
        r"(?<=[.!?])\s+",
        context
    )

    extracted_tasks = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        lower_sentence = sentence.lower()

        if not any(
            word in lower_sentence
            for word in [
                "complete",
                "attend",
                "submit",
                "finish",
                "review"
            ]
        ):
            continue

        deadline = None

        date_match = re.search(
            r"\b("
            r"January|February|March|April|May|June|"
            r"July|August|September|October|November|December"
            r")\s+(\d{1,2})\b",
            sentence,
            re.IGNORECASE
        )

        if date_match:

            month = date_match.group(1)
            day = int(date_match.group(2))

            current_year = datetime.now().year

            try:

                parsed_date = datetime.strptime(
                    f"{month} {day} {current_year}",
                    "%B %d %Y"
                )

                deadline = parsed_date.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:

                deadline = None

        extracted_tasks.append({
            "title": sentence,
            "deadline": deadline
        })

    created_tasks = []

    with Session(engine) as session:

        previous_task_id = None

        for item in extracted_tasks:

            title = item["title"]
            lower_title = title.lower()

            dependency = None

            # Detect simple sequential dependency.
            # Example:
            # "After completing the training,
            # attend the security assessment."

            if (
                previous_task_id
                and (
                    lower_title.startswith("after ")
                    or "after completing" in lower_title
                    or "after finishing" in lower_title
                )
            ):
                dependency = previous_task_id

            task = Task(

                task_id=f"T-{str(uuid4())[:8].upper()}",

                title=title,

                description=(
                    "Automatically extracted "
                    "from synthetic context"
                ),

                deadline=item["deadline"],

                priority="medium",

                status="READY",

                source="ContextFlow Context Analyzer",

                link=None,

                depends_on=dependency
            )

            session.add(task)

            created_tasks.append(task)

            previous_task_id = task.task_id

        session.commit()

        for task in created_tasks:
            session.refresh(task)

    return {
        "message":
            "Context analyzed and tasks created successfully",

        "tasks": created_tasks
    }


@app.get("/dashboard")
def dashboard():

    return FileResponse(
        "frontend/index.html"
    )


@app.get("/context")
def context_page():

    return FileResponse(
        "frontend/context.html"
    )