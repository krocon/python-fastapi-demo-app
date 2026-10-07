"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.tasks.in_memory_task_repository import InMemoryTaskRepository
from app.tasks.task_repository import TaskRepository


@pytest.fixture
def make_client():
    """Returns a function that starts the app with the given (default: empty) repository."""

    def factory(repository: TaskRepository | None = None) -> TestClient:
        return TestClient(create_app(repository or InMemoryTaskRepository()))

    return factory


@pytest.fixture
def client(make_client) -> TestClient:
    return make_client()
