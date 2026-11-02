from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from .schemas import Task, TaskCreate, TaskStatus
from .service import complete_task, create_task, get_task, list_tasks


app = FastAPI(
    title="Codex Task Tracker API",
    description="A small task manager API used for Codex App lab exercises.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def read_tasks(
    status: TaskStatus | None = Query(default=None),
    q: str | None = Query(
        default=None,
        description="Case-insensitive text search across title and description.",
    ),
) -> list[Task]:
    return list_tasks(status=status, q=q)


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int) -> Task:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", response_model=Task, status_code=201)
def add_task(payload: TaskCreate) -> Task:
    return create_task(payload.model_dump())


@app.post("/tasks/{task_id}/complete", response_model=Task)
def complete_existing_task(task_id: int) -> Task:
    task = complete_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
