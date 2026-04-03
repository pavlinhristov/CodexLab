from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .store import load_tasks, next_task_id, save_tasks


def list_tasks(status: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    """Return task records, optionally filtered by status and search text."""
    tasks = load_tasks()
    filtered: list[dict[str, Any]] = []
    query = q.lower() if q else None

    for task in tasks:
        if status and task["status"] != status:
            continue

        if query:
            title = task["title"].lower()
            description = task["description"].lower()
            if query not in title and query not in description:
                continue

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

    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            updated_task = dict(task)
            updated_task["status"] = "done"
            updated_task["completed_at"] = datetime.now(timezone.utc).isoformat()
            tasks[index] = updated_task
            save_tasks(tasks)
            return updated_task

    return None
