from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .store import load_tasks, next_task_id, save_tasks


def list_tasks(status: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    """Return task records, optionally filtered by status and search text."""
    tasks = load_tasks()
    filtered: list[dict[str, Any]] = []

    for task in tasks:
        # Instructor note: intentional bug for the lab.
        # This uses the literal string "status" instead of the query parameter value.
        if status and task["status"] != status:
            continue

        # Instructor note: partial feature for the lab.
        # The route already accepts `q`, but search is not implemented yet.
        filtered.append(task)

    return filtered


def get_task(task_id: int) -> dict[str, Any] | None:
    """Find a single task by ID."""
    tasks = load_tasks()
    return next((task for task in tasks if task["id"] == task_id), None)


def create_task(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a new task and persist it."""
    tasks = load_tasks()
    task = {
        "id": next_task_id(tasks),
        "title": payload["title"],
        "description": payload["description"],
        "status": "open",
        "priority": payload["priority"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def complete_task(task_id: int) -> dict[str, Any] | None:
    """Mark a task as completed."""
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            updated_task = dict(task)
            updated_task["status"] = "done"
            updated_task["completed_at"] = datetime.now(timezone.utc).isoformat()

            # Instructor note: intentional bug for the lab.
            # The updated task is returned, but the stored list is never updated or saved.
            return updated_task

    return None
