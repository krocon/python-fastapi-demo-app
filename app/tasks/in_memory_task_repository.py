"""
In-memory implementation of TaskRepository. Data is lost on restart.

No locks needed: asyncio runs one coroutine at a time, and none of these
methods awaits anything, so each call finishes before the next one starts.
"""

from itertools import count
from typing import Self

from app.tasks.task import Task, UpdateTaskRequest


class InMemoryTaskRepository:

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = count(1)

    async def find_all(self, done: bool | None = None) -> list[Task]:
        return sorted(
            (task for task in self._tasks.values() if done is None or task.done == done),
            key=lambda task: task.id,
        )

    async def find_by_id(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    async def create(self, title: str) -> Task:
        return self._add(title)

    def _add(self, title: str) -> Task:
        task = Task(id=next(self._next_id), title=title.strip())
        self._tasks[task.id] = task
        return task

    async def update(self, task_id: int, request: UpdateTaskRequest) -> Task | None:
        existing = self._tasks.get(task_id)
        if existing is None:
            return None
        changes = request.model_dump(exclude_none=True)
        if "title" in changes:
            changes["title"] = changes["title"].strip()
        updated = existing.model_copy(update=changes)
        self._tasks[task_id] = updated
        return updated

    async def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None

    @classmethod
    def with_sample_data(cls) -> Self:
        """A repository pre-filled with a few tasks, handy for demos."""
        repository = cls()
        repository._add("Learn Python")
        repository._add("Build a FastAPI API")
        repository._add("Record a one-minute video")
        return repository
