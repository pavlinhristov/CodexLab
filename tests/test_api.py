"""Exercise task API behavior against isolated JSON storage."""

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, mock_open, patch

from fastapi.testclient import TestClient

from app import store
from app.main import app


class TaskApiTests(unittest.TestCase):
    """Verify public task responses without changing repository sample data."""

    def setUp(self) -> None:
        """Create per-test storage and a client with automatic cleanup.

        Returns:
            None. Registers cleanup for the client, data-path patch, and
            temporary directory, including when a test fails.
        """
        temporary_directory = self.enterContext(TemporaryDirectory())
        self.data_file = Path(temporary_directory) / "tasks.json"
        tasks = [
            {
                "id": task_id,
                "title": title,
                "description": description,
                "status": status,
                "priority": "medium",
                "created_at": "2026-02-20T14:30:00+00:00",
                "completed_at": (
                    "2026-02-21T09:15:00+00:00" if status == "done" else None
                ),
            }
            for task_id, status, title, description in (
                (1, "open", "Launch Checklist", "Prepare the release notes."),
                (2, "done", "Archive notes", "Review launch REPORT and STRASSE milestones."),
                (3, "open", "Plan workshop agenda", "Bring the Plan to the partner session."),
                (4, "open", "Straße inspection", "Verify the path."),
            )
        ]
        self.data_file.write_text(json.dumps(tasks), encoding="utf-8")
        self.enterContext(patch.object(store, "DATA_FILE", self.data_file))
        self.client = self.enterContext(TestClient(app))

    def test_list_without_status_returns_all_tasks_in_order(self) -> None:
        """Check that omitting status retains every task and its order.

        Returns:
            None.
        """
        response = self.client.get("/tasks")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([task["id"] for task in response.json()], [1, 2, 3, 4])

    def test_open_status_returns_only_open_tasks(self) -> None:
        """Catch discarded matches or completed tasks leaking into open results.

        Returns:
            None.
        """
        response = self.client.get("/tasks", params={"status": "open"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([task["id"] for task in response.json()], [1, 3, 4])
        self.assertEqual({task["status"] for task in response.json()}, {"open"})

    def test_done_status_returns_only_completed_tasks(self) -> None:
        """Catch discarded matches or open tasks leaking into done results.

        Returns:
            None.
        """
        response = self.client.get("/tasks", params={"status": "done"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([task["id"] for task in response.json()], [2])
        self.assertEqual({task["status"] for task in response.json()}, {"done"})

    def test_invalid_status_is_rejected(self) -> None:
        """Preserve query validation for unsupported status values.

        Returns:
            None.
        """
        response = self.client.get("/tasks", params={"status": "invalid"})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"][0]["loc"], ["query", "status"])

    def test_listing_does_not_modify_storage(self) -> None:
        """Catch accidental writes while listing or filtering stored tasks.

        Returns:
            None.
        """
        original_bytes = self.data_file.read_bytes()

        for params in (
            {},
            {"status": "open"},
            {"status": "done"},
            {"q": "launch"},
            {"status": "open", "q": "launch"},
        ):
            with self.subTest(params=params):
                response = self.client.get("/tasks", params=params)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(self.data_file.read_bytes(), original_bytes)

    def test_empty_store_returns_no_tasks(self) -> None:
        """Keep an empty collection valid with and without status filtering.

        Returns:
            None.
        """
        self.data_file.write_text("[]", encoding="utf-8")

        for params in (
            {},
            {"status": "open"},
            {"status": "done"},
            {"q": "launch"},
            {"status": "open", "q": "launch"},
        ):
            with self.subTest(params=params):
                response = self.client.get("/tasks", params=params)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), [])

    def test_search_matches_literal_substrings_in_either_field(self) -> None:
        """Verify title/description matching, case, order, and unique results.

        Returns:
            None.
        """
        cases = (
            ("checklist", [1]),
            ("milestones", [2]),
            ("LaUnCh", [1, 2]),
            ("AUnC", [1, 2]),
            ("plan", [3]),
            ("missing", []),
            (" launch ", [2]),
            (".*", []),
        )

        for query, expected_ids in cases:
            with self.subTest(query=query):
                response = self.client.get("/tasks", params={"q": query})

                self.assertEqual(response.status_code, 200)
                self.assertEqual([task["id"] for task in response.json()], expected_ids)

    def test_search_casefolds_unicode_query_and_fields(self) -> None:
        """Match both Unicode and ASCII forms in titles and descriptions.

        Returns:
            None.
        """
        for query in ("STRASSE", "straße"):
            with self.subTest(query=query):
                response = self.client.get("/tasks", params={"q": query})

                self.assertEqual(response.status_code, 200)
                self.assertEqual([task["id"] for task in response.json()], [2, 4])

    def test_search_and_status_must_both_match(self) -> None:
        """Reject records that match only one of the supplied filters.

        Returns:
            None.
        """
        cases = (
            ("open", "launch", [1]),
            ("done", "launch", [2]),
            ("done", "plan", []),
        )

        for status, query, expected_ids in cases:
            with self.subTest(status=status, query=query):
                response = self.client.get("/tasks", params={"status": status, "q": query})

                self.assertEqual(response.status_code, 200)
                self.assertEqual([task["id"] for task in response.json()], expected_ids)

    def test_empty_search_is_rejected(self) -> None:
        """Preserve the route's existing minimum search length.

        Returns:
            None.
        """
        response = self.client.get("/tasks", params={"q": ""})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"][0]["loc"], ["query", "q"])

    def test_completion_persists_status_and_timestamp(self) -> None:
        """Require completion to survive a new read from JSON storage.

        Returns:
            None.
        """
        started_at = datetime.now(timezone.utc)
        response = self.client.post("/tasks/1/complete")
        finished_at = datetime.now(timezone.utc)

        self.assertEqual(response.status_code, 200)
        completed = response.json()
        self.assertEqual(completed["status"], "done")
        self.assertIsNotNone(completed["completed_at"])
        completed_at = datetime.fromisoformat(completed["completed_at"])
        self.assertIsNotNone(completed_at.utcoffset())
        self.assertLessEqual(started_at, completed_at)
        self.assertLessEqual(completed_at, finished_at)

        stored = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(stored[0]["id"], 1)
        self.assertEqual(stored[0]["status"], "done")
        self.assertEqual(datetime.fromisoformat(stored[0]["completed_at"]), completed_at)
        fetched = self.client.get("/tasks/1")
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json(), completed)

    def test_completion_changes_only_the_selected_task(self) -> None:
        """Catch incorrect indexing, lost fields, and changes to other tasks.

        Returns:
            None.
        """
        original = json.loads(self.data_file.read_text(encoding="utf-8"))
        response = self.client.post("/tasks/3/complete")

        self.assertEqual(response.status_code, 200)
        stored = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual([task["id"] for task in stored], [1, 2, 3, 4])
        self.assertEqual(stored[2]["status"], "done")
        self.assertIsNotNone(stored[2]["completed_at"])
        expected = original[2] | {
            "status": "done",
            "completed_at": stored[2]["completed_at"],
        }
        self.assertEqual(stored[2], expected)
        self.assertEqual(stored[:2] + stored[3:], original[:2] + original[3:])

    def test_missing_task_completion_preserves_storage(self) -> None:
        """Keep missing-task completion a 404 with no storage changes.

        Returns:
            None.
        """
        original_bytes = self.data_file.read_bytes()
        response = self.client.post("/tasks/999/complete")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.data_file.read_bytes(), original_bytes)

    def test_completion_write_failure_returns_server_error(self) -> None:
        """Prevent a successful response when the storage write fails.

        Returns:
            None. Injects a failing file through the existing data-path seam.
        """
        original_bytes = self.data_file.read_bytes()
        failing_file = Mock(spec=Path)
        failing_file.exists.return_value = True
        failing_file.open = mock_open(read_data=original_bytes.decode("utf-8"))
        failing_file.open.return_value.write.side_effect = OSError("Storage write failed")

        with patch.object(store, "DATA_FILE", failing_file):
            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.post("/tasks/1/complete")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.data_file.read_bytes(), original_bytes)
