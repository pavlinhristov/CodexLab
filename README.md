# CodexLab: Task Tracker Lab

A hands-on repository for OpenAI partners learning how to use Codex App for macOS or Codex Cloud on a realistic but compact backend project.

## Lab Overview

In this lab, you will use Codex to explore an unfamiliar codebase, diagnose bugs, implement a small feature, and commit your work to GitHub.

This is a Codex-first lab. Learners should accomplish each task by prompting Codex to inspect the repo, run commands, edit code, explain findings, and prepare Git changes. The learner's job is to direct Codex, review its diffs, and verify the results.

The application is a minimal task manager API built with FastAPI. It stores tasks in a local JSON file and exposes endpoints for listing, creating, and completing tasks.

Canonical repository for this lab: `https://github.com/pavlinhristov/CodexLab`

Estimated time: 30 to 45 minutes.

By the end of the lab, you will have practiced using Codex to:

- understand how a project is organized
- trace data flow across source files
- identify and fix application bugs
- implement a new feature
- commit working changes to a GitHub repository

## How To Work In This Lab

Use either Codex App for macOS or Codex Cloud for every step.

- Ask Codex to inspect the codebase before you make changes.
- Ask Codex to run the setup commands for you.
- Ask Codex to reproduce bugs and explain what it finds.
- Ask Codex to implement fixes and the new feature.
- Review Codex's diffs before accepting changes.
- Ask Codex to run verification commands after each change.
- Ask Codex to create your branch and prepare your commit.

Do not treat this as a manual coding exercise. The goal is to showcase how far you can get by directing Codex with clear prompts.

## Prerequisites

Make sure you have the following installed:

- Git
- Codex App for macOS or access to Codex Cloud
- Python 3.9 or newer

## Repository Structure

```text
CodexLab/
├── README.md
├── .gitignore
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── service.py
│   └── store.py
└── data/
    └── tasks.json
```

## Setup Instructions

### 0. Open the repository in Codex

Use one of the following:

- Codex App for macOS: open the cloned repository folder in the app
- Codex Cloud: open the repository in your cloud workspace

Recommended first prompt:

- `Set up this repository for development. Create a virtual environment, install the dependencies, and start the FastAPI app in a way that lets us keep testing it during the lab. Tell me what commands you ran and whether the server started successfully.`

### 1. Start from the canonical lab repository

All learners should start from:

- `https://github.com/pavlinhristov/CodexLab`

Recommended Git workflow for the lab:

1. Fork `pavlinhristov/CodexLab` to your own GitHub account if you want to push your finished work.
2. Clone your fork locally.
3. If you are only doing a local practice run, you can clone the canonical repo directly instead.

Clone your fork:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/CodexLab.git
cd CodexLab
```

Or clone the canonical repo directly:

```bash
git clone https://github.com/pavlinhristov/CodexLab.git
cd CodexLab
```

### 2. Ask Codex to create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Suggested Codex prompt:

- `Create the virtual environment for this project and activate it in the current shell session if possible.`

### 3. Ask Codex to install dependencies

```bash
pip install -r requirements.txt
```

Suggested Codex prompt:

- `Install this project's Python dependencies and let me know if anything fails.`

### 4. Ask Codex to run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

Suggested Codex prompt:

- `Start the FastAPI app and confirm the local URL I should use for testing.`

If you are using Codex Cloud, ask Codex to keep the server running in one session and use separate commands in the same workspace to test it. You do not need browser access for the lab to work.

## Lab Tasks

### Task 1: Understand the Codebase

Start by asking Codex to explain the repository before you change anything. Do not open files manually first unless you want to validate Codex's explanation after the fact.

Suggested prompts:

- `Explain what this repository does.`
- `Walk me through the key files in this project.`
- `Trace the data flow for GET /tasks from the API route to storage.`
- `Which file contains request validation, and which file contains business logic?`
- `Summarize this codebase as if I just joined the team and need to work on it in the next 10 minutes.`

As you inspect the project, make sure you can answer:

- What does the application do?
- What are the key files?
- How does a request move through the application?
- Where are tasks stored?

Expected mental model:

- `app/main.py` defines the HTTP API
- `app/schemas.py` defines request and response shapes
- `app/service.py` contains task-related business logic
- `app/store.py` reads and writes the JSON data file
- `data/tasks.json` contains the sample task data

What Codex should do for you in this task:

- inspect the repository structure
- read the important files
- explain how the app works in plain language
- point you to the exact files that matter for later fixes

### Task 2: Find and Fix Bugs

This repository includes two intentional bugs. Your job is to ask Codex to reproduce them, diagnose the root cause, implement fixes, and verify that the behavior is correct.

For each bug, use a prompt that asks Codex to do the full loop:

- reproduce the issue
- explain the likely cause
- make the code change
- show you the diff
- run verification commands after the fix

#### Bug A: Status filtering is broken

Ask Codex to run:

```bash
curl http://127.0.0.1:8000/tasks
curl "http://127.0.0.1:8000/tasks?status=open"
```

What you should notice:

- The first command returns all tasks
- The second command should return only open tasks
- In the starter code, the filtered result is incorrect

Suggested Codex prompts:

- `Reproduce the status filter bug on GET /tasks, explain why it happens, fix it, and verify the fix.`
- `The status filter on GET /tasks is not working. Find the bug, patch it, and show me the diff before I approve it.`

#### Bug B: Completing a task does not persist

Ask Codex to run:

```bash
curl -X POST http://127.0.0.1:8000/tasks/1/complete
curl http://127.0.0.1:8000/tasks/1
```

What you should notice:

