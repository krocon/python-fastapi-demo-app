"""Route tests: the whole app runs in-process via FastAPI's TestClient."""

import asyncio

from app.tasks.in_memory_task_repository import InMemoryTaskRepository
from app.tasks.task import UpdateTaskRequest


def test_root_returns_hello(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Hello, FastAPI!" in response.text
    assert 'href="/live/"' in response.text


def test_health_check_is_up(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_and_fetch_a_task(client):
    created = client.post("/tasks", json={"title": "Write tests"})
    assert created.status_code == 201
    assert created.headers["Location"] == "/tasks/1"

    task = client.get("/tasks/1").json()
    assert task == {"id": 1, "title": "Write tests", "done": False}


def test_list_tasks_filtered_by_done(make_client):
    repository = InMemoryTaskRepository()
    asyncio.run(repository.create("Open task"))
    closed = asyncio.run(repository.create("Closed task"))
    asyncio.run(repository.update(closed.id, UpdateTaskRequest(done=True)))
    client = make_client(repository)

    done_tasks = client.get("/tasks?done=true").json()

    assert [task["title"] for task in done_tasks] == ["Closed task"]


def test_patch_marks_a_task_as_done(make_client):
    repository = InMemoryTaskRepository()
    task = asyncio.run(repository.create("Ship it"))
    client = make_client(repository)

    response = client.patch(f"/tasks/{task.id}", json={"done": True})

    assert response.status_code == 200
    assert response.json()["done"] is True


def test_delete_removes_a_task(make_client):
    repository = InMemoryTaskRepository()
    task = asyncio.run(repository.create("Temporary"))
    client = make_client(repository)

    assert client.delete(f"/tasks/{task.id}").status_code == 204
    assert client.get(f"/tasks/{task.id}").status_code == 404


def test_blank_title_is_rejected(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 400
    assert response.json() == {"message": "title must not be blank"}


def test_unknown_task_returns_404(client):
    response = client.get("/tasks/42")

    assert response.status_code == 404
    assert response.json() == {"message": "Task 42 not found"}


def test_non_numeric_id_returns_400(client):
    assert client.get("/tasks/abc").status_code == 400
