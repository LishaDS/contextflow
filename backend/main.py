from fastapi import FastAPI
from sqlmodel import Session, select
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

@app.get("/tasks")
def get_tasks():
    with Session(engine) as session:
        tasks = session.exec(select(Task)).all()
    return {"tasks": tasks}


@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return {"error": "Task not found"}
        task.status = "COMPLETED"
        session.add(task)
        session.commit()
        session.refresh(task)
    return {"message": "Task completed successfully", "task": task}

from fastapi.responses import FileResponse

@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/index.html")

