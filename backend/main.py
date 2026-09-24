from fastapi import FastAPI
from .models import Task

app = FastAPI(title="ContextFlow API")


@app.get("/")
def root():
    return {"message": "ContextFlow backend is running!"}


@app.post("/tasks")
def create_task(task: Task):
    return {
        "message": "Task created successfully",
        "task": task
    }