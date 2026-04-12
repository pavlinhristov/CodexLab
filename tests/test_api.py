from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import store
from app.main import app


@pytest.fixture(autouse=True)
def isolated_tasks_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run each test against a disposable copy of the task data file."""
    source = Path(__file__).resolve().parents[1] / "data" / "tasks.json"
    temp_data_file = tmp_path / "tasks.json"
    temp_data_file.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(store, "DATA_FILE", temp_data_file)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks_returns_seed_data(client: TestClient) -> None:
    response = client.get("/tasks")
    payload = response.json()

    assert response.status_code == 200
    assert isinstance(payload, list)
    assert len(payload) == 4
    assert [task["id"] for task in payload] == [1, 2, 3, 4]


def test_list_tasks_without_q_preserves_default_behavior(client: TestClient) -> None:
    default_response = client.get("/tasks")
    status_only_response = client.get("/tasks", params={"status": "open"})

    assert default_response.status_code == 200
    assert status_only_response.status_code == 200
    assert [task["id"] for task in default_response.json()] == [1, 2, 3, 4]
    assert [task["id"] for task in status_only_response.json()] == [1, 3, 4]


def test_list_tasks_filters_by_status(client: TestClient) -> None:
    response = client.get("/tasks", params={"status": "open"})
    payload = response.json()

    assert response.status_code == 200
    assert [task["id"] for task in payload] == [1, 3, 4]
    assert all(task["status"] == "open" for task in payload)


def test_list_tasks_search_filters_title_and_description_case_insensitive(
    client: TestClient,
) -> None:
    launch_response = client.get("/tasks", params={"q": "LAUNCH"})
    oauth_response = client.get("/tasks", params={"q": "oauth"})

    assert launch_response.status_code == 200
    assert [task["id"] for task in launch_response.json()] == [1]
    assert oauth_response.status_code == 200
    assert [task["id"] for task in oauth_response.json()] == [2]


def test_list_tasks_combines_status_and_search(client: TestClient) -> None:
    response = client.get("/tasks", params={"status": "open", "q": "plan"})

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [3]


def test_list_tasks_with_invalid_status_returns_422(client: TestClient) -> None:
    response = client.get("/tasks", params={"status": "invalid"})

    assert response.status_code == 422


def test_list_tasks_with_empty_query_returns_422(client: TestClient) -> None:
    response = client.get("/tasks", params={"q": ""})

    assert response.status_code == 422


def test_get_task_by_id_success(client: TestClient) -> None:
    response = client.get("/tasks/2")
    payload = response.json()

    assert response.status_code == 200
    assert payload["id"] == 2
    assert payload["title"] == "Fix login redirect"


def test_get_task_by_id_not_found(client: TestClient) -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_validation_error_for_short_title(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={"title": "hi", "description": "short title should fail", "priority": "low"},
    )

    assert response.status_code == 422
    assert any(
        detail.get("loc") == ["body", "title"]
        for detail in response.json().get("detail", [])
    )


def test_create_task_validation_error_for_invalid_priority(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "A valid title",
            "description": "Priority should fail validation.",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422
    assert any(
        detail.get("loc") == ["body", "priority"]
        for detail in response.json().get("detail", [])
    )


def test_create_task_success_persists_and_returns_created_task(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Document API tests",
            "description": "Add end-to-end endpoint coverage.",
            "priority": "medium",
        },
    )
    created = response.json()
    follow_up = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 201
    assert created["id"] == 5
    assert created["status"] == "open"
    assert created["priority"] == "medium"
    assert created["completed_at"] is None
    assert follow_up.status_code == 200
    assert follow_up.json()["title"] == "Document API tests"


def test_complete_task_persists_done_state(client: TestClient) -> None:
    complete_response = client.post("/tasks/1/complete")
    refreshed_response = client.get("/tasks/1")

    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "done"
    assert complete_response.json()["completed_at"] is not None

    assert refreshed_response.status_code == 200
    assert refreshed_response.json()["status"] == "done"
    assert refreshed_response.json()["completed_at"] is not None

    done_tasks = client.get("/tasks", params={"status": "done"})
    assert done_tasks.status_code == 200
    assert any(task["id"] == 1 for task in done_tasks.json())


def test_complete_task_not_found(client: TestClient) -> None:
    response = client.post("/tasks/999/complete")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
