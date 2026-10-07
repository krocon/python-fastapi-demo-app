"""
The application factory wires all plugins and routes together.
Dependencies are parameters so tests can pass in fresh instances.
"""

from fastapi import FastAPI

from app.plugins.monitoring import configure_monitoring
from app.plugins.routing import configure_routing
from app.plugins.serialization import PrettyJSONResponse
from app.plugins.status_pages import configure_status_pages
from app.tasks.in_memory_task_repository import InMemoryTaskRepository
from app.tasks.task_event_bus import TaskEventBus
from app.tasks.task_repository import TaskRepository


def create_app(
    task_repository: TaskRepository | None = None,
    event_bus: TaskEventBus | None = None,
) -> FastAPI:
    app = FastAPI(title="FastAPI Demo App", version="1.0.0", default_response_class=PrettyJSONResponse)

    # Shared objects live on app.state; routes get them via Depends (see tasks/dependencies.py).
    app.state.task_repository = task_repository or InMemoryTaskRepository.with_sample_data()
    app.state.event_bus = event_bus or TaskEventBus()

    configure_monitoring(app)
    configure_status_pages(app)
    configure_routing(app)
    return app


# The instance Uvicorn and `fastapi dev` pick up.
app = create_app()
