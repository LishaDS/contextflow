from pydantic import BaseModel
from typing import Optional


class Task(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    status: str = "READY"
    source: Optional[str] = None
    link: Optional[str] = None