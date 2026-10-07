"""Plain unit tests – no web server involved. Async functions run via asyncio.run()."""

import asyncio

import pytest

from app.tasks.in_memory_task_repository import InMemoryTaskRepository
from app.tasks.task import Task, UpdateTaskRequest


@pytest.fixture
def repository() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


def test_ids_are_assigned_sequentially(repository):
    first = asyncio.run(repository.create("First"))
    second = asyncio.run(repository.create("Second"))

    assert first.id == 1
    assert second.id == 2


def test_update_only_changes_the_given_fields(repository):
    task = asyncio.run(repository.create("Original"))

    updated = asyncio.run(repository.update(task.id, UpdateTaskRequest(done=True)))

    assert updated == Task(id=task.id, title="Original", done=True)


def test_update_of_unknown_id_returns_none(repository):
    assert asyncio.run(repository.update(99, UpdateTaskRequest(title="Nope"))) is None


def test_delete_returns_whether_a_task_was_removed(repository):
    task = asyncio.run(repository.create("To delete"))

    assert asyncio.run(repository.delete(task.id)) is True
    assert asyncio.run(repository.delete(task.id)) is False
