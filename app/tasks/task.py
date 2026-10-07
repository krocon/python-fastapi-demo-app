"""Data models (DTOs) – Pydantic turns them into JSON and back."""

from pydantic import BaseModel

from app.tasks.validation import Title


class Task(BaseModel):
    """A single to-do item."""

    id: int
    title: str
    done: bool = False


class CreateTaskRequest(BaseModel):
    """Body of POST /tasks."""

    title: Title


class UpdateTaskRequest(BaseModel):
    """Body of PATCH /tasks/{id}. Only fields that are set get updated."""

    title: Title | None = None
    done: bool | None = None
