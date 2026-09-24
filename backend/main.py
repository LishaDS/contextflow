from fastapi import FastAPI
from .models import Task
from uuid import uuid4

app = FastAPI(title="ContextFlow API")


@app.get("/")
def root():
    return {"message": "ContextFlow backend is running!"}


@app.post("/tasks")
def create_task(task: Task):
    task.task_id = f"T-{str(uuid4())[:8].upper()}"

    return {
        "message": "Task created successfully",
        "task": task
    }