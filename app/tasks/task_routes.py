"""
REST endpoints for tasks. Every change is published to the TaskEventBus:

  GET    /tasks            list all tasks (optional ?done=true|false)
  GET    /tasks/{id}       get one task
  POST   /tasks            create a task
  PATCH  /tasks/{id}       update title and/or done
  DELETE /tasks/{id}       delete a task
"""

from fastapi import APIRouter, HTTPException, Response, status

from app.tasks.dependencies import EventBusDep, RepositoryDep
from app.tasks.task import CreateTaskRequest, Task, UpdateTaskRequest
from app.tasks.task_event import TaskCreated, TaskDeleted, TaskUpdated

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")


@router.get("")
async def list_tasks(repository: RepositoryDep, done: bool | None = None) -> list[Task]:
    return await repository.find_all(done)


@router.get("/{task_id}")
async def get_task(task_id: int, repository: RepositoryDep) -> Task:
    task = await repository.find_by_id(task_id)
    if task is None:
        raise _not_found(task_id)
    return task


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest, response: Response, repository: RepositoryDep, event_bus: EventBusDep
) -> Task:
    task = await repository.create(request.title)
    await event_bus.publish(TaskCreated(task=task))
    response.headers["Location"] = f"/tasks/{task.id}"
    return task


@router.patch("/{task_id}")
async def update_task(
    task_id: int, request: UpdateTaskRequest, repository: RepositoryDep, event_bus: EventBusDep
) -> Task:
    task = await repository.update(task_id, request)
    if task is None:
        raise _not_found(task_id)
    await event_bus.publish(TaskUpdated(task=task))
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, repository: RepositoryDep, event_bus: EventBusDep) -> None:
    if not await repository.delete(task_id):
        raise _not_found(task_id)
    await event_bus.publish(TaskDeleted(id=task_id))
