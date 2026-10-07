"""
Something that happened to a task. Sent to live clients as JSON, e.g.
{"type":"created","task":{"id":4,"title":"Try FastAPI","done":false}}

The `type` field is the discriminator of a tagged union – Pydantic picks
the right class when parsing.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter

from app.tasks.task import Task


class TaskCreated(BaseModel):
    type: Literal["created"] = "created"
    task: Task


class TaskUpdated(BaseModel):
    type: Literal["updated"] = "updated"
    task: Task


class TaskDeleted(BaseModel):
    type: Literal["deleted"] = "deleted"
    id: int


TaskEvent = Annotated[TaskCreated | TaskUpdated | TaskDeleted, Field(discriminator="type")]

# Parses JSON back into the right event class: task_event_adapter.validate_json(text)
task_event_adapter: TypeAdapter[TaskEvent] = TypeAdapter(TaskEvent)