- The completion endpoint appears to succeed
- The follow-up GET request should show task `1` as `done`
- In the starter code, the completed state is not saved correctly

Suggested Codex prompts:

- `Reproduce the complete-task persistence bug, diagnose the root cause, implement the fix, and verify that the task stays done afterward.`
- `Check whether POST /tasks/{task_id}/complete updates the stored data correctly. If not, fix it and rerun the API calls to prove it works.`

What Codex should do for you in this task:

- run the failing API calls
- inspect the relevant source files
- explain the bug in terms of code behavior
- edit the code
- rerun the API calls to confirm the fix

### Task 3: Add New Functionality

Add search support to the task list endpoint.

#### Feature to implement

Update `GET /tasks` so that the optional `q` query parameter filters tasks by:

- title
- description

Requirements:

- matching should be case-insensitive
- the search should return tasks where `q` appears anywhere in the title or description
- it should work together with the `status` filter
- if `q` is omitted, existing behavior should stay the same

Example desired behavior:

```bash
curl "http://127.0.0.1:8000/tasks?q=launch"
curl "http://127.0.0.1:8000/tasks?status=open&q=plan"
```

Suggested Codex prompts:

- `Implement the q search filter for GET /tasks, including case-insensitive matching across title and description, then verify it with curl requests.`
- `Propose the smallest clean implementation for the q filter, apply it, and test that it works with the status filter.`
- `Add case-insensitive search across title and description in the task service and show me the final diff.`

What Codex should do for you in this task:

- identify where the feature belongs
- implement the code change
- preserve existing behavior when `q` is omitted
- test search-only and combined search-plus-status behavior

### Task 4: Commit Your Changes

After your fixes and feature work are complete, have Codex prepare the Git workflow for you.

Before committing, ask Codex to check whether `data/tasks.json` changed only because you exercised the API during testing. If it did, restore that file so your final commit contains code and documentation changes, not runtime data churn.

Ask Codex to:

- create a new branch
- review whether `data/tasks.json` should be reverted
- show the changed files
- summarize the edits
- create a commit once you approve the diff

Commands Codex should run:

```bash
git checkout -b codex/lab-fixes
git status
git add .
git commit -m "Fix task bugs and add search filter"
git push origin codex/lab-fixes
```

If you forked the repository at the start of the lab, you can then open a pull request from your branch.

Suggested cleanup prompt before the commit:

- `Check whether data/tasks.json changed only because of runtime testing. If so, restore it before we commit.`

Suggested Codex prompts:

- `Create a new branch named codex/lab-fixes, review the diff, and suggest a concise commit message.`
- `Review my uncommitted changes, tell me if the bug fixes and search feature are complete, then commit them with a clear message.`
- `Prepare this repo for a pull request by summarizing the user-visible and code-level changes.`

## Verification

Use the commands below after you finish the lab, or ask Codex to run them and summarize the results.

Suggested verification prompt:

- `Run the verification steps for this lab and tell me whether the repository now behaves correctly.`

Note: the completion endpoint writes to `data/tasks.json` after you fix Bug B. That is expected during testing. Just make sure you ask Codex to review that file before the final commit.


### Run automated regression tests

From the repository root, use the virtual environment created during setup (verified with Python 3.14.4):

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

The suite covers status filtering, completion persistence, case-insensitive search, combined filters, and validation errors. Tests use temporary JSON files and leave `data/tasks.json` unchanged. A running server is not required.


### Verify the application still runs

```bash
uvicorn app.main:app --reload
```

### Verify Bug A is fixed

```bash
curl "http://127.0.0.1:8000/tasks?status=open"
curl "http://127.0.0.1:8000/tasks?status=done"
```

Expected result:

- `status=open` returns only open tasks
- `status=done` returns only completed tasks

### Verify Bug B is fixed

```bash
curl -X POST http://127.0.0.1:8000/tasks/3/complete
curl http://127.0.0.1:8000/tasks/3
```

Expected result:

- The second response shows `"status": "done"`
- The task also includes a non-null `completed_at`

### Verify the new feature works

```bash
curl "http://127.0.0.1:8000/tasks?q=launch"
curl "http://127.0.0.1:8000/tasks?q=report"
curl "http://127.0.0.1:8000/tasks?status=open&q=plan"
```

Expected result:

- each request returns only tasks whose title or description matches the query
- search remains case-insensitive
- combined filters behave correctly

If you are using Codex Cloud, you can use the same prompts. Codex should still inspect the repository, edit files, and run the verification commands in the workspace environment.

## Example Workflow in Codex

If you want a simple path through the lab, try this sequence:

1. Ask Codex to set up the repository and start the app.
2. Ask Codex to explain the repository structure.
3. Ask Codex to trace the `GET /tasks` request flow.
4. Ask Codex to reproduce Bug A, diagnose it, patch it, and verify the result.
5. Ask Codex to reproduce Bug B, diagnose it, patch it, and verify the result.
6. Ask Codex to implement the `q` search feature and test it with API calls.
7. Ask Codex to review the final diff and summarize the completed work.
8. Ask Codex to create a branch and commit the changes.

## Notes for Learners

- You do not need to understand every line of code before asking Codex for help.
- The goal of the lab is to practice directing Codex effectively while still validating the results yourself.
- Strong prompts are action-oriented: ask Codex to inspect, explain, fix, verify, and summarize.
- Treat Codex like an engineering teammate: delegate the work, then review the output carefully.
- The canonical starting point for the lab is `github.com/pavlinhristov/CodexLab`.
- Use the API docs at `http://127.0.0.1:8000/docs` if you prefer testing from a browser instead of `curl`.
