"""WebSocket tests: TestClient.websocket_connect talks to the app in-process."""

from app.tasks.task import Task
from app.tasks.task_event import TaskCreated, TaskDeleted, task_event_adapter


def receive_event(websocket):
    return task_event_adapter.validate_json(websocket.receive_text())


def test_text_frame_creates_a_task_and_is_broadcast_back(client):
    with client.websocket_connect("/ws/tasks") as websocket:
        websocket.send_text("Created via WebSocket")

        event = receive_event(websocket)

        assert event == TaskCreated(task=Task(id=1, title="Created via WebSocket"))


def test_rest_delete_is_pushed_to_websocket_clients(client):
    with client.websocket_connect("/ws/tasks") as websocket:
        # Creating a task first guarantees the socket is subscribed before we delete.
        websocket.send_text("Delete me")
        created = receive_event(websocket)

        client.delete(f"/tasks/{created.task.id}")

        assert receive_event(websocket) == TaskDeleted(id=created.task.id)
