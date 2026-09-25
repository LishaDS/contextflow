from fastapi import FastAPI
from sqlmodel import Session, select
from uuid import uuid4
from fastapi.responses import FileResponse
import re

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

    task.task_id = (
        f"T-{str(uuid4())[:8].upper()}"
    )

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

        task = session.get(
            Task,
            task_id
        )

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

    tasks = []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        context
    )

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        lower_sentence = sentence.lower()

        if any(
            word in lower_sentence
            for word in [
                "complete",
                "attend",
                "submit",
                "finish",
                "review"
            ]
        ):

            tasks.append({
                "title": sentence,
                "source": "Synthetic context"
            })

    return {
        "message": "Context analyzed successfully",
        "tasks": tasks
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