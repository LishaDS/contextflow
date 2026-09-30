from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class ReminderRequest(BaseModel):
    title: str
    message: str
    deadline: str | None = None


@router.post("/reminders")
def create_reminder(reminder: ReminderRequest):

    return {
        "status": "REMINDER_CREATED",
        "title": reminder.title,
        "message": reminder.message,
        "deadline": reminder.deadline,
    }
