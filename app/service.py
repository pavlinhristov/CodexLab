"""Manage task records through the JSON storage layer."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .store import load_tasks, next_task_id, save_tasks


def list_tasks(status: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    """Read task records matching the supplied status and search filters.

    Args:
        status: Status string to match, or None to include every status.
        q: Case-insensitive substring to find in the title or description,
            or None to omit text filtering. Whitespace is matched literally.

    Returns:
        A list of matching task dictionaries in storage order. Does not write
        to storage.

    Raises:
        OSError: If the task file cannot be read.
        json.JSONDecodeError: If the task file contains invalid JSON.
    """
    tasks = load_tasks()
    normalized_query = q.casefold() if q is not None else None
    filtered: list[dict[str, Any]] = []

    for task in tasks:
        if status and task["status"] != status:
            continue

        if normalized_query is not None and not (
            normalized_query in task["title"].casefold()
            or normalized_query in task["description"].casefold()
        ):
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
    """Mark a stored task as completed and save it before returning.

    Args:
        task_id: Integer identifier of the task to complete.

    Returns:
        The saved task dictionary, or None if the identifier is absent.
        Rewrites the collection with the selected task's status and current
        UTC completion timestamp; leaves unrelated records unchanged.

    Raises:
        OSError: If the task file cannot be read or written.
        json.JSONDecodeError: If the task file contains invalid JSON.
    """
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "done"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            save_tasks(tasks)
            return task

    return None
