"""
Live endpoints:

  WS  /ws/tasks      two-way: receive all task events, send a text frame to create a task
  SSE /tasks/events  one-way: receive all task events as Server-Sent Events

FastAPI needs no extra plugin for either – WebSockets come from Starlette,
SSE from fastapi.sse (FastAPI >= 0.135).
"""

import asyncio
from collections.abc import AsyncIterable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.tasks.dependencies import EventBusDep, RepositoryDep
from app.tasks.task_event import TaskCreated

router = APIRouter(tags=["live"])


@router.websocket("/ws/tasks")
async def tasks_websocket(websocket: WebSocket, repository: RepositoryDep, event_bus: EventBusDep) -> None:
    await websocket.accept()

    with event_bus.subscribe() as events:
        # Server -> client: forward every task event as a JSON text frame.
        async def forward() -> None:
            async for event in events:
                await websocket.send_text(event.model_dump_json())

        forwarding = asyncio.create_task(forward())

        # Client -> server: every text frame becomes a new task.
        try:
            while True:
                title = (await websocket.receive_text()).strip()
                if title:
                    task = await repository.create(title)
                    await event_bus.publish(TaskCreated(task=task))
        except WebSocketDisconnect:
            pass
        finally:
            forwarding.cancel()


@router.get("/tasks/events", response_class=EventSourceResponse)
async def task_events(event_bus: EventBusDep) -> AsyncIterable[ServerSentEvent]:
    with event_bus.subscribe() as events:
        async for event in events:
            yield ServerSentEvent(data=event, event=event.type)
