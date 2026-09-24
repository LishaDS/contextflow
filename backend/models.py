from pydantic import BaseModel
from typing import Optional
from uuid import uuid4


class Task(BaseModel):
    task_id: str = ""
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    status: str = "READY"
    source: Optional[str] = None
    link: Optional[str] = None