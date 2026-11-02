import json
import tempfile
import unittest
from pathlib import Path

from app.service import list_tasks
from app.service import complete_task
from app import store


class ListTasksTests(unittest.TestCase):
    def test_status_filter_returns_only_matching_tasks(self) -> None:
        tasks = list_tasks(status="open")

        self.assertEqual([task["id"] for task in tasks], [1, 3, 4])
        self.assertTrue(all(task["status"] == "open" for task in tasks))


class CompleteTaskTests(unittest.TestCase):
    def test_completion_is_persisted(self) -> None:
        original_data_file = store.DATA_FILE
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "tasks.json"
            data_file.write_text(
                json.dumps(
                    [
                        {
                            "id": 1,
                            "title": "Write launch recap",
                            "description": "Draft a short internal summary.",
                            "status": "open",
                            "priority": "high",
                            "created_at": "2026-02-25T16:00:00+00:00",
                            "completed_at": None,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            store.DATA_FILE = data_file
            try:
                complete_task(1)
                persisted_task = store.load_tasks()[0]
            finally:
                store.DATA_FILE = original_data_file

        self.assertEqual(persisted_task["status"], "done")
        self.assertIsNotNone(persisted_task["completed_at"])


if __name__ == "__main__":
    unittest.main()
