from fastapi import FastAPI
from sqlmodel import Session
from uuid import uuid4

from .models import Task
from .database import create_db_and_tables, engine

app = FastAPI(title="ContextFlow API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "ContextFlow backend is running!"}


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