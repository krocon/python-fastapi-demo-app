"""
Storage abstraction for tasks.
Swap the implementation (e.g. for a database) without touching the routes.
"""

from typing import Protocol

from app.tasks.task import Task, UpdateTaskRequest


class TaskRepository(Protocol):
    async def find_all(self, done: bool | None = None) -> list[Task]: ...

    async def find_by_id(self, task_id: int) -> Task | None: ...

    async def create(self, title: str) -> Task: ...

    async def update(self, task_id: int, request: UpdateTaskRequest) -> Task | None: ...

    async def delete(self, task_id: int) -> bool: ...
