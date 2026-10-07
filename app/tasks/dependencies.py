"""
Dependency injection with Depends.

Routes declare `repository: RepositoryDep` and FastAPI hands in the instance
stored on app.state (see main.py). HTTPConnection works for HTTP *and* WebSocket.
"""

from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection

from app.tasks.task_event_bus import TaskEventBus
from app.tasks.task_repository import TaskRepository


def get_task_repository(connection: HTTPConnection) -> TaskRepository:
    return connection.app.state.task_repository


def get_event_bus(connection: HTTPConnection) -> TaskEventBus:
    return connection.app.state.event_bus


RepositoryDep = Annotated[TaskRepository, Depends(get_task_repository)]
EventBusDep = Annotated[TaskEventBus, Depends(get_event_bus)]
