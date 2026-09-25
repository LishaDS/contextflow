from sqlmodel import SQLModel, Field
from typing import Optional


class Task(SQLModel, table=True):

    task_id: str = Field(primary_key=True)

    title: str

    description: Optional[str] = None

    deadline: Optional[str] = None

    priority: str = "medium"

    status: str = "READY"

    source: Optional[str] = None

    link: Optional[str] = None

    depends_on: Optional[str] = None